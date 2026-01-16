"""
Vector Store Service

Provides vector database operations using ChromaDB.
Handles document storage, retrieval, and management.
"""
from typing import List, Dict, Optional, Any
import logging
import os
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class Document:
    """Document model for vector store"""
    
    def __init__(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
        embedding: Optional[List[float]] = None
    ):
        self.id = doc_id or str(uuid.uuid4())
        self.content = content
        self.metadata = metadata or {}
        self.embedding = embedding
        
        # Add timestamp if not present
        if "timestamp" not in self.metadata:
            self.metadata["timestamp"] = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "embedding": self.embedding
        }


class SearchResult:
    """Search result model"""
    
    def __init__(
        self,
        document: Document,
        score: float,
        rank: int
    ):
        self.document = document
        self.score = score  # Similarity score (0-1, higher is better)
        self.rank = rank    # Rank in results (1-based)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "rank": self.rank,
            "score": self.score,
            "document": self.document.to_dict()
        }


class VectorStoreService:
    """
    Vector database service using ChromaDB
    
    Features:
    - Document storage with embeddings
    - Semantic similarity search
    - Metadata filtering
    - Collection management
    
    Usage:
        store = VectorStoreService(collection_name="my_kb")
        await store.add_documents(documents)
        results = await store.search("query text", k=5)
    """
    
    def __init__(
        self,
        collection_name: str = "jarvis_default",
        persist_directory: Optional[str] = None,
        embedding_function: Optional[Any] = None
    ):
        """
        Initialize vector store
        
        Args:
            collection_name: Name of the collection
            persist_directory: Directory for persistent storage
            embedding_function: Custom embedding function (optional)
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory or os.path.join(
            os.getcwd(), "data", "chroma"
        )
        
        # Ensure directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize ChromaDB
        self._initialize_chroma(embedding_function)
        
        logger.info(
            f"Initialized VectorStoreService: collection={collection_name}, "
            f"persist_dir={self.persist_directory}"
        )
    
    def _initialize_chroma(self, embedding_function: Optional[Any] = None):
        """Initialize ChromaDB client and collection"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Create persistent client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            if embedding_function:
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    embedding_function=embedding_function,
                    metadata={"created_at": datetime.now().isoformat()}
                )
            else:
                # Use default embedding function
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"created_at": datetime.now().isoformat()}
                )
            
            logger.info(f"ChromaDB collection '{self.collection_name}' ready")
            
        except ImportError:
            logger.error("ChromaDB not installed. Run: pip install chromadb")
            raise
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise
    
    async def add_documents(
        self,
        documents: List[Document],
        embeddings: Optional[List[List[float]]] = None
    ) -> List[str]:
        """
        Add documents to vector store
        
        Args:
            documents: List of Document objects
            embeddings: Pre-computed embeddings (optional)
            
        Returns:
            List of document IDs
        """
        if not documents:
            logger.warning("No documents to add")
            return []
        
        try:
            # Prepare data for ChromaDB
            ids = [doc.id for doc in documents]
            contents = [doc.content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            # Add to collection
            if embeddings:
                self.collection.add(
                    ids=ids,
                    documents=contents,
                    metadatas=metadatas,
                    embeddings=embeddings
                )
            else:
                # ChromaDB will generate embeddings automatically
                self.collection.add(
                    ids=ids,
                    documents=contents,
                    metadatas=metadatas
                )
            
            logger.info(f"Added {len(documents)} documents to collection")
            return ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    async def search(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.0
    ) -> List[SearchResult]:
        """
        Semantic search for similar documents
        
        Args:
            query: Query text
            k: Number of results to return
            filter_metadata: Metadata filter (optional)
            score_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of SearchResult objects
        """
        if not query or not query.strip():
            logger.warning("Empty query provided")
            return []
        
        try:
            # Perform search
            query_params = {
                "query_texts": [query],
                "n_results": k
            }
            
            if filter_metadata:
                query_params["where"] = filter_metadata
            
            results = self.collection.query(**query_params)
            
            # Parse results
            search_results = []
            if results and results["documents"] and results["documents"][0]:
                documents = results["documents"][0]
                metadatas = results["metadatas"][0]
                distances = results["distances"][0]
                ids = results["ids"][0]
                
                for rank, (doc_id, content, metadata, distance) in enumerate(
                    zip(ids, documents, metadatas, distances), start=1
                ):
                    # Convert distance to similarity score (1 - normalized_distance)
                    # Chroma uses L2 distance, lower is better
                    # Normalize to 0-1 range where 1 is most similar
                    score = max(0.0, 1.0 - (distance / 2.0))
                    
                    # Apply threshold filter
                    if score < score_threshold:
                        continue
                    
                    doc = Document(
                        content=content,
                        metadata=metadata,
                        doc_id=doc_id
                    )
                    
                    search_results.append(
                        SearchResult(document=doc, score=score, rank=rank)
                    )
            
            logger.info(
                f"Search returned {len(search_results)} results "
                f"(threshold={score_threshold})"
            )
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            raise
    
    async def search_with_embedding(
        self,
        embedding: List[float],
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search using pre-computed embedding
        
        Args:
            embedding: Query embedding vector
            k: Number of results
            filter_metadata: Metadata filter (optional)
            
        Returns:
            List of SearchResult objects
        """
        try:
            query_params = {
                "query_embeddings": [embedding],
                "n_results": k
            }
            
            if filter_metadata:
                query_params["where"] = filter_metadata
            
            results = self.collection.query(**query_params)
            
            # Parse results (similar to search method)
            search_results = []
            if results and results["documents"] and results["documents"][0]:
                documents = results["documents"][0]
                metadatas = results["metadatas"][0]
                distances = results["distances"][0]
                ids = results["ids"][0]
                
                for rank, (doc_id, content, metadata, distance) in enumerate(
                    zip(ids, documents, metadatas, distances), start=1
                ):
                    score = max(0.0, 1.0 - (distance / 2.0))
                    
                    doc = Document(
                        content=content,
                        metadata=metadata,
                        doc_id=doc_id
                    )
                    
                    search_results.append(
                        SearchResult(document=doc, score=score, rank=rank)
                    )
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching with embedding: {e}")
            raise
    
    async def get_by_id(self, doc_id: str) -> Optional[Document]:
        """
        Get document by ID
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document object or None
        """
        try:
            results = self.collection.get(ids=[doc_id])
            
            if results and results["documents"]:
                content = results["documents"][0]
                metadata = results["metadatas"][0]
                
                return Document(
                    content=content,
                    metadata=metadata,
                    doc_id=doc_id
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting document by ID: {e}")
            return None
    
    async def delete(self, doc_ids: List[str]) -> int:
        """
        Delete documents by IDs
        
        Args:
            doc_ids: List of document IDs
            
        Returns:
            Number of documents deleted
        """
        if not doc_ids:
            return 0
        
        try:
            self.collection.delete(ids=doc_ids)
            logger.info(f"Deleted {len(doc_ids)} documents")
            return len(doc_ids)
            
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
    
    async def delete_by_metadata(self, filter_metadata: Dict[str, Any]) -> int:
        """
        Delete documents by metadata filter
        
        Args:
            filter_metadata: Metadata filter
            
        Returns:
            Number of documents deleted
        """
        try:
            # First get IDs matching the filter
            results = self.collection.get(where=filter_metadata)
            
            if results and results["ids"]:
                doc_ids = results["ids"]
                self.collection.delete(ids=doc_ids)
                logger.info(f"Deleted {len(doc_ids)} documents by metadata filter")
                return len(doc_ids)
            
            return 0
            
        except Exception as e:
            logger.error(f"Error deleting by metadata: {e}")
            raise
    
    async def update(
        self,
        doc_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None
    ) -> bool:
        """
        Update document
        
        Args:
            doc_id: Document ID
            content: New content (optional)
            metadata: New metadata (optional)
            embedding: New embedding (optional)
            
        Returns:
            True if successful
        """
        try:
            update_params = {"ids": [doc_id]}
            
            if content is not None:
                update_params["documents"] = [content]
            
            if metadata is not None:
                update_params["metadatas"] = [metadata]
            
            if embedding is not None:
                update_params["embeddings"] = [embedding]
            
            self.collection.update(**update_params)
            logger.info(f"Updated document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics
        
        Returns:
            Dict with collection stats
        """
        try:
            count = self.collection.count()
            
            # Get collection metadata
            metadata = self.collection.metadata
            
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    async def clear(self) -> bool:
        """
        Clear all documents from collection
        
        Returns:
            True if successful
        """
        try:
            # Delete collection and recreate
            self.client.delete_collection(name=self.collection_name)
            self._initialize_chroma()
            logger.warning(f"Cleared collection '{self.collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False


# Singleton instances per collection
_vector_stores: Dict[str, VectorStoreService] = {}


def get_vector_store(
    collection_name: str = "jarvis_default",
    force_reinit: bool = False
) -> VectorStoreService:
    """
    Get vector store instance (singleton per collection)
    
    Args:
        collection_name: Collection name
        force_reinit: Force re-initialization
        
    Returns:
        VectorStoreService instance
    """
    global _vector_stores
    
    if collection_name not in _vector_stores or force_reinit:
        _vector_stores[collection_name] = VectorStoreService(
            collection_name=collection_name
        )
    
    return _vector_stores[collection_name]
