#!/usr/bin/env python3
"""
Reprocess all documents with correct embedding model using existing pipeline
"""

from embedder import process_documents_with_embeddings
from chroma import ChromaDBManager
from config import config
import os
import json

def reprocess_documents():
    print("🔄 Starting document reprocessing with existing pipeline...")
    
    print(f"📍 Using embedding model: {config.EMBEDDING_MODEL}")
    print(f"📍 Expected dimension: {config.EMBEDDING_DIMENSION}")
    
    # Create input file for all documents
    docs_dir = 'docs'
    data = []
    
    for filename in os.listdir(docs_dir):
        if filename.endswith('.pdf'):
            filepath = os.path.join(docs_dir, filename)
            print(f'📄 Adding: {filename}')
            
            # Create entry like API does
            data.append({
                "filename": filename,
                "path": filepath,
                "size": os.path.getsize(filepath),
                "type": "pdf"
            })
    
    # Save to temp file  
    temp_input = "temp_input.json"
    with open(temp_input, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Created input file with {len(data)} documents")
    
    # Process with embeddings
    try:
        stats = process_documents_with_embeddings(
            input_file=temp_input,
            output_file="enhanced_document_data.json",
            model_config={
                "primary_model": config.EMBEDDING_MODEL,
                "use_ensemble": False,
                "use_cache": True,
                "use_gpu": False,
            },
        )
        print(f"✅ Processing stats: {stats}")
        
        # Test retrieval
        print('\n🔍 Testing su yasağı retrieval...')
        from embedder import MultiModelEmbedder
        
        embedder = MultiModelEmbedder(primary_model=config.EMBEDDING_MODEL)
        chroma_manager = ChromaDBManager()
        
        query = 'su getirebilir miyim bilgisayar laboratuvarında'
        query_embedding = embedder.embed_single(query)
        search_results = chroma_manager.search_similar(
            query_embedding=query_embedding.tolist(), 
            n_results=5, 
            filters=None
        )
        
        docs = search_results.get('documents', [[]])[0]
        for i, doc in enumerate(docs):
            print(f'\nResult {i+1}: {doc[:200]}...')
            if 'su dâhil' in doc.lower() or 'içecek' in doc.lower():
                print('*** SU YASAĞI BULUNDU! ***')
                
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Cleanup
    if os.path.exists(temp_input):
        os.remove(temp_input)

if __name__ == "__main__":
    reprocess_documents()
