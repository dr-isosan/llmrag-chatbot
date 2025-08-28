#!/bin/bash

echo "🚀 GitHub Repository Hazırlama Scripti - Demo Version"
echo "====================================================="

# Git repository başlat
echo "📁 Git repository başlatılıyor..."
git init

# .gitignore dosyasını güncelle
echo "📝 .gitignore güncelleniyor..."
cat > .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# ChromaDB
chroma_db/
*.db
*.sqlite

# Environment variables
.env

# Frontend
frontend/node_modules/
frontend/build/
frontend/.env.local
frontend/.env.development.local
frontend/.env.test.local
frontend/.env.production.local

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Uploads & temp files
uploads/
embeddings/
temp/
GITIGNORE

# Dosyaları stage'e al
echo "�� Dosyalar stage'e alınıyor..."
git add .

# İlk commit
echo "✅ İlk commit yapılıyor..."
git commit -m "🤖 RAG Chatbot Demo - Staj Projesi Showcase

�� IMPORTANT: Bu repository, staj süresince geliştirilen kapsamlı 
RAG chatbot sisteminin DEMO versiyonudur. Asıl production projesi
gizlilik sözleşmeleri nedeniyle private repository'de tutulmaktadır.

🎯 DEMO FEATURES:
✅ RAG (Retrieval-Augmented Generation) pipeline
✅ PDF/DOCX document processing  
✅ Vector database with ChromaDB
✅ React TypeScript frontend
✅ Flask API backend
✅ OpenAI GPT integration

🚀 PRODUCTION'DA EK ÖZELLIKLER:
• Advanced OCR & table processing
• Multi-model embedding fusion
• Enterprise security suite
• Comprehensive monitoring & analytics
• Advanced admin panel
• 90%+ test coverage
• CI/CD pipeline
• Production deployment configs

🛠️ TECH STACK:
• Python 3.8+ (Flask, ChromaDB, Sentence Transformers)
• React 18 + TypeScript + Material-UI
• OpenAI API
• Vector Database Technology

🎓 INTERNSHIP PROJECT:
Bu proje modern AI/ML teknolojilerini kullanarak pratik çözüm
geliştirme becerisini ve full-stack development yetkinliğini
göstermek amacıyla hazırlanmıştır.

�� LEARNING OUTCOMES:
• RAG Architecture & Vector Databases
• Large Language Model Integration  
• Full-stack Web Development
• Production-level Software Design
• Modern Frontend Development

⚠️ DISCLAIMER: Gerçek production kodları NDA kapsamındadır."

echo ""
echo "🎉 Repository hazır!"
echo ""
echo "📋 Sonraki adımlar:"
echo "1. GitHub'da yeni PUBLIC repository oluşturun"
echo "2. Repository adı önerileri:"
echo "   - 'rag-chatbot-demo'"
echo "   - 'internship-rag-project'"
echo "   - 'ai-chatbot-showcase'"
echo "3. git remote add origin <your-repo-url>"
echo "4. git branch -M main"
echo "5. git push -u origin main"
echo ""
echo "💡 Repository'yi CV/LinkedIn'de nasıl tanıtın:"
echo "   📌 'University internship project demonstrating RAG technology'"
echo "   📌 'AI Chatbot with Vector Database & LLM integration'"
echo "   📌 'Full-stack development with modern AI/ML stack'"
echo "   📌 'Simplified version of production-level RAG system'"
echo ""
echo "🔗 README'de belirtilmiş ki bu demo version'dur ve"
echo "    asıl proje çok daha kapsamlıdır. Bu profesyonel yaklaşım"
echo "    işverenlere güven verir!"
echo ""
echo "✨ Bu demo bile modern AI becerilerinizi göstermek için yeterli!"
