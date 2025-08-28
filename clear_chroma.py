import shutil
import os
from config import config

def clear_chroma():
    chroma_dir = os.path.join(os.getcwd(), "chroma")
    if os.path.exists(chroma_dir):
        shutil.rmtree(chroma_dir)
        print("ChromaDB dizini ve tüm veriler silindi.")
        print(f"Yeni collection {config.EMBEDDING_MODEL} ({config.EMBEDDING_DIMENSION} dim) için hazır.")
    else:
        print("ChromaDB dizini zaten yok.")
        print(f"Yeni collection {config.EMBEDDING_MODEL} ({config.EMBEDDING_DIMENSION} dim) için hazır.")

if __name__ == "__main__":
    clear_chroma()
