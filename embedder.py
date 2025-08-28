import os
import json
import logging
import time
import hashlib
from typing import List, Dict, Any, Optional, Union
import numpy as np
from pathlib import Path
import pickle
from datetime import datetime, timedelta
import threading
from multiprocessing import cpu_count

# import openai
# from openai import OpenAI
import requests
from tqdm import tqdm
from config import config
import torch
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """Embedding cache sistemi"""

    def __init__(self, cache_dir: str = "./embedding_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_file = os.path.join(cache_dir, "embedding_cache.pkl")
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, np.ndarray]:
        """Cache'i yükle"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Cache yüklenemedi: {e}")
        return {}

    def _save_cache(self):
        """Cache'i kaydet"""
        try:
            with open(self.cache_file, "wb") as f:
                pickle.dump(self.cache, f)
        except Exception as e:
            logger.error(f"Cache kaydedilemedi: {e}")

    def get_hash(self, text: str, model_name: str) -> str:
        """Text + model için hash oluştur"""
        combined = f"{model_name}:{text}"
        return hashlib.md5(combined.encode()).hexdigest()

    def get(self, text: str, model_name: str) -> Optional[np.ndarray]:
        """Cache'den embedding al"""
        hash_key = self.get_hash(text, model_name)
        return self.cache.get(hash_key)

    def set(self, text: str, model_name: str, embedding: np.ndarray):
        """Cache'e embedding ekle"""
        hash_key = self.get_hash(text, model_name)
        self.cache[hash_key] = embedding

        # Periyodik kaydetme (her 100 yeni embedding'de)
        if len(self.cache) % 100 == 0:
            self._save_cache()

    def clear(self):
        """Cache'i temizle"""
        self.cache.clear()
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)

    def get_stats(self) -> Dict[str, Any]:
        """Cache istatistikleri"""
        return {
            "total_embeddings": len(self.cache),
            "cache_size_mb": (
                os.path.getsize(self.cache_file) / (1024 * 1024)
                if os.path.exists(self.cache_file)
                else 0
            ),
        }


class MultiModelEmbedder:
    """Çoklu model destekli embedding sistemi"""

    DEFAULT_MODELS = [
        "sentence-transformers/LaBSE",  # Primary model - 768 dim
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",  # Fallback - 768 dim
    ]
    use_gpu: bool

    SUPPORTED_MODELS = {
        "multilingual": "sentence-transformers/LaBSE",
        "labse": "sentence-transformers/LaBSE",
        "turkish": "sentence-transformers/LaBSE",
        "universal": "sentence-transformers/LaBSE",
        "fast": "sentence-transformers/LaBSE",
    }

    def __init__(
        self,
        primary_model: Optional[str] = None,
        enable_cache: bool = True,
        use_gpu: bool = False,
    ):
        self.primary_model = primary_model or config.EMBEDDING_MODEL  # Use config model as default
        self.enable_cache = enable_cache
        self.use_gpu = use_gpu
        self.device = self._get_optimal_device(use_gpu)
        self.models = {}  # Model cache
        self.cache = EmbeddingCache() if enable_cache else None

        logger.info(f"🤖 MultiModelEmbedder başlatıldı - Device: {self.device}")

        # Primary model'i yükle
        self._load_model(self.primary_model)

    def _get_optimal_device(self, use_gpu: bool) -> str:
        """Optimal device seçimi"""
        if use_gpu and torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            logger.info(f"GPU bulundu: {gpu_count} GPU, {memory:.1f}GB memory")
            return "cuda"
        elif (
            use_gpu
            and hasattr(torch.backends, "mps")
            and torch.backends.mps.is_available()
        ):
            logger.info("Apple Metal GPU bulundu")
            return "mps"
        else:
            cpu_count = os.cpu_count()
            logger.info(f"CPU kullanılacak: {cpu_count} core")
            return "cpu"

    def _load_model(self, model_name: str) -> SentenceTransformer:
        """Model yükleme - offline öncelikli"""
        if model_name not in self.models:
            logger.info(f"📦 Model yükleniyor: {model_name}")
            try:
                # Offline mode'u dene
                model = SentenceTransformer(model_name, device=self.device, local_files_only=True)

                # Model optimization
                if self.device != "cpu":
                    model.half()  # FP16 for GPU

                self.models[model_name] = model
                logger.info(f"✅ Model offline yüklendi: {model_name}")

            except Exception as e:
                logger.warning(f"⚠️ Offline model yüklenemedi {model_name}: {e}")
                try:
                    # Online mode'u dene
                    logger.info(f"🌐 Online model yükleniyor: {model_name}")
                    model = SentenceTransformer(model_name, device=self.device)
                    
                    if self.device != "cpu":
                        model.half()  # FP16 for GPU
                    
                    self.models[model_name] = model
                    logger.info(f"✅ Model online yüklendi: {model_name}")
                    
                except Exception as e2:
                    logger.error(f"❌ Model yüklenemedi {model_name}: {e2}")
                    # LaBSE fallback models
                    fallback_models = ["sentence-transformers/LaBSE", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"]
                    
                    for fallback in fallback_models:
                        try:
                            logger.info(f"🔄 Fallback model yükleniyor: {fallback}")
                            model = SentenceTransformer(fallback, device=self.device, local_files_only=True)
                            self.models[model_name] = model
                            logger.info(f"✅ Fallback model offline yüklendi: {fallback}")
                            break
                        except:
                            continue
                    else:
                        # Son çare: en basit model
                        raise Exception(f"Hiçbir model yüklenemedi. İnternet bağlantınızı kontrol edin.")

        return self.models[model_name]

    def embed_single(
        self, text: str, model_name: Optional[str] = None, normalize: bool = True
    ) -> np.ndarray:
        """Tek metin için embedding"""
        model_name = model_name or self.primary_model

        # Cache kontrolü
        if self.cache:
            cached_embedding = self.cache.get(text, model_name)
            if cached_embedding is not None:
                return cached_embedding

        # Model yükle
        model = self._load_model(model_name)

        # Embedding hesapla
        try:
            if not text or not text.strip():
                model = self._load_model(model_name or self.primary_model)
                dim = model.get_sentence_embedding_dimension()
                if not dim:
                    dim = config.EMBEDDING_DIMENSION  # Use config dimension (768)
                return np.zeros(dim)

            embedding = model.encode(
                text,
                normalize_embeddings=normalize,
                convert_to_numpy=True,
                show_progress_bar=False,
            )

            # Cache'e kaydet
            if self.cache:
                self.cache.set(text, model_name, embedding)

            return embedding

        except Exception as e:
            logger.error(f"Embedding hatası: {e}")
            # Return zero vector as fallback
            dim = model.get_sentence_embedding_dimension() or config.EMBEDDING_DIMENSION
            return np.zeros(dim)

    def embed_batch(
        self,
        texts: List[str],
        model_name: Optional[str] = None,
        batch_size: Optional[int] = None,
        normalize: bool = True,
        show_progress: bool = False,
    ) -> List[np.ndarray]:
        """Batch embedding işlemi"""
        model_name = model_name or self.primary_model
        batch_size = batch_size or self._get_optimal_batch_size()

        if not texts:
            return []

        logger.info(f"📊 {len(texts)} metin için embedding hesaplanıyor...")
        logger.info(f"Model: {model_name}, Batch size: {batch_size}")

        # Cache kontrolü
        embeddings = []
        cached_results = {}
        texts_to_process = []
        text_indices = []

        if self.cache:
            for i, text in enumerate(texts):
                cached = self.cache.get(text, model_name)
                if cached is not None:
                    cached_results[i] = cached
                else:
                    texts_to_process.append(text)
                    text_indices.append(i)
        else:
            texts_to_process = texts
            text_indices = list(range(len(texts)))

        if texts_to_process:
            try:
                model = self._load_model(model_name)
                processed_embeddings = []
                for i in range(0, len(texts_to_process), batch_size):
                    batch = texts_to_process[i : i + batch_size]
                    batch_embeddings = model.encode(
                        batch,
                        normalize_embeddings=normalize,
                        show_progress_bar=show_progress and i == 0,
                    )
                    processed_embeddings.extend(batch_embeddings)
                for i, embedding in enumerate(processed_embeddings):
                    text_idx = text_indices[i]
                    text = texts_to_process[i]
                    if self.cache:
                        self.cache.set(text, model_name, embedding)
                    cached_results[text_idx] = embedding
            except Exception as e:
                logger.error(f"Batch embedding hatası: {e}")
                model = self._load_model(model_name)
                dim = model.get_sentence_embedding_dimension() or config.EMBEDDING_DIMENSION
                for text_idx in text_indices:
                    cached_results[text_idx] = np.zeros(dim if dim else config.EMBEDDING_DIMENSION)

        for i in range(len(texts)):
            if i in cached_results:
                embeddings.append(cached_results[i])
            else:
                model = self._load_model(model_name)
                dim = model.get_sentence_embedding_dimension()
                if not dim:
                    dim = config.EMBEDDING_DIMENSION
                embeddings.append(np.zeros(dim))

        return embeddings

    def embed_with_ensemble(
        self,
        texts: List[str],
        models: Optional[List[str]] = None,
        weights: Optional[List[float]] = None,
    ) -> List[np.ndarray]:
        """Ensemble embedding (çoklu model birleştirme)"""
        models = models or self.DEFAULT_MODELS[:2]
        weights = weights or [1.0] * len(models)

        if len(models) != len(weights):
            raise ValueError("Model sayısı ve ağırlık sayısı eşit olmalı")

        logger.info(f"🔗 Ensemble embedding: {len(models)} model")

        all_embeddings = []

        # Her model için embedding hesapla
        for model_name, weight in zip(models, weights):
            logger.info(f"📊 Model işleniyor: {model_name} (ağırlık: {weight})")
            model_embeddings = self.embed_batch(texts, model_name, show_progress=False)
            all_embeddings.append((model_embeddings, weight))

        # Ağırlıklı ortalama
        logger.info("🔄 Ensemble birleştirme yapılıyor...")
        ensemble_embeddings = []

        for i in range(len(texts)):
            combined_embedding = None
            total_weight = 0

            for model_embeddings, weight in all_embeddings:
                if model_embeddings[i] is not None:
                    if combined_embedding is None:
                        combined_embedding = model_embeddings[i] * weight
                    else:
                        combined_embedding += model_embeddings[i] * weight
                    total_weight += weight

            if combined_embedding is not None and total_weight > 0:
                combined_embedding /= total_weight
                # Normalize
                norm = np.linalg.norm(combined_embedding)
                if norm > 0:
                    combined_embedding /= norm
                ensemble_embeddings.append(combined_embedding)
            else:
                # Fallback: sıfır vektör
                dim = (
                    len(all_embeddings[0][0][0])
                    if all_embeddings and all_embeddings[0][0]
                    else 768
                )
                ensemble_embeddings.append(np.zeros(dim))

        logger.info("✅ Ensemble embedding tamamlandı")
        return ensemble_embeddings

    def _get_optimal_batch_size(self) -> int:
        """Optimal batch size hesaplama"""
        if self.use_gpu:
            return 32
        else:
            cpu_cores = cpu_count() or 4
            return min(16, max(4, cpu_cores // 2))

    def benchmark_models(
        self, test_texts: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, float]]:
        """Model performance benchmark"""
        test_texts = test_texts or [
            "Bu bir test cümlesidir.",
            "Merhaba dünya! Nasılsın?",
            "Eduroam ağına nasıl bağlanabilirim?",
        ]

        logger.info("🏃 Model benchmark başlıyor...")

        results = {}

        for model_key, model_name in self.SUPPORTED_MODELS.items():
            logger.info(f"⏱️ Test ediliyor: {model_key}")

            try:
                import time

                start_time = time.time()

                # Test embedding
                embeddings = self.embed_batch(
                    test_texts, model_name, show_progress=False
                )

                end_time = time.time()
                duration = end_time - start_time

                # Embedding kalitesi (basit metrik)
                avg_norm = np.mean(
                    [np.linalg.norm(emb) for emb in embeddings if emb is not None]
                )

                results[model_key] = {
                    "model_name": model_name,
                    "duration_seconds": duration,
                    "texts_per_second": len(test_texts) / duration,
                    "avg_embedding_norm": float(avg_norm),
                    "embedding_dimension": (
                        len(embeddings[0])
                        if embeddings and embeddings[0] is not None
                        else 0
                    ),
                }

                logger.info(
                    f"   ⚡ {len(test_texts)/duration:.1f} text/sec, dim: {results[model_key]['embedding_dimension']}"
                )

            except Exception as e:
                logger.error(f"   ❌ Benchmark hatası {model_key}: {e}")
                results[model_key] = {"error": str(e)}

        return results

    def get_model_info(self) -> Dict[str, Any]:
        """Model bilgileri"""
        info = {
            "primary_model": self.primary_model,
            "device": self.device,
            "loaded_models": list(self.models.keys()),
            "cache_enabled": self.cache is not None,
            "supported_models": self.SUPPORTED_MODELS,
        }

        if self.cache:
            info["cache_stats"] = self.cache.get_stats()

        return info

    def cleanup(self):
        """Cleanup işlemleri"""
        if self.cache:
            self.cache._save_cache()

        # GPU memory temizle
        if self.device != "cpu":
            torch.cuda.empty_cache()

        logger.info("🧹 Cleanup tamamlandı")


def process_documents_with_embeddings(
    input_file: str, output_file: str, model_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Dokümanları embedding'lerle işle"""

    # Default config
    default_config = {
        "primary_model": config.EMBEDDING_MODEL,
        "use_ensemble": False,
        "ensemble_models": None,
        "batch_size": None,
        "use_cache": True,
        "use_gpu": True,
    }

    if model_config:
        default_config.update(model_config)

    logger.info("🚀 Embedding işlemi başlıyor...")
    logger.info(f"📄 Girdi: {input_file}")
    logger.info(f"💾 Çıktı: {output_file}")

    # Input dosyasını yükle
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"❌ Input dosyası okunamadı: {e}")
        raise

    if not data:
        logger.error("❌ Input dosyası boş")
        return {"error": "Empty input file"}

    # Embedder oluştur
    embedder = MultiModelEmbedder(
        primary_model=default_config["primary_model"],
        enable_cache=default_config["use_cache"],
        use_gpu=default_config["use_gpu"],
    )

    # İstatistikler
    total_documents = len(data)
    total_chunks = sum(len(item.get("chunks", [])) for item in data)
    processed_chunks = 0

    logger.info(f"📊 {total_documents} doküman, {total_chunks} chunk işlenecek")

    try:
        for doc_idx, item in enumerate(data, 1):
            chunks = item.get("chunks", [])
            if not chunks:
                logger.warning(f"⚠️ Doküman {doc_idx} chunk'ları boş")
                item["embeddings"] = []
                continue

            logger.info(
                f"[{doc_idx}/{total_documents}] İşleniyor: {item.get('filename', 'Unknown')}"
            )

            # Embedding hesapla
            if default_config["use_ensemble"] and default_config["ensemble_models"]:
                embeddings = embedder.embed_with_ensemble(
                    chunks, models=default_config["ensemble_models"]
                )
            else:
                embeddings = embedder.embed_batch(
                    chunks, batch_size=default_config["batch_size"], show_progress=False
                )

            # Numpy array'leri liste'ye çevir
            embeddings_list = []
            for emb in embeddings:
                if emb is not None:
                    embeddings_list.append(emb.tolist())
                else:
                    # Fallback: sıfır vektör
                    embeddings_list.append([0.0] * config.EMBEDDING_DIMENSION)  # Use config dimension

            item["embeddings"] = embeddings_list
            processed_chunks += len(chunks)

            logger.info(f"   ✅ {len(chunks)} chunk embedding tamamlandı")

        # Sonuçları kaydet
        logger.info("💾 Sonuçlar kaydediliyor...")

        # Backup eski dosya (varsa sil)
        if os.path.exists(output_file):
            backup_file = f"{output_file}.backup"
            if os.path.exists(backup_file):
                os.remove(backup_file)
            os.rename(output_file, backup_file)
            logger.info(f"📁 Backup oluşturuldu: {backup_file}")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Dosya boyutu kontrolü
        file_size = os.path.getsize(output_file) / (1024 * 1024)
        logger.info(
            f"✅ Embedding dosyası kaydedildi: {output_file} ({file_size:.2f} MB)"
        )

        # Final istatistikler
        stats = {
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "processed_chunks": processed_chunks,
            "output_file_size_mb": file_size,
            "model_info": embedder.get_model_info(),
        }

        logger.info("📊 EMBEDDING İSTATİSTİKLERİ:")
        logger.info(f"   İşlenen doküman: {total_documents}")
        logger.info(f"   İşlenen chunk: {processed_chunks}")
        logger.info(f"   Dosya boyutu: {file_size:.2f} MB")
        logger.info(f"   Model: {default_config['primary_model']}")

        # Cleanup
        embedder.cleanup()

        return stats

    except Exception as e:
        logger.error(f"❌ Embedding işlemi hatası: {e}")
        embedder.cleanup()
        raise


def main():
    """uploads_base.json'daki verileri embed ederek uploads_with_embed.json'a kaydeder"""
    input_file = "uploads_base.json"
    output_file = "uploads_with_embed.json"

    embedding_config = {
        "primary_model": config.EMBEDDING_MODEL,
        "use_ensemble": False,
        "ensemble_models": [
            "sentence-transformers/LaBSE",  # Use LaBSE instead of MiniLM
            "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        ],
        "use_cache": True,
        "use_gpu": True,
    }

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    try:
        logger.info("🚀 uploads_base.json embedding işlemi başlıyor...")
        stats = process_documents_with_embeddings(
            input_file=input_file,
            output_file=output_file,
            model_config=embedding_config,
        )
        logger.info(f"✅ uploads_with_embed.json kaydedildi. İstatistikler: {stats}")
    except Exception as e:
        logger.error(f"❌ Ana işlem hatası: {e}")
        raise


if __name__ == "__main__":
    main()