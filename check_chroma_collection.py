import os
from chroma import ChromaDBManager

def check_chroma_collection():
    chroma_path = "./chroma"
    collection_name = "rag_documents"
    print("ChromaDB koleksiyon kontrolü başlatılıyor...")
    try:
        chroma_manager = ChromaDBManager(chroma_path, collection_name)
        info = chroma_manager.get_collection_info()
        print("--- ChromaDB Koleksiyon Bilgisi ---")
        for k, v in info.items():
            print(f"{k}: {v}")
        # Embedding boyutunu kontrol et
        if info.get("total_chunks", 0) > 0:
            sample = chroma_manager.collection.get(limit=1, include=["embeddings"])
            emb = sample["embeddings"][0]
            if hasattr(emb, "shape"):
                print(f"Örnek embedding shape: {emb.shape}")
            elif isinstance(emb, (list, tuple)):
                print(f"Örnek embedding boyutu: {len(emb)}")
            else:
                print(f"Embedding tipi: {type(emb)}")
        else:
            print("Koleksiyonda hiç chunk yok!")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    check_chroma_collection()
