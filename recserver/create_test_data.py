import numpy as np
import json
import faiss
dim = 5
embeddings = np.eye(dim)

schema = {
    "filters":[{"field": "country", "values": ["US", "EU"]}],
    "encoders":[{"field": "state",  "values": ["a", "b", "c", "d", "e"], "type":"np", "weight":1, "npy": "state.npy"}]
}
index_labels = ["1", "2", "3", "5"]

index_us = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))
index_eu = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))
def add_items(index, data, ids):
    data = np.array(data).astype(np.float32)
    index.add_with_ids(data, np.array(ids, dtype='int64'))

add_items(index_eu, np.array([[1,0,0,0,0],[0,1,0,0,0]]), ["1","2"])
add_items(index_us, np.array([[0,0,0,0,1],[0,0,0,1,0]]), ["5","3"])

# -------------Write-------------
np.save('state.npy', embeddings)
with open("schema.json", "w") as f:
    json.dump(schema, f)
with open("index_labels.json", "w") as f:
    json.dump(index_labels, f)

faiss.write_index(index_eu, "0")
faiss.write_index(index_us, "1")