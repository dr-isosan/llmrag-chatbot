# embedder_docs.py
"""
Sadece data.json'u embedleyip embedded_data.json olarak kaydeder.
"""
import json
import os
from embedder import MultiModelEmbedder
from config import config

def main():
    INPUT_JSON = "data.json"
    OUTPUT_JSON = "embedded_data.json"
    if not os.path.exists(INPUT_JSON):
        print(f"[embedder_docs] {INPUT_JSON} yok.")
        return
    
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    embedder = MultiModelEmbedder(primary_model=config.EMBEDDING_MODEL)
    
    for item in data:
        chunks = item.get("chunks", [])
        if chunks:
            # Her chunk için embedding hesapla
            embeddings = []
            for chunk in chunks:
                embedding = embedder.embed_single(chunk)
                embeddings.append(embedding.tolist())
            item["embeddings"] = embeddings
        else:
            item["embeddings"] = []
    
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[embedder_docs] {OUTPUT_JSON} kaydedildi. {len(data)} dosya embedlendi.")

if __name__ == "__main__":
    main()
