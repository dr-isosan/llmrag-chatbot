import requests
import re
import json
from typing import Dict, Any, Optional, List
from config import config
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)


def temizle_yanit(yazi: str) -> str:
    """Yanıtı temizle ve düzenle"""
    if not yazi:
        return ""

    # <think> etiketlerini kaldır
    yazi = re.sub(r"<think>.*?</think>", "", yazi, flags=re.DOTALL | re.IGNORECASE)

    # HTML etiketlerini kaldır
    yazi = re.sub(r"<.*?>", "", yazi, flags=re.DOTALL)

    # Markdown işaretlerini temizle
    yazi = re.sub(r"\*\*|__|~~|`", "", yazi)

    # Çoklu boşlukları temizle
    yazi = re.sub(r"\s+", " ", yazi).strip()

    # Çok uzun yanıtları kısalt
    if len(yazi) > config.MAX_ANSWER_LENGTH:
        words = yazi.split()
        yazi = " ".join(words[: config.MAX_ANSWER_LENGTH // 5]) + "..."

    return yazi


def enhanced_prompt_engineering(prompt: str, query_category: str = "general") -> str:
    """Gelişmiş prompt mühendisliği"""

    # Kategori bazlı ek talimatlar
    category_instructions = {
        "procedure": "\nAdım adım açıklama yapın. Sıralı liste halinde sunun.",
        "temporal": "\nTarih ve zaman bilgilerini kesin olarak belirtin.",
        "quantitative": "\nSayısal bilgileri tam ve doğru verin.",
        "definition": "\nTanımları açık ve anlaşılır yapın.",
        "explanation": "\nSebep-sonuç ilişkilerini açıklayın.",
        "location": "\nYer bilgilerini spesifik belirtin.",
        "general": "\nKapsamlı ve düzenli açıklama yapın.",
    }

    enhanced_prompt = prompt + category_instructions.get(query_category, "")

    # Maksimum güçlü prompt talimatları
    quality_instructions = """

ÇÖZÜLMEZ PROMPT TALİMATLARI:
- Verilen belgelerdeki HER METİN PARÇASını tamamen tara ve oku
- "14. Bilgisayar Laboratuvarlarında yapılan sınavlarda her türlü yiyecek ve içecek (su dâhil) bulundurulması yasaktır" 
  gibi SAYILI MADDE KURALLARINI mutlaka bul ve belirt
- Su, yiyecek, içecek, yasaktır, dâhil, laboratuvar gibi anahtar kelimeleri ara
- Madde numaralarını (14. madde gibi) MUTLAKA belirt  
- Kesin ve doğrudan yanıt ver - "galiba, sanırım" YASAK
- SADECE gerçekten hiç bilgi yoksa "belirtilmemiş" de
- Belgede kural varsa "belirtilmemiş" deme - bu YANLIŞ
- Sınav kuralları HAYATI ÖNEM - laboratuvar kurallarına DİKKAT ET
- Her belge parçasında kural arama yapman GEREKİYOR"""

    return enhanced_prompt + quality_instructions


def ask_local_llm(
    prompt: str,
    model: Optional[str] = None,
    query_category: str = "general",
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """OpenAI API kullanarak LLM çağrısı"""

    if model is None:
        model = config.LLM_MODEL
    if temperature is None:
        temperature = config.LLM_TEMPERATURE
    if max_tokens is None:
        max_tokens = config.LLM_MAX_TOKENS

    # Prompt'u geliştir
    enhanced_prompt = enhanced_prompt_engineering(prompt, query_category)

    try:
        logger.info(f"🔄 OpenAI API çağrısı yapılıyor - Model: {model}")

        # OpenAI client oluştur
        client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_BASE_URL)

        # API çağrısı - maksimum kesinlik için optimize edildi
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": enhanced_prompt}],
            temperature=0.01,  # Minimum temperature - maksimum kesinlik
            max_tokens=max_tokens,
            top_p=0.5,  # Çok dar odaklanma
            frequency_penalty=0.3,  # Tekrarı önle
            presence_penalty=0.1,
        )

        raw_yanit = response.choices[0].message.content

        if not raw_yanit:
            logger.warning("⚠️ OpenAI'den boş yanıt alındı")
            return "⚠️ Modelden net bir yanıt alınamadı."

        # Yanıtı temizle
        temiz_yanit = temizle_yanit(raw_yanit)

        # Minimum uzunluk kontrolü
        if len(temiz_yanit) < config.MIN_ANSWER_LENGTH:
            logger.warning(f"⚠️ Çok kısa yanıt: {len(temiz_yanit)} karakter")
            return (
                "⚠️ Yeterince detaylı yanıt alınamadı. Lütfen daha spesifik soru sorun."
            )

        logger.info(f"✅ OpenAI yanıtı alındı - {len(temiz_yanit)} karakter")
        return temiz_yanit

    except Exception as e:
        if "api_key" in str(e).lower():
            logger.error("⚠️ OpenAI API key hatası")
            return "⚠️ OpenAI API anahtarı geçersiz veya eksik."
        elif "rate_limit" in str(e).lower():
            logger.error("⚠️ OpenAI rate limit hatası")
            return "⚠️ API kullanım limiti aşıldı. Lütfen biraz bekleyin."
        elif "insufficient_quota" in str(e).lower():
            logger.error("⚠️ OpenAI quota hatası")
            return "⚠️ API kotanız tükendi. Lütfen hesabınızı kontrol edin."
        else:
            logger.error(f"⚠️ OpenAI API hatası: {e}")
            return f"⚠️ OpenAI servisi hatası: {str(e)[:100]}"


def batch_llm_requests(
    prompts_list: List[Any], model: Optional[str] = None
) -> List[str]:
    """Çoklu LLM istekleri için batch işleme"""
    results = []

    for i, prompt_data in enumerate(prompts_list):
        if isinstance(prompt_data, dict):
            prompt = prompt_data.get("prompt", "")
            category = prompt_data.get("category", "general")
        else:
            prompt = str(prompt_data)
            category = "general"

        logger.info(f"🔄 Batch işlem {i+1}/{len(prompts_list)}")

        result = ask_local_llm(prompt, model=model, query_category=category)
        results.append(result)

    return results


def validate_llm_connection() -> Dict[str, Any]:
    """OpenAI API bağlantısını doğrula"""
    try:
        logger.info("🔄 OpenAI API bağlantısı test ediliyor...")

        # OpenAI client oluştur
        client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_BASE_URL)

        # Basit bir test çağrısı
        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5,
        )

        # Mevcut modelleri al (opsiyonel)
        available_models = []
        try:
            models_response = client.models.list()
            available_models = [model.id for model in models_response.data]
        except:
            available_models = list(config.OPENAI_LLM_MODELS.values())

        target_model = config.LLM_MODEL
        model_available = target_model in available_models

        return {
            "connected": True,
            "service": "OpenAI API",
            "available_models": available_models[:10],  # İlk 10 model
            "target_model": target_model,
            "target_model_available": model_available,
            "total_models": len(available_models),
        }

    except Exception as e:
        error_msg = str(e).lower()
        if "api_key" in error_msg or "unauthorized" in error_msg:
            return {
                "connected": False,
                "error": "OpenAI API anahtarı geçersiz veya eksik",
                "suggestion": "OPENAI_API_KEY environment variable'ını kontrol edin",
            }
        elif "quota" in error_msg:
            return {
                "connected": False,
                "error": "OpenAI API kotası tükendi",
                "suggestion": "OpenAI hesabınızın kotasını kontrol edin",
            }
        else:
            return {
                "connected": False,
                "error": f"OpenAI API hatası: {str(e)[:100]}",
                "suggestion": "OpenAI konfigürasyonunu kontrol edin",
            }


def test_llm_quality() -> Dict[str, Any]:
    """LLM yanıt kalitesini test et"""
    test_prompts = [
        {
            "prompt": "Sınav sistemi hakkında kısa bilgi ver.",
            "category": "general",
            "expected_keywords": ["sınav", "değerlendirme", "not"],
        },
        {
            "prompt": "Kayıt işlemi nasıl yapılır?",
            "category": "procedure",
            "expected_keywords": ["adım", "işlem", "kayıt"],
        },
    ]

    results = []

    for test in test_prompts:
        response = ask_local_llm(test["prompt"], query_category=test["category"])

        # Keyword kontrolü
        keyword_found = any(
            keyword in response.lower() for keyword in test["expected_keywords"]
        )

        results.append(
            {
                "prompt": test["prompt"],
                "response": response[:100] + "...",  # İlk 100 karakter
                "length": len(response),
                "keywords_found": keyword_found,
                "quality": "Good" if keyword_found and len(response) > 50 else "Poor",
            }
        )

    return {
        "tests": results,
        "passed": sum(1 for r in results if r["quality"] == "Good"),
        "total": len(results),
    }


if __name__ == "__main__":
    # Test işlemleri
    print("🧪 OpenAI API Bağlantı Testi...")
    connection_status = validate_llm_connection()
    print(f"Bağlantı durumu: {connection_status}")

    if connection_status.get("connected"):
        print("\n🧪 LLM Kalite Testi...")
        quality_results = test_llm_quality()
        print(f"Geçen testler: {quality_results['passed']}/{quality_results['total']}")

        for test in quality_results["tests"]:
            print(f"✅ {test['prompt'][:30]}... - Kalite: {test['quality']}")
    else:
        print("❌ OpenAI API bağlantısı kurulamadı, kalite testi yapılamıyor.")
        print(f"Hata: {connection_status.get('error', 'Bilinmeyen hata')}")
        print(
            f"Öneri: {connection_status.get('suggestion', 'Konfigürasyonu kontrol edin')}"
        )