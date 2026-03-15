import json
import pickle
import re
from rank_bm25 import BM25Okapi

def tokenize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text.split()

with open("cleaned_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

corpus=[tokenize(item["chunk"].lower()) for item in data]

bm25=BM25Okapi(corpus)

with open("bm25_index.pkl", "wb") as f:
    pickle.dump({"bm25": bm25, "data": data}, f)

print("BM25 index built")
print("Total documents:", len(corpus))