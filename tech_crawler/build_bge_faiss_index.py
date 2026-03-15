import json
import faiss
import numpy as np
from  sentence_transformers import SentenceTransformer

with open("cleaned_data.json","r",encoding="utf-8")as f:
    data=json.load(f)


model=SentenceTransformer('BAAI/bge-m3')

texts = [item["chunk"] for item in data]

embeddings=model.encode(texts,show_progress_bar=True, normalize_embeddings=True)


dimension=embeddings.shape[1]
index=faiss.IndexFlatIP(dimension)

index.add(np.array(embeddings))


faiss.write_index(index,"tech_bge.index")

with open("tech_bge_meta.json","w",encoding="utf-8")as f:
    json.dump(data,f,ensure_ascii=False,indent=2)

print("BGE-M3 FAISS index created")
print("Total vectors:", index.ntotal)
print("Vector dimension:", dimension)