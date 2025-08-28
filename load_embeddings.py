#!/usr/bin/env python3
"""
Load from embeddings/embeddings_data.json and create ChromaDB
"""

import json
from embedder import MultiModelEmbedder
from chroma import ChromaDBManager
from config import config

def load_from_embeddings():
    print("📄 Loading from embeddings/embeddings_data.json...")
    
    with open('embeddings/embeddings_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Found {len(data)} documents")
    
    # Initialize
    chroma_manager = ChromaDBManager()
    
    # Bu data zaten doğru formatta - chunks ve embeddings var
    # Ama embeddings yoksa oluşturmamız gerekiyor
    
    # Her doküman için embeddings oluştur
    embedder = MultiModelEmbedder(primary_model=config.EMBEDDING_MODEL)
    
    for doc in data:
        chunks = doc.get('chunks', [])
        if chunks and not doc.get('embeddings'):  # Embeddings yoksa oluştur
            print(f"Creating embeddings for {doc['filename']}: {len(chunks)} chunks")
            embeddings = []
            for chunk in chunks:
                embedding = embedder.embed_single(chunk)
                embeddings.append(embedding.tolist())
            doc['embeddings'] = embeddings
    
    # Artık doğru formatta olan data'yı ChromaDB'ye ekle
    result = chroma_manager.add_documents_batch(data)
    print(f"✅ Total added: {result.get('total_added', 0)} chunks")
    
    # Test retrieval
    print("\n🔍 Testing su yasağı retrieval...")
    query = 'su getirebilir miyim bilgisayar laboratuvarında'
    query_embedding = embedder.embed_single(query)
    search_results = chroma_manager.search_similar(
        query_embedding=query_embedding.tolist(), 
        n_results=5, 
        filters=None
    )
    
    docs = search_results.get('documents', [[]])[0]
    metas = search_results.get('metadatas', [[]])[0]
    distances = search_results.get('distances', [[]])[0]
    
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances)):
        print(f"\nResult {i+1} (Distance: {dist:.4f}):")
        print(f"Source: {meta.get('source_file', 'Unknown')}")
        print(f"Text: {doc[:300]}...")
        if 'su dâhil' in doc or 'içecek' in doc or 'Bilgisayar Laboratuvarlarında' in doc:
            print('*** SU YASAĞI BULUNDU! ***')

if __name__ == "__main__":
    load_from_embeddings()
