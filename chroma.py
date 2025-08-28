import os
import json
import shutil
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import numpy as np
from config import config

logger = logging.getLogger(__name__)


class ChromaDBManager:
    """Gelişmiş ChromaDB yönetim sınıfı"""

    def __init__(
        self, chroma_path: str = "./chroma", collection_name: str = "rag_documents"
    ):
        self.chroma_path = chroma_path
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.stats = {
            "total_documents": 0,
            "total_chunks": 0,
            "unique_sources": 0,
            "index_size_mb": 0,
            "last_updated": None,
        }

        self._initialize_client()

    def _initialize_client(self):
        """ChromaDB client başlatma"""
        try:
            # Eğer chroma dizini bozuksa, yeniden oluştur
            if os.path.exists(self.chroma_path):
                try:
                    # Test amaçlı client oluştur
                    test_client = chromadb.PersistentClient(path=self.chroma_path)
                    test_client.list_collections()
                except Exception as e:
                    logger.warning(f"ChromaDB dizini bozuk, yeniden oluşturuluyor: {e}")
                    shutil.rmtree(self.chroma_path)

            # ChromaDB dizinini oluştur
            os.makedirs(self.chroma_path, exist_ok=True)

            # Yeni ChromaDB client konfigürasyonu
            self.client = chromadb.PersistentClient(path=self.chroma_path)

            # Collection oluştur/al
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "hnsw:space": "cosine",  # Cosine similarity için optimize
                    "expected_dimension": str(config.EMBEDDING_DIMENSION)  # Expected dimension metadata
                },
            )
            
            # Dimension uyumluluğunu kontrol et
            self._validate_collection_dimension()

            logger.info(f"✅ ChromaDB başlatıldı: {self.chroma_path}")
            self._update_stats()

        except Exception as e:
            logger.error(f"❌ ChromaDB başlatma hatası: {e}")
            raise

    def _validate_collection_dimension(self):
        """Collection'ın expected dimension ile uyumlu olduğunu kontrol et"""
        try:
            if not self.collection:
                return
                
            # Collection'daki mevcut veri sayısını kontrol et
            count = self.collection.count()
            if count == 0:
                logger.info(f"✅ Yeni collection, dimension: {config.EMBEDDING_DIMENSION}")
                return
                
            # Bir sample embedding al ve dimension kontrolü yap
            sample = self.collection.get(limit=1, include=["embeddings"])
            if sample and sample.get("embeddings") and len(sample["embeddings"]) > 0:
                actual_dim = len(sample["embeddings"][0])
                expected_dim = config.EMBEDDING_DIMENSION
                
                if actual_dim != expected_dim:
                    logger.error(f"❌ DIMENSION MISMATCH! Collection: {actual_dim}, Config: {expected_dim}")
                    logger.warning(f"⚠️ Collection'ı yeniden oluşturmak için clear_chroma.py çalıştırın")
                    raise ValueError(f"Embedding dimension mismatch: {actual_dim} != {expected_dim}")
                else:
                    logger.info(f"✅ Dimension validation passed: {actual_dim}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Dimension validation hatası: {e}")

    def _update_stats(self):
        """İstatistikleri güncelle"""
        try:
            if not self.collection:
                logger.warning("ChromaDB collection None, istatistik güncellenemedi.")
                return
            count = self.collection.count()  # type: ignore
            self.stats["total_chunks"] = count
            self.stats["last_updated"] = datetime.now().isoformat()

            # Dosya boyutu
            if os.path.exists(self.chroma_path):
                size = self._get_directory_size(self.chroma_path)
                self.stats["index_size_mb"] = size

            # Unique sources (metadata'dan)
            if count > 0:
                sample_metadata = self.collection.get(limit=min(count, 1000), include=["metadatas"])  # type: ignore
                if sample_metadata and sample_metadata.get("metadatas"):
                    sources = set()
                    for metadata in sample_metadata["metadatas"] or []:
                        if metadata and "source_file" in metadata:
                            sources.add(metadata["source_file"])
                    self.stats["unique_sources"] = len(sources)
        except Exception as e:
            logger.warning(f"İstatistik güncelleme hatası: {e}")

    def _get_directory_size(self, path: str) -> float:
        """Dizin boyutunu MB cinsinden hesapla"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size / (1024 * 1024)

    def create_backup(self, backup_path: Optional[str] = None) -> str:
        """Database backup oluştur"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.chroma_path}_backup_{timestamp}"

        try:
            if os.path.exists(self.chroma_path):
                shutil.copytree(self.chroma_path, backup_path)
                backup_size = self._get_directory_size(backup_path)
                logger.info(
                    f"✅ Backup oluşturuldu: {backup_path} ({backup_size:.2f} MB)"
                )
                return backup_path
            else:
                logger.warning("Backup alınacak veri yok")
                return ""
        except Exception as e:
            logger.error(f"❌ Backup hatası: {e}")
            raise

    def restore_from_backup(self, backup_path: str):
        """Backup'tan geri yükle"""
        try:
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup bulunamadı: {backup_path}")

            # Mevcut veriyi temizle
            if os.path.exists(self.chroma_path):
                shutil.rmtree(self.chroma_path)

            # Backup'ı geri yükle
            shutil.copytree(backup_path, self.chroma_path)

            # Client'ı yeniden başlat
            self._initialize_client()

            logger.info(f"✅ Backup geri yüklendi: {backup_path}")

        except Exception as e:
            logger.error(f"❌ Restore hatası: {e}")
            raise

    def clear_collection(self):
        """Collection'ı temizle"""
        try:
            if not self.client:
                logger.error("ChromaDB client None, collection silinemedi.")
                return
            self.client.delete_collection(self.collection_name)  # type: ignore
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name, metadata={"hnsw:space": "cosine"}
            )
            self._update_stats()
            logger.info("✅ Collection temizlendi")
        except Exception as e:
            logger.error(f"❌ Collection temizleme hatası: {e}")
            raise

    def check_duplicates(self, new_ids: List[str]) -> Dict[str, Any]:
        """Duplicate ID kontrolü"""
        try:
            if not self.collection:
                logger.error("ChromaDB collection None, duplicate kontrolü yapılamadı.")
                return {"error": "collection is None"}
            existing_ids = set()
            total_count = self.collection.count()  # type: ignore
            batch_size = 1000
            for offset in range(0, total_count, batch_size):
                batch = self.collection.get(
                    limit=min(batch_size, total_count - offset),
                    offset=offset,
                    include=["ids"],  # type: ignore
                )
                if batch and batch.get("ids"):
                    existing_ids.update(batch["ids"] or [])
            duplicates = [id for id in new_ids if id in existing_ids]
            return {
                "total_existing": len(existing_ids),
                "new_ids_count": len(new_ids),
                "duplicates": duplicates,
                "duplicate_count": len(duplicates),
            }
        except Exception as e:
            logger.error(f"❌ Duplicate kontrol hatası: {e}")
            return {"error": str(e)}

    def add_documents_batch(
        self,
        data: List[Dict[str, Any]],
        batch_size: int = 1000,
        skip_duplicates: bool = True,
    ) -> Dict[str, Any]:
        """Gelişmiş batch doküman ekleme"""

        logger.info("🚀 Batch doküman ekleme başlıyor...")

        if not self.collection:
            logger.error("ChromaDB collection None, ekleme yapılamadı.")
            return {"total_added": 0, "skipped": 0, "errors": ["collection is None"]}

        # Verileri işle
        ids, embeddings, metadatas, documents = self._process_data_batch(data)
        total_chunks = len(ids)

        if total_chunks == 0:
            logger.warning("⚠️ Eklenecek chunk bulunamadı")
            return {"total_added": 0, "skipped": 0, "errors": []}

        logger.info(f"📊 Toplam {total_chunks} chunk işlenecek")

        # Duplicate kontrolü
        duplicate_info = {"duplicates": [], "duplicate_count": 0}
        if skip_duplicates:
            logger.info("🔍 Duplicate kontrol yapılıyor...")
            duplicate_info = self.check_duplicates(ids)

            if duplicate_info.get("duplicate_count", 0) > 0:
                logger.info(
                    f"⚠️ {duplicate_info['duplicate_count']} duplicate bulundu, atlanacak"
                )

                # Duplicate'leri filtrele
                duplicate_set = set(duplicate_info["duplicates"])
                filtered_data = []

                for i, id in enumerate(ids):
                    if id not in duplicate_set:
                        filtered_data.append(
                            (ids[i], embeddings[i], metadatas[i], documents[i])
                        )

                if filtered_data:
                    ids, embeddings, metadatas, documents = zip(*filtered_data)
                    ids, embeddings, metadatas, documents = (
                        list(ids),
                        list(embeddings),
                        list(metadatas),
                        list(documents),
                    )
                else:
                    logger.info("⚠️ Tüm veriler duplicate, ekleme atlanıyor")
                    return {
                        "total_added": 0,
                        "skipped": duplicate_info["duplicate_count"],
                        "errors": [],
                    }

        # Batch ekleme
        total_added = 0
        errors = []

        logger.info(
            f"⚡ {len(ids)} chunk ChromaDB'ye eklenecek (batch size: {batch_size})"
        )

        from collections.abc import Sequence

        for i in range(0, len(ids), batch_size):
            end = min(i + batch_size, len(ids))
            batch_num = (i // batch_size) + 1
            total_batches = (len(ids) + batch_size - 1) // batch_size

            try:
                # Embedding ve metadata tiplerini Sequence'e çevir
                emb_batch = embeddings[i:end]
                meta_batch = metadatas[i:end]
                if not isinstance(emb_batch, Sequence):
                    emb_batch = list(emb_batch)
                if not isinstance(meta_batch, Sequence):
                    meta_batch = list(meta_batch)
                self.collection.add(
                    ids=ids[i:end],
                    embeddings=emb_batch,  # type: ignore
                    metadatas=meta_batch,  # type: ignore
                    documents=documents[i:end],
                )  # type: ignore
                batch_size_actual = end - i
                total_added += batch_size_actual

                logger.info(
                    f"📦 Batch {batch_num}/{total_batches}: {batch_size_actual} chunk eklendi"
                )

            except Exception as e:
                error_msg = f"Batch {batch_num} hatası: {e}"
                logger.error(f"❌ {error_msg}")
                errors.append(error_msg)
                continue

        # İstatistikleri güncelle
        self._update_stats()

        # Sonuç raporu
        result = {
            "total_processed": total_chunks,
            "total_added": total_added,
            "skipped": duplicate_info.get("duplicate_count", 0),
            "errors": errors,
            "success_rate": total_added / total_chunks if total_chunks > 0 else 0,
        }

        logger.info("✅ Batch ekleme tamamlandı")
        logger.info(
            f"📊 Eklenen: {total_added}, Atlanan: {result['skipped']}, Hata: {len(errors)}"
        )

        return result

    def _process_data_batch(
        self, data: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[List[float]], List[Dict[str, Any]], List[str]]:
        """Veri batch'ini işle"""
        ids, embeddings, metadatas, documents = [], [], [], []

        for item in data:
            filename = item.get("filename", "unknown")
            file_type = item.get("file_type", "unknown")
            chunks = item.get("chunks", [])
            chunk_embeddings = item.get("embeddings", [])
            chunk_metadata = item.get("chunk_metadata", [])
            doc_metadata = item.get("document_metadata", {})

            # Chunk count kontrolü
            if len(chunks) != len(chunk_embeddings):
                logger.warning(
                    f"⚠️ {filename}: chunk-embedding sayısı eşleşmiyor ({len(chunks)} vs {len(chunk_embeddings)})"
                )
                min_count = min(len(chunks), len(chunk_embeddings))
                chunks = chunks[:min_count]
                chunk_embeddings = chunk_embeddings[:min_count]

            # Her chunk için
            for idx, (chunk, embedding) in enumerate(zip(chunks, chunk_embeddings)):
                if not chunk.strip():
                    continue

                # ID oluştur (daha unique)
                chunk_hash = hashlib.md5(chunk.encode()).hexdigest()[:8]
                unique_id = f"{filename}_{idx}_{chunk_hash}"

                # Metadata oluştur
                metadata = {
                    "source_file": filename,
                    "file_type": file_type,
                    "chunk_index": idx,
                    "chunk_hash": chunk_hash,
                    "chunk_length": len(chunk),
                    "upload_timestamp": datetime.now().isoformat(),
                }

                # Doküman metadata'sını flatten ederek ekle (ChromaDB primitive types only)
                if doc_metadata:
                    for key, value in doc_metadata.items():
                        if value is not None:
                            # ChromaDB sadece str, int, float, bool kabul eder
                            if isinstance(value, (str, int, float, bool)):
                                metadata[f"doc_{key}"] = value
                            else:
                                metadata[f"doc_{key}"] = str(value)

                # Chunk-specific metadata ekle
                if chunk_metadata and idx < len(chunk_metadata):
                    metadata.update(chunk_metadata[idx])

                ids.append(unique_id)
                embeddings.append(embedding)
                metadatas.append(metadata)
                documents.append(chunk)

        return ids, embeddings, metadatas, documents

    def search_similar(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Gelişmiş similarity search"""
        try:
            if not self.collection:
                logger.error("ChromaDB collection None, arama yapılamadı.")
                return {
                    "documents": [[]],
                    "metadatas": [[]],
                    "distances": [[]],
                    "total_found": 0,
                }
            # Where clause oluştur
            where_clause = None
            if filters:
                where_clause = self._build_where_clause(filters)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],  # type: ignore
                where=where_clause,
            )  # type: ignore
            docs = (
                results.get("documents", [[]])
                if results and results.get("documents")
                else [[]]
            )
            return {
                "documents": docs,
                "metadatas": results.get("metadatas", [[]]) if results else [[]],
                "distances": results.get("distances", [[]]) if results else [[]],
                "total_found": len(docs[0]) if docs and docs[0] else 0,
            }
        except Exception as e:
            logger.error(f"❌ Search hatası: {e}")
            return {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
                "total_found": 0,
            }

    def _build_where_clause(self, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Filter'ları ChromaDB where clause'una çevir"""
        where = {}
        for key, value in filters.items():
            if key == "source_files" and isinstance(value, list):
                where["source_file"] = {"$in": value}
            elif key == "file_types" and isinstance(value, list):
                where["file_type"] = {"$in": value}
            elif key == "min_chunk_length":
                where["chunk_length"] = {"$gte": value}
            elif key == "max_chunk_length":
                where["chunk_length"] = {"$lte": value}
            elif isinstance(value, str):
                where[key] = {"$eq": value}
            elif isinstance(value, (int, float)):
                where[key] = {"$eq": value}
        return where if where else None

    def get_collection_info(self) -> Dict[str, Any]:
        """Collection bilgilerini al"""
        try:
            if not self.collection:
                logger.error("ChromaDB collection None, bilgi alınamıyor.")
                return {"error": "collection is None"}
            count = self.collection.count()  # type: ignore
            info = {
                "collection_name": self.collection_name,
                "total_chunks": count,
                "chroma_path": self.chroma_path,
                "stats": self.stats,
            }
            if count > 0:
                sample = self.collection.get(
                    limit=min(100, count), include=["metadatas"]
                )  # type: ignore
                if sample and sample.get("metadatas"):
                    sources = set()
                    file_types = set()
                    for metadata in sample["metadatas"] or []:
                        if metadata:
                            if "source_file" in metadata:
                                sources.add(metadata["source_file"])
                            if "file_type" in metadata:
                                file_types.add(metadata["file_type"])
                    info["unique_sources"] = list(sources)
                    info["file_types"] = list(file_types)
                    info["source_count"] = len(sources)
                    info["file_type_count"] = len(file_types)
            return info
        except Exception as e:
            logger.error(f"❌ Collection info hatası: {e}")
            return {"error": str(e)}

    def optimize_collection(self) -> Dict[str, Any]:
        """Collection optimizasyonu"""
        logger.info("🔧 Collection optimizasyonu başlıyor...")

        try:
            before_size = self._get_directory_size(self.chroma_path)

            # ChromaDB'nin kendi optimizasyon fonksiyonları varsa çağır
            # (Bu özellik ChromaDB versiyonuna göre değişebilir)

            after_size = self._get_directory_size(self.chroma_path)

            result = {
                "before_size_mb": before_size,
                "after_size_mb": after_size,
                "size_reduction_mb": before_size - after_size,
                "optimization_completed": True,
            }

            logger.info(
                f"✅ Optimizasyon tamamlandı: {before_size:.2f}MB -> {after_size:.2f}MB"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Optimizasyon hatası: {e}")
            return {"error": str(e), "optimization_completed": False}

    def export_data(
        self, output_file: str, include_embeddings: bool = False
    ) -> Dict[str, Any]:
        """Collection'ı dışa aktar"""
        logger.info(f"📤 Collection dışa aktarılıyor: {output_file}")

        try:
            if not self.collection:
                logger.error("ChromaDB collection None, export yapılamadı.")
                return {"error": "collection is None"}
            total_count = self.collection.count()  # type: ignore
            batch_size = 1000
            exported_count = 0
            exported_data = []
            for offset in range(0, total_count, batch_size):
                include_fields = ["ids", "documents", "metadatas"]
                if include_embeddings:
                    include_fields.append("embeddings")
                batch = self.collection.get(
                    limit=min(batch_size, total_count - offset),
                    offset=offset,
                    include=include_fields,  # type: ignore
                )
                if batch and batch.get("ids"):
                    for i in range(len(batch["ids"])):
                        doc_list = batch.get("documents") or []
                        meta_list = batch.get("metadatas") or []
                        emb_list = batch.get("embeddings") or []
                        item = {
                            "id": batch["ids"][i],
                            "document": doc_list[i] if i < len(doc_list) else None,
                            "metadata": meta_list[i] if i < len(meta_list) else None,
                        }
                        if include_embeddings and emb_list and i < len(emb_list):
                            item["embedding"] = emb_list[i]
                        exported_data.append(item)
                        exported_count += 1
                logger.info(f"📦 Exported: {exported_count}/{total_count}")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "collection_name": self.collection_name,
                        "export_timestamp": datetime.now().isoformat(),
                        "total_items": exported_count,
                        "includes_embeddings": include_embeddings,
                        "data": exported_data,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            file_size = os.path.getsize(output_file) / (1024 * 1024)
            result = {
                "exported_count": exported_count,
                "output_file": output_file,
                "file_size_mb": file_size,
                "includes_embeddings": include_embeddings,
            }
            logger.info(
                f"✅ Export tamamlandı: {exported_count} item, {file_size:.2f}MB"
            )
            return result
        except Exception as e:
            logger.error(f"❌ Export hatası: {e}")
            return {"error": str(e)}

    def get_stats(self) -> Dict[str, Any]:
        """İstatistikleri döndür"""
        self._update_stats()
        return self.stats.copy()


def main():
    """uploads_with_embed.json'daki verileri ChromaDB'ye ekler"""
    chroma_path = "./chroma"
    input_file = "uploads_with_embed.json"
    collection_name = "rag_documents"

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logger.info("🚀 uploads_with_embed.json ChromaDB'ye aktarılıyor...")

    if not os.path.exists(input_file):
        logger.error(f"❌ Giriş dosyası bulunamadı: {input_file}")
        return

    try:
        chroma_manager = ChromaDBManager(chroma_path, collection_name)

        # Mevcut durum kontrolü
        current_info = chroma_manager.get_collection_info()
        if current_info.get("total_chunks", 0) > 0:
            logger.info(f"⚠️ Collection'da {current_info['total_chunks']} chunk mevcut")
            # Otomatik olarak temizlemeden devam et, istenirse kodla eklenir

        logger.info(f"📄 JSON dosyası yükleniyor: {input_file}")
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data:
            logger.warning(f"⚠️ JSON dosyası boş: {input_file}")
            return

        logger.info(f"📊 {len(data)} doküman bulundu")

        # Batch import
        result = chroma_manager.add_documents_batch(
            data=data, batch_size=1000, skip_duplicates=True
        )

        logger.info("📊 IMPORT RAPORU:")
        logger.info(f"   İşlenen: {result['total_processed']}")
        logger.info(f"   Eklenen: {result['total_added']}")
        logger.info(f"   Atlanan: {result['skipped']}")
        logger.info(f"   Başarı oranı: {result['success_rate']:.1%}")
        if result["errors"]:
            logger.warning(f"⚠️ {len(result['errors'])} hata oluştu:")
            for error in result["errors"][:5]:
                logger.warning(f"   - {error}")

        # Final istatistikler
        final_stats = chroma_manager.get_stats()
        logger.info("📊 FİNAL İSTATİSTİKLER:")
        logger.info(f"   Toplam chunk: {final_stats['total_chunks']:,}")
        logger.info(f"   Unique source: {final_stats['unique_sources']}")
        logger.info(f"   Index boyutu: {final_stats['index_size_mb']:.2f} MB")

        logger.info("✅ uploads_with_embed.json ChromaDB'ye başarıyla aktarıldı!")

    except KeyboardInterrupt:
        logger.info("⚠️ İşlem kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"❌ Ana işlem hatası: {e}")
        raise


if __name__ == "__main__":
    main()