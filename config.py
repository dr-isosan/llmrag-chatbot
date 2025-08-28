# RAG Chatbot Configuration
import os
from typing import Dict, Any
from env_loader import *


class RAGConfig:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = "https://api.openai.com/v1"

    # Embedding Configuration
    EMBEDDING_MODEL = "sentence-transformers/LaBSE"  # LaBSE model
    EMBEDDING_DIMENSION = 768  # LaBSE dimension
    NORMALIZE_EMBEDDINGS = True

    # Retrieval Configuration
    DEFAULT_N_RESULTS = 10  # Increased from 5
    MAX_N_RESULTS = 20  # Increased from 10
    SIMILARITY_THRESHOLD = 0.01  # Much lower threshold - daha fazla chunk dahil et
    RERANK_TOP_K = 3

    # Text Processing Configuration
    MAX_CHUNK_SIZE = 1024  # Increased from 512 - daha büyük chunk'lar
    CHUNK_OVERLAP = 100  # Increased from 50 - daha fazla overlap
    MAX_CONTEXT_LENGTH = 4000  # Increased from 2000 - daha fazla context

    # LLM Configuration - OpenAI API
    LLM_MODEL = "gpt-4o"  # OpenAI GPT model
    LLM_TEMPERATURE = 0.1  # Lower for more factual responses
    LLM_MAX_TOKENS = 2048  # Increased from 512 for complete responses

    # Alternative OpenAI models
    OPENAI_LLM_MODELS = {
        "gpt4o": "gpt-4o",
        "gpt4o-mini": "gpt-4o-mini",
        "gpt4-turbo": "gpt-4-turbo",
        "gpt35-turbo": "gpt-3.5-turbo",
    }

    # Quality Control
    MIN_ANSWER_LENGTH = 20
    MAX_ANSWER_LENGTH = 1000
    REQUIRE_SOURCE_VALIDATION = True

    # Prompt Templates
    SYSTEM_PROMPT = """Sen bir üniversite bilgi asistanısın. Verilen belgelerden kesin, doğru ve yararlı bilgiler çıkararak cevap vermelisin.

KURALLAR:
1. SADECE sorulan soruyu yanıtla - başka konuları dahil etme
2. Sadece verilen belgelerden bilgi kullan
3. Belirsiz olduğun konularda "belirtilmemiş" de
4. Sayısal bilgileri (tarih, süre, puan) kesin olarak belirt
5. Alakasız bilgileri yanıta dahil etme
6. Tek bir konuya odaklan
7. Kaynak belge adını cevabın sonunda belirt
8. Türkçe dilbilgisi kurallarına uy"""

    RAG_PROMPT_TEMPLATE = """
{system_prompt}

SORU: {question}

İLGİLİ BELGELER:
{context}

ÖNEMLİ: Sadece soruyla DOĞRUDAN alakalı bilgileri yanıtla. Başka konulardan bahsetme!

CEVAP (Kısa, net ve sadece soruyla alakalı):
"""

    FALLBACK_RESPONSE = "Bu konuda belgelerimde yeterli bilgi bulunmuyor. Lütfen daha spesifik bir soru sorun veya farklı bir konuda soru sormayı deneyin."


# Global config instance
config = RAGConfig()