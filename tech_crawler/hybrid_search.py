import json
import faiss
import numpy as np
import re
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import pickle



def tokenize(text):
    text=text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text.split()

import os

current_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(current_dir, 'bm25_index.pkl'), 'rb') as f:
    bm25_bundle=pickle.load(f)

bm25:BM25Okapi=bm25_bundle['bm25']
bm25_data=bm25_bundle['data']

faiss_index=faiss.read_index(os.path.join(current_dir, "tech_bge.index"))
with open(os.path.join(current_dir, "tech_bge_meta.json"), "r", encoding="utf-8") as f:
    faiss_metadata=json.load(f)

model=SentenceTransformer('BAAI/bge-m3')


def exact_url_match(query, k=5):
    matches = []
    q = query.lower().strip()

    for idx, item in enumerate(faiss_metadata):  
        url = item.get("url", "").lower()
        if q in url:   
            matches.append({
                "score": 1.0,
                "idx": idx,
                "source": "exact_url",
                "title": item.get("title"),
                "company": item.get("company"),
                "url": item.get("url"),
                "snippet": item.get("chunk", "")[:300]
            })

    return matches[:k]




def bm25_search(query,k=10):
    tokens=tokenize(query)
    scores=bm25.get_scores(tokens)
    indices=np.argsort(scores)[::-1][:k]
    results=[]
    for idx in indices:
        item=bm25_data[int(idx)]
        results.append(
            {
                "score": float(scores[int(idx)]),
                "idx": int(idx),
                "source": "bm25",
                "title": item.get("title"),
                "company": item.get("company"),
                "url": item.get("url"),
                "snippet": item.get("chunk")[:300],
            }
        )
    return results


def vector_search(query,k=10):
    q_vec=model.encode([query],normalize_embeddings=True)
    D,I=faiss_index.search(np.array(q_vec),k)
    results=[]
    for score, idx in zip(D[0], I[0]):
        item=faiss_metadata[int(idx)]
        results.append(
            {
                "score": float(score),
                "idx": int(idx),
                "source": "Vector",
                "title": item.get("title"),
                "company": item.get("company"),
                "url": item.get("url"),
                "snippet": item.get("chunk")[:300],
            }
        )
    return results



def rrf_fusion(bm25_results, vector_results, k=10, k_rrf=60):
    rank_map = {}
    metadata_by_url = {item["url"]: item for item in faiss_metadata}

    for rank, item in enumerate(bm25_results):
        url = item["url"]
        score = 1.0 / (k_rrf + rank + 1)
        rank_map.setdefault(url, 0.0)
        rank_map[url] += score

    for rank, item in enumerate(vector_results):
        url = item["url"]
        score = 1.0 / (k_rrf + rank + 1)
        rank_map.setdefault(url, 0.0)
        rank_map[url] += score

    stored_results = sorted(rank_map.items(), key=lambda x: x[1], reverse=True)[:k]

    results = []

    for url, fused_score in stored_results:
        item = metadata_by_url.get(url)
        results.append(
            {
                "fused_score": float(fused_score),
                "title": item.get("title"),
                "company": item.get("company"),
                "url": item.get("url"),
                "snippet": item.get("chunk")[:300],
            }
        )

    return results



def search(query, mode="hybrid", k=10):

    url_hits=exact_url_match(query)
    if url_hits:
        return url_hits[:k]

    if mode == "bm25":
        return bm25_search(query, k=k)
    if mode == "vector":
        return vector_search(query, k=k)
    bm25_res = bm25_search(query, k=k)
    vec_res = vector_search(query, k=k)
    return rrf_fusion(bm25_res, vec_res, k=k)



if __name__ == "__main__":
    z=1
    while(z!=0): 
        q = input("Query: ")
        mode = input("Mode (bm25/vector/hybrid): ").strip()
        print(f'searching for {q} in {mode} mode')
        results = search(q, mode=mode, k=5)

        for i, r in enumerate(results, start=1):
            print("Rank:", i)
            if "fused_score" in r:
                print("RRF Score:", np.round(r["fused_score"], 4))
            elif "score" in r:
                print("Score:", np.round(r["score"], 4))
            print("Title:", r.get("title"))
            print("Company:", r.get("company"))
            print("URL:", r.get("url"))
            print("Snippet:", r.get("snippet"))
            print("-" * 60)

        z=int(input("Do you want to continue? (1 for yes / 0 for no): "))
