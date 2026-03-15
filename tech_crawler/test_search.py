import json
import faiss
import numpy as np
from  sentence_transformers import SentenceTransformer

index=faiss.read_index("tech_bge.index")

with open("tech_bge_meta.json","r",encoding="utf-8")as f:
    metadata=json.load(f)

model=SentenceTransformer('BAAI/bge-m3')

querry=input("Enter your querry:") 

querry_vector=model.encode([querry],normalize_embeddings=True)

D,I=index.search(np.array(querry_vector),10)

print("Top 5 results:")
for rank, idx in enumerate(I[0]):
    item=metadata[idx]
    print(f"Rank {rank+1}:")
    print(f"URL: {item['url']}")
    print(f"Title: {item['title']}")
    print(f"Description: {item['description']}")
    print(f"Chunk: {item['chunk'][:200]}...")
    print("-"*50)