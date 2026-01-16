"""
RAG (Retrieval-Augmented Generation) Module

This module provides RAG capabilities for Jarvis, including:
- Vector database integration (Chroma)
- Document processing and chunking
- Semantic retrieval
- Knowledge base management
"""

__version__ = "0.1.0"

from app.rag.embedding_service import EmbeddingService
from app.rag.vector_store import VectorStoreService
from app.rag.document_processor import DocumentProcessor
from app.rag.retrieval_service import RetrievalService
from app.rag.knowledge_base_service import KnowledgeBaseService

__all__ = [
    "EmbeddingService",
    "VectorStoreService",
    "DocumentProcessor",
    "RetrievalService",
    "KnowledgeBaseService",
]
