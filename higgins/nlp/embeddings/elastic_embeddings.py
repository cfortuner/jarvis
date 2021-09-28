"""
This script contains an example how to perform semantic search with ElasticSearch.

As dataset, we use the Quora Duplicate Questions dataset, which contains about 500k questions:
https://www.quora.com/q/quoradata/First-Quora-Dataset-Release-Question-Pairs

Questions are indexed to ElasticSearch together with their respective sentence
embeddings.

The script shows results from BM25 as well as from semantic search with
cosine similarity.

You need ElasticSearch (https://www.elastic.co/de/elasticsearch/) up and running. Further, you need the Python
ElasticSearch Client installed: https://elasticsearch-py.readthedocs.io/en/master/

As embeddings model, we use the SBERT model 'quora-distilbert-multilingual',
that it aligned for 100 languages. I.e., you can type in a question in various languages and it will
return the closest questions in the corpus (questions in the corpus are mainly in English).
"""

import csv
import os
from typing import Dict, List

from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer, util
import time
import tqdm.autonotebook


es = Elasticsearch()


def create_vector_index(
    index: str, text_field: str, vector_field: str, vector_dims: int
):
    if not es.indices.exists(index=index):
        es_index = {
            "mappings": {
                "properties": {
                    text_field: {"type": "text"},
                    vector_field: {"type": "dense_vector", "dims": vector_dims},
                }
            }
        }
        es.indices.create(index=index, body=es_index, ignore=[400])
    else:
        print(f"Index {index} already exists!")


def create_and_upload_embeddings(
    model: SentenceTransformer,
    rows: List[Dict],
    index: str,
    text_field: str,
    vector_field: str,
    chunk_size: int = 500,
):
    with tqdm.tqdm(total=len(rows)) as pbar:
        for start_idx in range(0, len(rows), chunk_size):
            row_slice = rows[start_idx : start_idx + chunk_size]
            embeddings = model.encode(
                sentences=[row[text_field] for row in row_slice],
                show_progress_bar=False,
            )
            bulk_data = []
            for row, embedding in zip(row_slice, embeddings):
                row[vector_field] = embedding
                row_id = row["_id"]
                del row["_id"]
                document = {
                    "_index": index,
                    "_id": row_id,
                    "_source": row,
                }
                bulk_data.append(document)

            helpers.bulk(es, bulk_data)
            pbar.update(chunk_size)


def init_query_session(model, index, text_field, vector_field):
    """Open interactive query session"""
    while True:
        inp_question = input("Please enter a question: ")

        encode_start_time = time.time()
        question_embedding = model.encode(inp_question)
        encode_end_time = time.time()

        # Lexical search
        bm25 = es.search(
            index=index, body={"query": {"match": {f"{text_field}": inp_question}}}
        )

        # Sematic search
        sem_search = es.search(
            index=index,
            body={
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": f"cosineSimilarity(params.queryVector, doc['{vector_field}']) + 1.0",
                            "params": {"queryVector": question_embedding},
                        },
                    }
                }
            },
        )

        print("Input question:", inp_question)
        print(
            "Computing the embedding took {:.3f} seconds, BM25 search took {:.3f} seconds, semantic search with ES took {:.3f} seconds".format(
                encode_end_time - encode_start_time,
                bm25["took"] / 1000,
                sem_search["took"] / 1000,
            )
        )

        print("BM25 results:")
        for hit in bm25["hits"]["hits"][0:5]:
            print("\t{}".format(hit["_source"][text_field]))

        print("\nSemantic Search results:")
        for hit in sem_search["hits"]["hits"][0:5]:
            print("\t{}".format(hit["_source"][text_field]))

        print("\n\n========\n")


def prepare_quora_dataset(max_corpus_size: int = 100000):
    url = "http://qim.fs.quoracdn.net/quora_duplicate_questions.tsv"
    dataset_path = "quora_duplicate_questions.tsv"

    # Download dataset if needed
    if not os.path.exists(dataset_path):
        print("Download dataset")
        util.http_get(url, dataset_path)

    # Get all unique sentences from the file
    all_questions = {}
    with open(dataset_path, encoding="utf8") as fIn:
        reader = csv.DictReader(fIn, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_questions[row["qid1"]] = row["question1"]
            if len(all_questions) >= max_corpus_size:
                break

            all_questions[row["qid2"]] = row["question2"]
            if len(all_questions) >= max_corpus_size:
                break

    qids = list(all_questions.keys())
    questions = [
        {
            "_id": qid,
            "question": all_questions[qid],
        }
        for qid in qids
    ]
    return questions


def create_quora_embeddings_index(model):
    index = "quora"
    text_field = "question"
    vector_field = text_field + "_vector"
    corpus_size = 100000
    questions = prepare_quora_dataset(corpus_size)
    create_vector_index(index, text_field, vector_field, 768)
    create_and_upload_embeddings(model, questions, index, text_field, vector_field)


if __name__ == "__main__":
    model = SentenceTransformer("quora-distilbert-multilingual")
    vector_field = "question_vector"

    # create_quora_embeddings_index(model)

    init_query_session(
        model, index="quora", text_field="question", vector_field="question_vector"
    )
