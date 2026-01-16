"""
RAG (Retrieval-Augmented Generation) Module

This module provides RAG capabilities for Jarvis, including:
- Vector database integration (Chroma)
- Document processing and chunking
- Semantic retrieval
- Knowledge base management
"""

__version__ = "0.1.0"

from app.rag.embedding_service import EmbeddingService, EmbeddingProvider, get_embedding_service
from app.rag.vector_store import VectorStoreService, Document, SearchResult, get_vector_store
from app.rag.chunking import ChunkingService, Chunk, ChunkingStrategy, get_chunking_service
from app.rag.loaders import (
    DocumentLoader, TextLoader, MarkdownLoader, CodeLoader, PDFLoader,
    LoaderFactory, get_loader_factory
)
from app.rag.document_processor import DocumentProcessor, get_document_processor
from app.rag.retrieval_service import RetrievalService
from app.rag.knowledge_base_service import KnowledgeBaseService

__all__ = [
    # Embedding
    "EmbeddingService",
    "get_embedding_service",
    "EmbeddingProvider",
    # Vector Store
    "VectorStoreService",
    "get_vector_store",
    "Document",
    "SearchResult",
    # Chunking
    "ChunkingService",
    "Chunk",
    "ChunkingStrategy",
    "get_chunking_service",
    # Loaders
    "DocumentLoader",
    "TextLoader",
    "MarkdownLoader",
    "CodeLoader",
    "PDFLoader",
    "LoaderFactory",
    "get_loader_factory",
    # Document Processor
    "DocumentProcessor",
    "get_document_processor",
    # Retrieval Service
    "RetrievalService",
    "get_retrieval_service",
    "RetrievalMode",
    "RetrievalResult",
    # Knowledge Base (to be implemented)
    "KnowledgeBaseService",
]
