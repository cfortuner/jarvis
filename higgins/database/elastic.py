"""Elasticsearch database utils.

References
-----------
https://www.elastic.co/guide/en/elasticsearch/reference/7.14/index.html
https://opendistro.github.io/for-elasticsearch-docs/docs/elasticsearch/aggregations/
https://github.com/oliver006/elasticsearch-gmail

Query DSL:
https://github.com/elastic/elasticsearch-dsl-py

Text analysis and full-text search
https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis.html

"""

from elasticsearch import Elasticsearch
client = Elasticsearch()

response = client.search(
    index="gmail",
    body={
      "query": {
        "bool": {
          "must": [{"match": {"title": "python"}}],
          "must_not": [{"match": {"description": "beta"}}],
          "filter": [{"term": {"category": "search"}}]
        }
      },
      "aggs" : {
        "per_tag": {
          "terms": {"field": "tags"},
          "aggs": {
            "max_lines": {"max": {"field": "lines"}}
          }
        }
      }
    }
)

for hit in response['hits']['hits']:
    print(hit['_score'], hit['_source']['title'])

for tag in response['aggregations']['per_tag']['buckets']:
    print(tag['key'], tag['max_lines']['value'])
