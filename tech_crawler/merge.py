import json

with open("official_data.json","r", encoding="utf-8") as f:
    official_data = json.load(f)
                              

with open("official_datav2.json","r", encoding="utf-8") as f:
    official_data_v2 = json.load(f)

with open("official_datav3.json","r", encoding="utf-8") as f:
    official_data_v3 = json.load(f)

with open("wiki_data.json","r", encoding="utf-8") as f:
    wiki_data = json.load(f)


merged = official_data + official_data_v2 + official_data_v3 + wiki_data


seen = set()
unique = []
for item in merged:
    if item["url"] not in seen:
        seen.add(item["url"])
        unique.append(item)

print(f"Total merged: {len(unique)}")

with open("merged_data.json", "w", encoding="utf-8") as f:
    json.dump(unique, f, indent=2, ensure_ascii=False)