import json
import re
from hashlib import md5


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    return text.strip()


def chunk_text(text, size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


with open("merged_data.json", "r", encoding="utf-8") as f:
    all_data = json.load(f)


seen_hashes = set()
final_chunks = []

for item in all_data:
    raw_content = item.get("content")

    if not raw_content:
        continue

    content = clean_text(raw_content)

    if len(content) < 200:
        continue

    content_hash = md5(content.encode("utf-8")).hexdigest()

    if content_hash in seen_hashes:
        continue

    seen_hashes.add(content_hash)

    chunks = chunk_text(content)

    for chunk in chunks:
        final_chunks.append({
            "url": item.get("url", ""),
            "domain": item.get("domain", ""),
            "company": item.get("company", ""),
            "title": item.get("title", ""),
            "description": item.get("description", ""),
            "chunk": chunk
        })


with open("cleaned_data.json", "w", encoding="utf-8") as f:
    json.dump(final_chunks, f, ensure_ascii=False, indent=2)

print("Total final chunks:", len(final_chunks))
