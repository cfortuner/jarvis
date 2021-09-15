from datasets import load_dataset

from elasticsearch import Elasticsearch, helpers

# Connect to ES instance
es = Elasticsearch(hosts=["http://localhost:9200"], timeout=60, retry_on_timeout=True)

def create_db():
    # Load HF dataset
    dataset = load_dataset("ag_news", split="train")["text"][:50000]

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

    print("Total articles inserted: {}".format(rows))


# from IPython.display import display, HTML
from bs4 import BeautifulSoup

def parse_html(html):
    elem = BeautifulSoup(html, features="html.parser")
    text = ''
    for e in elem.descendants:
        if isinstance(e, str):
            text += e.strip()
        elif e.name in ['br',  'p', 'h1', 'h2', 'h3', 'h4','tr', 'th']:
            text += '\n'
        elif e.name == 'li':
            text += '\n- '
    return text


def table(category, query, rows):
    print(category, query)
    for score, text in rows:
        print(score, text)


def search(query, limit):
  query = {
      "size": limit,
      "query": {
          "query_string": {"query": query}
      }
  }

  results = []
  for result in es.search(index="articles", body=query)["hits"]["hits"]:
    source = result["_source"]
    results.append((min(result["_score"], 18) / 18, source["title"]))

  return results

limit = 3
query= "+yankees lose"
table("Elasticsearch", query, search(query, limit))


from txtai.pipeline import Similarity

def ranksearch(query, limit):
  results = [text for _, text in search(query, limit * 10)]
  return [(score, results[x]) for x, score in similarity(query, results)][:limit]

# Create similarity instance for re-ranking
similarity = Similarity("valhalla/distilbart-mnli-12-3")
print("Ranking similarity-----")
table("Elasticsearch + txtai", query, ranksearch(query, limit))


for query in ["good news +economy", "bad news +economy"]:
  table("Elasticsearch", query, search(query, limit))
  table("Elasticsearch + txtai", query, ranksearch(query, limit))