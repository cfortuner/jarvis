from txtai.embeddings import Embeddings

# Create embeddings model, backed by sentence-transformers & transformers
embeddings = Embeddings({"path": "sentence-transformers/nli-mpnet-base-v2"})

data = [
    "US tops 5 million confirmed virus cases",
    "Canada's last fully intact ice shelf has suddenly collapsed, forming a Manhattan-sized iceberg",
    "Beijing mobilises invasion craft along coast as Taiwan tensions escalate",
    "The National Park Service warns against sacrificing slower friends in a bear attack",
    "Maine man wins $1M from $25 lottery ticket",
    "Make huge profits without work, earn up to $100,000 a day",
]

print("%-20s %s" % ("Query", "Best Match"))
print("-" * 50)

for query in (
    "feel good story",
    "climate change",
    "public health story",
    "war",
    "wildlife",
    "asia",
    "lucky",
    "dishonest junk",
):
    # Get index of best section that best matches query
    uid = embeddings.similarity(query, data)[0][0]

    print("%-20s %s" % (query, data[uid]))

# Create an index for the list of text
embeddings.index([(uid, text, None) for uid, text in enumerate(data)])

print("%-20s %s" % ("Query", "Best Match"))
print("-" * 50)

# Run an embeddings search for each query
for query in (
    "feel good story",
    "climate change",
    "public health story",
    "war",
    "wildlife",
    "asia",
    "lucky",
    "dishonest junk",
):
    # Extract uid of first result
    # search result format: (uid, score)
    uid = embeddings.search(query, 1)[0][0]

    # Print text
    print("%-20s %s" % (query, data[uid]))


embeddings.save("index")

embeddings = Embeddings()
embeddings.load("index")

uid = embeddings.search("climate change", 1)[0][0]
print(data[uid])

# Run initial query
uid = embeddings.search("feel good story", 1)[0][0]
print("Initial: ", data[uid])

# Update data
data[0] = "See it: baby panda born"
embeddings.upsert([(0, data[0], None)])

uid = embeddings.search("feel good story", 1)[0][0]
print("After update: ", data[uid])

# Remove record just added from index
embeddings.delete([0])

# Ensure value matches previous value
uid = embeddings.search("feel good story", 1)[0][0]
print("After delete: ", data[uid])
