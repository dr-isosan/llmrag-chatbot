# Simplified version of RAG (Retrieval-Augmented Generation) Chatbot 

> **⚠️
> 
> **🇺🇸 English:** This repository contains a **simplified demonstration version** of a comprehensive RAG chatbot system developed during my internship.
> 
> **🇹🇷 Türkçe:** Bu repository, stajım süresince geliştirdiğim kapsamlı RAG chatbot sisteminin **basitleştirilmiş demo versiyonunu** içermektedir.

## 🎯 Purpose / Amaç

**🇺🇸** Create an intelligent Q&A system that processes university documents (PDF, DOCX, TXT) to answer student questions with accurate information extracted from those documents.

**🇹🇷** Üniversite belgelerini (PDF, DOCX, TXT) işleyerek öğrencilerin sorularını bu belgelerden doğru bilgilerle yanıtlayan bir AI asistan oluşturmak.


## 🏗️ System Architecture / Sistem Mimarisi

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


## 🚀 Quick Start / Hızlı Başlangıç

### Prerequisites / Gereksinimler
```bash
Python 3.8+
Node.js 16+
OpenAI API Key
```

### Installation / Kurulum
```bash
# Backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
python main.py

# Frontend
cd frontend
npm install
npm start
```

### Access / Erişim
- Frontend: http://localhost:3000
- Backend API: http://localhost:5001

## 🛠️ Technology Stack / Teknoloji Yığını

**Backend:**
- Flask (Web Framework)
- ChromaDB (Vector Database)
- Sentence Transformers (Embeddings)
- OpenAI API (Language Model)
- PyPDF2, python-docx (Document Processing)

**Frontend:**
- React 18 (UI Framework)
- TypeScript (Type Safety)
- Material-UI (UI Components)
- Axios (HTTP Client)

## 📁 Project Structure / Proje Yapısı

```
ragi-simplified-demo/
├── README.md              # This file / Bu dosya
├── main.py                # Entry point / Giriş noktası
├── requirements.txt       # Dependencies / Bağımlılıklar
├── config.py              # Configuration / Konfigürasyon
├── rag_chatbot.py         # RAG engine / RAG motoru
├── api.py                 # Flask API
├── base.py                # Document processor / Doküman işleyici
├── embedder.py            # Embeddings / Gömülümler
├── chroma.py              # Vector DB / Vektör DB
├── demo.py                # Demo script / Demo scripti
├── DEPLOYMENT.md          # Deployment guide / Kurulum rehberi
└── frontend/              # React application / React uygulaması
    ├── src/
    │   ├── App.tsx
    │   └── components/
    │       ├── ChatBot.tsx
    │       └── DocsManager.tsx
    └── package.json
```

## 🎓 Internship Project Context / Staj Projesi Bağlamı

**🇺🇸** This project was developed during my university internship to demonstrate proficiency in:
- Modern AI/ML technologies (RAG, Vector Databases, LLMs)
- Full-stack development capabilities
- Understanding of production-level software architecture
- Ability to work with cutting-edge NLP technologies

**🇹🇷** Bu proje, üniversite stajım süresince aşağıdaki konulardaki yetkinliğimi göstermek için geliştirildi:
- Modern AI/ML teknolojileri (RAG, Vektör Veritabanları, LLM'ler)
- Full-stack geliştirme yetenekleri
- Production seviyesi yazılım mimarisi anlayışı
- Çağdaş NLP teknolojileriyle çalışabilme yetisi



## 🎯 Key Learning Outcomes / Temel Öğrenme Çıktıları

- ✅ RAG (Retrieval-Augmented Generation) architecture
- ✅ Vector databases and similarity search
- ✅ Transformer-based embeddings
- ✅ Large Language Model integration
- ✅ Full-stack web development
- ✅ RESTful API design
- ✅ Modern frontend development with React/TypeScript
- ✅ Production deployment considerations

---

**⭐ If you found this demo useful, please consider giving it a star/home/dr_iso/Lecture/ragi-simplified-demo && head -20 README.md*  
**⭐ Bu demo'yu faydalı bulduysanız, lütfen yıldız vermeyi düşünün!**
