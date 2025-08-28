#!/usr/bin/env python3
"""
Retrieval test - Neden su yasağı bulunamıyor?
"""

from chroma import ChromaDBManager
from embedder import MultiModelEmbedder
from config import config

def test_retrieval():
    # Test retrieval
    embedder = MultiModelEmbedder(primary_model=config.EMBEDDING_MODEL)  # Use LaBSE
    chroma_manager = ChromaDBManager()

    query = 'su getirebilir miyim bilgisayar laboratuvarında'
    print(f'Query: {query}')

    query_embedding = embedder.embed_single(query)
    search_results = chroma_manager.search_similar(
        query_embedding=query_embedding.tolist(), 
        n_results=10, 
        filters=None
    )

    print('\n=== SEARCH RESULTS ===')
    docs = search_results.get('documents', [[]])[0]
    metas = search_results.get('metadatas', [[]])[0]
    distances = search_results.get('distances', [[]])[0]

    for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances)):
        print(f'\n--- Result {i+1} (Distance: {dist:.4f}) ---')
        print(f'Source: {meta.get("source_file", "Unknown")}')
        
        # Su ile ilgili kısım var mı?
        if 'su' in doc.lower() or 'içecek' in doc.lower() or 'yiyecek' in doc.lower():
            print('*** İÇECEK/SU YASAGI BULUNDU! ***')
        
        print(f'Text: {doc[:300]}...')
        
        # 14. madde arayalım
        if '14.' in doc and 'Bilgisayar' in doc:
            print('*** 14. MADDE BULUNDU! ***')

if __name__ == "__main__":
    test_retrieval()
