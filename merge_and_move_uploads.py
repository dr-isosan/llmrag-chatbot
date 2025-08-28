import os
import json
import shutil

# Dosya yolları
def merge_and_move_uploads():
    BASE_JSON = "uploads_base.json"
    EMBED_JSON = "uploads_with_embed.json"
    ALL_BASE_JSON = "enhanced_document_data.json"
    ALL_EMBED_JSON = "enhanced_document_data_with_embeddings.json"
    UPLOADS_DIR = "uploads"
    DOCS_DIR = "docs"

    # 1. uploads klasöründeki dosyaları docs klasörüne taşı
    os.makedirs(DOCS_DIR, exist_ok=True)
    for filename in os.listdir(UPLOADS_DIR):
        src = os.path.join(UPLOADS_DIR, filename)
        dst = os.path.join(DOCS_DIR, filename)
        if os.path.isfile(src):
            shutil.move(src, dst)
            print(f"[+] {filename} docs klasörüne taşındı.")

    # 2. uploads_base.json'u enhanced_document_data.json'a ekle ve uploads_base.json'u boşalt
    if os.path.exists(BASE_JSON):
        with open(BASE_JSON, "r", encoding="utf-8") as f:
            new_base = json.load(f)
        if os.path.exists(ALL_BASE_JSON):
            with open(ALL_BASE_JSON, "r", encoding="utf-8") as f:
                all_base = json.load(f)
        else:
            all_base = []
        filenames = {item.get("filename") for item in all_base}
        for item in new_base:
            if item.get("filename") not in filenames:
                all_base.append(item)
        with open(ALL_BASE_JSON, "w", encoding="utf-8") as f:
            json.dump(all_base, f, ensure_ascii=False, indent=2)
        # uploads_base.json'u boşalt
        with open(BASE_JSON, "w", encoding="utf-8") as f:
            json.dump([], f)
        print(f"[+] uploads_base.json verileri enhanced_document_data.json'a eklendi ve boşaltıldı.")

    # 3. uploads_with_embed.json'u enhanced_document_data_with_embeddings.json'a ekle ve uploads_with_embed.json'u boşalt
    if os.path.exists(EMBED_JSON):
        with open(EMBED_JSON, "r", encoding="utf-8") as f:
            new_embed = json.load(f)
        if os.path.exists(ALL_EMBED_JSON):
            with open(ALL_EMBED_JSON, "r", encoding="utf-8") as f:
                all_embed = json.load(f)
        else:
            all_embed = []
        filenames = {item.get("filename") for item in all_embed}
        for item in new_embed:
            if item.get("filename") not in filenames:
                all_embed.append(item)
        with open(ALL_EMBED_JSON, "w", encoding="utf-8") as f:
            json.dump(all_embed, f, ensure_ascii=False, indent=2)
        # uploads_with_embed.json'u boşalt
        with open(EMBED_JSON, "w", encoding="utf-8") as f:
            json.dump([], f)
        print(f"[+] uploads_with_embed.json verileri enhanced_document_data_with_embeddings.json'a eklendi ve boşaltıldı.")

    print("Tüm işlemler tamamlandı.")

if __name__ == "__main__":
    merge_and_move_uploads()
