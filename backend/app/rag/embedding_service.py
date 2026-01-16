"""
Embedding Service

Provides text embedding functionality using multiple backends:
1. OpenAI text-embedding-ada-002 (primary)
2. Local sentence-transformers (fallback)
"""
from typing import List, Dict, Optional
import logging
import os
from enum import Enum

logger = logging.getLogger(__name__)


class EmbeddingProvider(Enum):
    """Embedding provider types"""
    OPENAI = "openai"
    LOCAL = "local"
    DEEPSEEK = "deepseek"  # 备选


class EmbeddingService:
    """
    Text embedding service with multiple provider support
    
    Usage:
        service = EmbeddingService(provider="openai")
        embedding = await service.embed_text("Hello world")
        embeddings = await service.embed_batch(["text1", "text2"])
    """
    
    def __init__(
        self, 
        provider: str = "openai",
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize embedding service
        
        Args:
            provider: "openai", "local", or "deepseek"
            model: Model name (optional, uses default for provider)
            api_key: API key (optional, uses env var)
        """
        self.provider = EmbeddingProvider(provider)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Default models
        self.model = model or self._get_default_model()
        
        # Initialize provider-specific client
        self._initialize_client()
        
        logger.info(f"Initialized EmbeddingService with provider={self.provider.value}, model={self.model}")
    
    def _get_default_model(self) -> str:
        """Get default model for provider"""
        defaults = {
            EmbeddingProvider.OPENAI: "text-embedding-ada-002",
            EmbeddingProvider.LOCAL: "all-MiniLM-L6-v2",  # 轻量级，384维
            EmbeddingProvider.DEEPSEEK: "deepseek-embed",
        }
        return defaults[self.provider]
    
    def _initialize_client(self):
        """Initialize provider-specific client"""
        if self.provider == EmbeddingProvider.OPENAI:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized")
            except ImportError:
                logger.error("OpenAI library not installed. Run: pip install openai")
                raise
                
        elif self.provider == EmbeddingProvider.LOCAL:
            try:
                from sentence_transformers import SentenceTransformer
                self.client = SentenceTransformer(self.model)
                logger.info(f"Local model loaded: {self.model}")
            except ImportError:
                logger.error("sentence-transformers not installed. Run: pip install sentence-transformers")
                raise
                
        elif self.provider == EmbeddingProvider.DEEPSEEK:
            # TODO: Implement DeepSeek embedding API
            logger.warning("DeepSeek embedding not yet implemented, falling back to OpenAI")
            self.provider = EmbeddingProvider.OPENAI
            self._initialize_client()
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for single text
        
        Args:
            text: Input text
            
        Returns:
            List of floats (embedding vector)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return []
        
        try:
            if self.provider == EmbeddingProvider.OPENAI:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=text
                )
                embedding = response.data[0].embedding
                logger.debug(f"Generated OpenAI embedding: dim={len(embedding)}")
                return embedding
                
            elif self.provider == EmbeddingProvider.LOCAL:
                # Sentence-transformers is sync, run in executor
                import asyncio
                loop = asyncio.get_event_loop()
                embedding = await loop.run_in_executor(
                    None, 
                    self.client.encode, 
                    text
                )
                embedding_list = embedding.tolist()
                logger.debug(f"Generated local embedding: dim={len(embedding_list)}")
                return embedding_list
                
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (optimized)
        
        Args:
            texts: List of input texts
            batch_size: Batch size for API calls (default: 100)
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if len(valid_texts) < len(texts):
            logger.warning(f"Filtered out {len(texts) - len(valid_texts)} empty texts")
        
        try:
            if self.provider == EmbeddingProvider.OPENAI:
                # OpenAI supports batch up to 2048 texts
                all_embeddings = []
                for i in range(0, len(valid_texts), batch_size):
                    batch = valid_texts[i:i + batch_size]
                    response = await self.client.embeddings.create(
                        model=self.model,
                        input=batch
                    )
                    batch_embeddings = [item.embedding for item in response.data]
                    all_embeddings.extend(batch_embeddings)
                    logger.debug(f"Generated batch {i//batch_size + 1}: {len(batch)} texts")
                
                logger.info(f"Generated {len(all_embeddings)} OpenAI embeddings")
                return all_embeddings
                
            elif self.provider == EmbeddingProvider.LOCAL:
                import asyncio
                loop = asyncio.get_event_loop()
                embeddings = await loop.run_in_executor(
                    None,
                    self.client.encode,
                    valid_texts,
                    batch_size
                )
                embeddings_list = [emb.tolist() for emb in embeddings]
                logger.info(f"Generated {len(embeddings_list)} local embeddings")
                return embeddings_list
                
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def get_model_info(self) -> Dict:
        """
        Get embedding model information
        
        Returns:
            Dict with model details
        """
        info = {
            "provider": self.provider.value,
            "model": self.model,
        }
        
        if self.provider == EmbeddingProvider.OPENAI:
            info["dimension"] = 1536  # text-embedding-ada-002
            info["max_tokens"] = 8191
            
        elif self.provider == EmbeddingProvider.LOCAL:
            if hasattr(self.client, "get_sentence_embedding_dimension"):
                info["dimension"] = self.client.get_sentence_embedding_dimension()
            else:
                # For all-MiniLM-L6-v2
                info["dimension"] = 384
            info["max_tokens"] = 256
        
        return info
    
    def get_embedding_dimension(self) -> int:
        """Get dimension of embedding vectors"""
        return self.get_model_info()["dimension"]


# Singleton instance (lazy initialization)
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(
    provider: str = "openai",
    force_reinit: bool = False
) -> EmbeddingService:
    """
    Get singleton embedding service instance
    
    Args:
        provider: Embedding provider
        force_reinit: Force re-initialization
        
    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    
    if _embedding_service is None or force_reinit:
        _embedding_service = EmbeddingService(provider=provider)
    
    return _embedding_service
