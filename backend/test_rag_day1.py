"""
RAG System - Day 1 Integration Test

Tests embedding service and vector store together
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.embedding_service import EmbeddingService, get_embedding_service
from app.rag.vector_store import VectorStoreService, Document, get_vector_store


async def test_embedding_service():
    """Test embedding service"""
    print("\n" + "="*60)
    print("Test 1: Embedding Service")
    print("="*60)
    
    # Initialize service
    service = get_embedding_service(provider="openai")
    
    # Test single embedding
    text = "Hello, this is a test document."
    embedding = await service.embed_text(text)
    
    print(f"✅ Single embedding: dim={len(embedding)}")
    print(f"   First 5 values: {embedding[:5]}")
    
    # Test batch embedding
    texts = [
        "Python is a programming language.",
        "Machine learning is fascinating.",
        "I love building AI applications."
    ]
    embeddings = await service.embed_batch(texts)
    
    print(f"✅ Batch embedding: {len(embeddings)} vectors")
    
    # Get model info
    info = service.get_model_info()
    print(f"✅ Model info: {info}")
    
    return True


async def test_vector_store():
    """Test vector store"""
    print("\n" + "="*60)
    print("Test 2: Vector Store Service")
    print("="*60)
    
    # Initialize vector store
    store = get_vector_store(collection_name="test_collection")
    
    # Clear existing data
    await store.clear()
    print("✅ Collection cleared")
    
    # Create test documents
    documents = [
        Document(
            content="Python is a high-level programming language known for its simplicity.",
            metadata={"source": "test", "category": "programming", "topic": "python"}
        ),
        Document(
            content="Machine learning is a subset of artificial intelligence.",
            metadata={"source": "test", "category": "ai", "topic": "ml"}
        ),
        Document(
            content="FastAPI is a modern web framework for building APIs with Python.",
            metadata={"source": "test", "category": "programming", "topic": "fastapi"}
        ),
        Document(
            content="Natural language processing enables computers to understand human language.",
            metadata={"source": "test", "category": "ai", "topic": "nlp"}
        ),
        Document(
            content="Vector databases store high-dimensional embeddings efficiently.",
            metadata={"source": "test", "category": "database", "topic": "vectors"}
        ),
    ]
    
    # Add documents (ChromaDB will auto-generate embeddings)
    doc_ids = await store.add_documents(documents)
    print(f"✅ Added {len(doc_ids)} documents")
    
    # Get stats
    stats = await store.get_stats()
    print(f"✅ Collection stats: {stats['document_count']} documents")
    
    # Test semantic search
    print("\n--- Semantic Search Tests ---")
    
    queries = [
        "What is Python programming?",
        "Tell me about AI and machine learning",
        "How do vector databases work?"
    ]
    
    for query in queries:
        results = await store.search(query, k=2)
        print(f"\nQuery: '{query}'")
        for result in results:
            print(f"  [{result.rank}] Score: {result.score:.3f}")
            print(f"      Content: {result.document.content[:80]}...")
            print(f"      Topic: {result.document.metadata.get('topic')}")
    
    # Test metadata filtering
    print("\n--- Metadata Filter Test ---")
    results = await store.search(
        "programming language",
        k=5,
        filter_metadata={"category": "programming"}
    )
    print(f"Filtered search (category=programming): {len(results)} results")
    for result in results:
        print(f"  - {result.document.metadata.get('topic')}: {result.score:.3f}")
    
    # Test get by ID
    print("\n--- Get by ID Test ---")
    first_doc = await store.get_by_id(doc_ids[0])
    if first_doc:
        print(f"✅ Retrieved document: {first_doc.content[:50]}...")
    
    # Test delete
    print("\n--- Delete Test ---")
    deleted = await store.delete([doc_ids[0]])
    print(f"✅ Deleted {deleted} document(s)")
    
    # Verify deletion
    stats = await store.get_stats()
    print(f"✅ Remaining documents: {stats['document_count']}")
    
    return True


async def test_integration():
    """Test embedding service + vector store integration"""
    print("\n" + "="*60)
    print("Test 3: Integration Test (Embedding + VectorStore)")
    print("="*60)
    
    # Initialize services
    embedding_service = get_embedding_service(provider="openai")
    vector_store = get_vector_store(collection_name="integration_test")
    
    # Clear collection
    await vector_store.clear()
    
    # Prepare documents
    texts = [
        "The quick brown fox jumps over the lazy dog.",
        "A journey of a thousand miles begins with a single step.",
        "To be or not to be, that is the question.",
    ]
    
    # Generate embeddings manually
    embeddings = await embedding_service.embed_batch(texts)
    print(f"✅ Generated {len(embeddings)} embeddings")
    
    # Create documents with pre-computed embeddings
    documents = [
        Document(content=text, metadata={"index": i})
        for i, text in enumerate(texts)
    ]
    
    # Add to vector store
    await vector_store.add_documents(documents, embeddings=embeddings)
    print(f"✅ Added {len(documents)} documents with custom embeddings")
    
    # Search
    results = await vector_store.search("famous quote", k=2)
    print(f"\nSearch results:")
    for result in results:
        print(f"  [{result.rank}] {result.score:.3f}: {result.document.content}")
    
    return True


async def main():
    """Run all tests"""
    print("\n🚀 RAG System - Day 1 Integration Tests")
    print("=" * 60)
    
    try:
        # Test 1: Embedding Service
        success1 = await test_embedding_service()
        
        # Test 2: Vector Store
        success2 = await test_vector_store()
        
        # Test 3: Integration
        success3 = await test_integration()
        
        # Summary
        print("\n" + "="*60)
        print("📊 Test Summary")
        print("="*60)
        print(f"Embedding Service: {'✅ PASS' if success1 else '❌ FAIL'}")
        print(f"Vector Store:      {'✅ PASS' if success2 else '❌ FAIL'}")
        print(f"Integration:       {'✅ PASS' if success3 else '❌ FAIL'}")
        
        if success1 and success2 and success3:
            print("\n🎉 All tests passed! Day 1 objectives complete.")
        else:
            print("\n⚠️  Some tests failed. Please review errors above.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
