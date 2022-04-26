import numpy as np
import json
import faiss
dim = 5
embeddings = np.eye(dim)

schema = {
    "id_col": "id",
    "metric": "l2",
    "filters":[{"field": "country", "values": ["EU", "US"]}],
    "encoders":[{"field": "state",  "values": ["a", "b", "c", "d", "e"], "type":"np", "weight":1, "npy": "state.npy"}],
    "sources":[{"record": "items", "type": "csv", "path": "test.csv"}],
}
index_labels = ["eu1", "eu2", "us3", "us5"]

index_us = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))
index_eu = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))
def add_items(index, data, labels):
    data = np.array(data).astype(np.float32)
    ids = [index_labels.index(l) for l in labels]
    index.add_with_ids(data, np.array(ids, dtype='int64'))

add_items(index_eu, np.array([[1,0,0,0,0],[0,1,0,0,0]]), ["eu1","eu2"])
add_items(index_us, np.array([[0,0,0,0,1],[0,0,0,1,0]]), ["us5","us3"])

# -------------Write-------------
np.save('state.npy', embeddings)
with open("schema.json", "w") as f:
    json.dump(schema, f, indent=4)
with open("index_labels.json", "w") as f:
    json.dump(index_labels, f)
with open("test.csv", 'w') as f:
    f.write("id,country,state\n")
    f.write("us1,US,a\n")
    f.write("us1,US,b\n")
    f.write("eu1,US,c\n")
    f.write("eu2,EU,d\n")
    f.write("us3,US,e\n")


faiss.write_index(index_eu, "0")
faiss.write_index(index_us, "1")