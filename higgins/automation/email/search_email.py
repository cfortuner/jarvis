from typing import Dict, List

from elasticsearch import Elasticsearch
from elasticsearch import helpers
import elasticsearch_dsl
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch
import pandas as pd
from txtai.pipeline import Similarity


EMAIL_INDEX = "email"
QUERY_LIMIT = 1000
SIMILARITY_BATCH_SIZE = 100


def bulk_load_docs():
    # Connect to ES instance
    es = Elasticsearch(
        hosts=["http://localhost:9200"], timeout=60, retry_on_timeout=True
    )

    dataset = []
    # Elasticsearch bulk buffer
    buffer = []
    rows = 0

    for x, text in enumerate(dataset):
        # Article record
        article = {"_id": x, "_index": "articles", "title": text}

        # Buffer article
        buffer.append(article)

        # Increment number of articles processed
        rows += 1

        # Bulk load every 1000 records
        if rows % 1000 == 0:
            helpers.bulk(es, buffer)
            buffer = []

            print("Inserted {} articles".format(rows), end="\r")

    if buffer:
        helpers.bulk(es, buffer)


def get_all(query: Dict):
    client = Elasticsearch()
    s = Search(using=client, index="email")
    resp = s.execute()
    print(f"Hits: {resp.hits.total.value}")


def get_by_id(id_: str, client: Elasticsearch):
    resp = client.get(index=EMAIL_INDEX, id=id_)
    print(type(resp))
    return resp


def search_query_string(
    query_str: str,
    fields: List,
    client: Elasticsearch,
    start: int = 0,
    stop: int = QUERY_LIMIT,
) -> List[elasticsearch_dsl.response.hit.Hit]:
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html
    # https://www.elastic.co/guide/en/elasticsearch//reference/current/query-dsl-multi-match-query.html
    query = MultiMatch(query=query_str, fields=fields, type="best_fields")
    s = Search(using=client, index=EMAIL_INDEX)
    s = s.query(query)
    s = s[start:stop]  # pagination/limit
    hits = s.execute()
    return hits


def dsl_hit_to_dict(hit: List[elasticsearch_dsl.response.hit.Hit]) -> Dict:
    """Convert Elasticsearc-DSL Hit objects to normal ES result dicts."""
    return {
        "_id": hit.meta.id,
        "_index": hit.meta.index,
        "_type": "_doc",  # not sure if this exists
        "_score": hit.meta.score,
        "_source": hit.to_dict(),
    }


def results_to_df(results: List[Dict], fields: List[str] = None):
    rows = []
    for result in results:
        doc = {
            "_id": result["_id"],
            "_score": min(result["_score"], 18) / 18,
        }
        doc.update(
            {
                k: v
                for k, v in result["_source"].items()
                if fields is None or k in fields
            }
        )
        rows.append(doc)
    df = pd.DataFrame(rows)
    return df


def search_subjects(query: str, client: Elasticsearch, limit: int = QUERY_LIMIT):
    query = {"size": limit, "query": {"query_string": {"query": query}}}

    results = []
    for result in client.search(index=EMAIL_INDEX, body=query)["hits"]["hits"]:
        source = result["_source"]
        results.append((min(result["_score"], 18) / 18, source["subject"]))

    return results


def dict_to_table(dct, columns=None):
    df = pd.DataFrame(data=dct, columns=columns)
    return df


def semantic_search(query: str, strings: List[str], engine: Similarity):
    return [(score, strings[x]) for x, score in engine(query, strings)]


if __name__ == "__main__":
    # search_elastic_emails({})
    es = Elasticsearch(
        hosts=["http://localhost:9200"], timeout=60, retry_on_timeout=True
    )

    # query = "+Slack"
    # results = search_subjects(query, client=es, limit=10)
    # print(results)
    similarity = Similarity("valhalla/distilbart-mnli-12-3")

    # email = get_by_id(id_=df.iloc[0]["_id"], client=es)
    # print(email)
    query_field = "subject"
    # queries = ["+job opportunity"]  # + means include/contains? - means exclude
    queries = ["+recruiter email"]  # + means include/contains? - means exclude
    for query in queries:
        hits = search_query_string(query, fields=[query_field], client=es)
        print(f"Found {len(hits)} results.")
        results = [dsl_hit_to_dict(hit) for hit in hits]
        df = results_to_df(results, fields=["subject", "sender_address", "date"])
        with pd.option_context("display.max_colwidth", -1):
            print(df.head(20))
        # Create similarity instance for re-ranking
        rankings = []
        for i in range(0, len(results), SIMILARITY_BATCH_SIZE):
            strings = [
                r["_source"][query_field]
                for r in results[i : i + SIMILARITY_BATCH_SIZE]
            ]
            rankings += semantic_search(query, strings, similarity)
            print(f"Processed {len(rankings)} rows")
        df = pd.DataFrame(data=rankings, columns=["score", query_field])
        df = df.sort_values(by="score", ascending=False, inplace=False)
        # with pd.option_context("display.max_colwidth", -1):
        print(df.head(20))
