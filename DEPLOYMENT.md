# Deployment Guide

## Local Development

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API Key

### Quick Start

1. **Clone and Setup Backend**
```bash
cd ragi-simplified-demo
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
python main.py
```

2. **Setup Frontend**
```bash
cd frontend
npm install
npm start
```

3. **Access Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5001

## Production Deployment

### Using Docker (Recommended)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5001
CMD ["python", "main.py"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "5001:5001"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./chroma_db:/app/chroma_db
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

### Manual Deployment

1. **Server Setup**
```bash
sudo apt update
sudo apt install python3 python3-pip nodejs npm nginx
```

2. **Application Setup**
```bash
git clone your-repo
cd ragi-simplified-demo
pip3 install -r requirements.txt
cd frontend && npm install && npm run build
```

3. **Process Management**
```bash
# Install PM2
npm install -g pm2

# Start backend
pm2 start main.py --name rag-backend

# Serve frontend with nginx
sudo cp frontend/build/* /var/www/html/
```

## Environment Variables

```env
OPENAI_API_KEY=your_openai_api_key
CHROMA_PATH=./chroma_db
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
```

## Monitoring

- Check logs: `pm2 logs rag-backend`
- Monitor status: `pm2 status`
- Restart: `pm2 restart rag-backend`
