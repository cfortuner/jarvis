import sqlite3

import regex as re

from elasticsearch import Elasticsearch, helpers

# Connect to ES instance
es = Elasticsearch(hosts=["http://localhost:9200"], timeout=60, retry_on_timeout=True)

# Connection to database file
db = sqlite3.connect("articles.sqlite")
cur = db.cursor()

# Elasticsearch bulk buffer
buffer = []
rows = 0

# Select tagged sentences without a NLP label. NLP labels are set for non-informative sentences.
cur.execute(
    "SELECT s.Id, Article, Title, Published, Reference, Name, Text FROM sections s JOIN articles a on s.article=a.id WHERE (s.labels is null or s.labels NOT IN ('FRAGMENT', 'QUESTION')) AND s.tags is not null"
)
for row in cur:
    # Build dict of name-value pairs for fields
    article = dict(
        zip(("id", "article", "title", "published", "reference", "name", "text"), row)
    )
    name = article["name"]

    # Only process certain document sections
    if not name or not re.search(
        r"background|(?<!.*?results.*?)discussion|introduction|reference", name.lower()
    ):
        # Bulk action fields
        article["_id"] = article["id"]
        article["_index"] = "articles"
    print(article)
    break
