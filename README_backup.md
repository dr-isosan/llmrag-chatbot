# RAG (Retrieval-Augmented Generation) Chatbot

Bu proje, dokümanları işleyerek akıllı soru-cevap sistemi oluşturan bir RAG chatbot uygulamasıdır.

## 🎯 Proje Amacı

Üniversite belgelerini (PDF, DOCX, TXT) yükleyerek öğrencilerin sorularını bu belgelerden doğru bilgilerle yanıtlayan bir AI asistan oluşturmak.

## 🏗️ Sistem Mimarisi

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Flask       │    │   ChromaDB      │
│   (React)       │◄──►│     API         │◄──►│   (Vector DB)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   OpenAI GPT    │
                       │   (Language     │
                       │    Model)       │
                       └─────────────────┘
```

## 🔧 Temel Bileşenler

### 1. Document Processor (base.py)
- PDF, DOCX, TXT dosyalarını işler
- Metinleri chunk'lara böler
- Metadata çıkarır

### 2. Embedder (embedder.py)
- Sentence Transformers kullanır
- Metinleri vektör temsillerine dönüştürür
- LaBSE modeli ile 768 boyutlu embedding'ler

### 3. Vector Database (chroma.py)
- ChromaDB ile vektör saklama
- Similarity search
- Metadata filtreleme

### 4. RAG Engine (rag_chatbot.py)
- Query processing
- Retrieval + Generation
- Response evaluation

### 5. Web API (api.py)
- Flask RESTful API
- File upload endpoints
- Chat endpoints

### 6. Frontend (frontend/)
- React TypeScript uygulaması
- Material-UI components
- Real-time chat interface

## 🚀 Kullanım

### Backend Setup
```bash
pip install flask flask-cors chromadb sentence-transformers openai
export OPENAI_API_KEY="your-api-key"
python api.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 📋 API Endpoints

- POST /api/upload - Doküman yükleme
- POST /api/chat - Sohbet
- GET /api/files - Yüklü dosyaları listeleme
- DELETE /api/files/<id> - Dosya silme

## 🔄 İş Akışı

1. **Doküman Yükleme**: Kullanıcı PDF/DOCX yükler
2. **Preprocessing**: Dosya chunk'lara bölünür
3. **Embedding**: Her chunk vektörize edilir
4. **Storage**: Vektörler ChromaDB'ye kaydedilir
5. **Query**: Kullanıcı soru sorar
6. **Retrieval**: İlgili chunk'lar bulunur
7. **Generation**: GPT ile yanıt üretilir
8. **Response**: Kaynaklarla birlikte yanıt döner

## 🛠️ Teknolojiler

**Backend:**
- Python 3.8+
- Flask (Web Framework)
- ChromaDB (Vector Database)
- Sentence Transformers (Embeddings)
- OpenAI API (Language Model)

**Frontend:**
- React 18
- TypeScript
- Material-UI
- Axios

## 🎯 Özellikler

- ✅ Çoklu format desteği (PDF, DOCX, TXT)
- ✅ Akıllı semantic search
- ✅ Context-aware responses
- ✅ Real-time chat interface
- ✅ Document upload & management
- ✅ Source attribution
- ✅ Turkish language support

## 🎓 Staj Projesi Hakkında

Bu proje, modern AI ve NLP teknolojilerini kullanarak pratik bir çözüm geliştiren bir staj çalışmasıdır. RAG (Retrieval-Augmented Generation) mimarisini uygulayarak, geleneksel chatbot'ların bilgi eksikliği problemini çözmeyi amaçlar.

### Öğrenilen Teknolojiler:
- Vector Databases ve Similarity Search
- Transformer-based Embeddings
- Large Language Models (LLM)
- Full-stack Web Development
- RESTful API Design
- Modern Frontend Development
