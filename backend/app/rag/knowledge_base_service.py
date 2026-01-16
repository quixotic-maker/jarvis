"""
知识库管理服务
提供知识库的创建、管理、导入、导出等完整功能
"""
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
import logging
import json
import asyncio

from .document_processor import get_document_processor, DocumentProcessor
from .vector_store import get_vector_store, VectorStoreService, Document
from .embedding_service import get_embedding_service, EmbeddingService
from .retrieval_service import get_retrieval_service, RetrievalService, RetrievalMode

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """知识库数据模型"""
    
    def __init__(
        self,
        name: str,
        description: str = "",
        collection_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.description = description
        self.collection_name = collection_name or name.lower().replace(" ", "_")
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "collection_name": self.collection_name,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class KnowledgeBaseService:
    """知识库管理服务 - 提供完整的知识库生命周期管理"""
    
    def __init__(
        self,
        kb_name: str = "default",
        description: str = "",
        chunk_size: int = 800,
        chunk_overlap: int = 150
    ):
        """
        初始化知识库服务
        
        Args:
            kb_name: 知识库名称
            description: 知识库描述
            chunk_size: 文档分块大小
            chunk_overlap: 分块重叠大小
        """
        self.kb_name = kb_name
        self.description = description
        self.collection_name = kb_name.lower().replace(" ", "_")
        
        # 初始化各个服务
        self.document_processor = get_document_processor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.vector_store = get_vector_store(self.collection_name)
        self.embedding_service = get_embedding_service()
        self.retrieval_service = get_retrieval_service(self.collection_name)
        
        # 知识库元数据
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap
        }
        
        logger.info(
            f"KnowledgeBaseService初始化: kb='{kb_name}', "
            f"collection='{self.collection_name}'"
        )
    
    async def add_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        添加单个文档到知识库
        
        Args:
            file_path: 文件路径
            metadata: 额外元数据
            
        Returns:
            List[str]: 添加的文档ID列表
        """
        logger.info(f"添加文档到知识库: {file_path}")
        
        # 1. 处理文档（加载+分块）
        documents = self.document_processor.process_file(file_path, metadata)
        
        if not documents:
            logger.warning(f"文档处理失败: {file_path}")
            return []
        
        # 2. 生成embeddings
        contents = [doc.content for doc in documents]
        embeddings = await self.embedding_service.embed_batch(contents)
        
        # 3. 添加embeddings到documents
        for doc, embedding in zip(documents, embeddings):
            doc.embedding = embedding
        
        # 4. 存入向量数据库
        doc_ids = await self.vector_store.add_documents(documents)
        
        logger.info(f"成功添加 {len(doc_ids)} 个文档块")
        return doc_ids
    
    async def add_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        添加纯文本到知识库
        
        Args:
            text: 文本内容
            metadata: 元数据
            
        Returns:
            List[str]: 文档ID列表
        """
        logger.info(f"添加文本到知识库: {len(text)} 字符")
        
        # 处理文本
        documents = self.document_processor.process_text(text, metadata)
        
        if not documents:
            return []
        
        # 生成embeddings
        contents = [doc.content for doc in documents]
        embeddings = await self.embedding_service.embed_batch(contents)
        
        for doc, embedding in zip(documents, embeddings):
            doc.embedding = embedding
        
        # 存储
        doc_ids = await self.vector_store.add_documents(documents)
        
        logger.info(f"成功添加 {len(doc_ids)} 个文本块")
        return doc_ids
    
    async def add_directory(
        self,
        directory_path: str,
        recursive: bool = True,
        file_patterns: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        批量添加目录中的文档
        
        Args:
            directory_path: 目录路径
            recursive: 是否递归
            file_patterns: 文件匹配模式
            metadata: 额外元数据
            
        Returns:
            Dict: 导入统计信息
        """
        logger.info(f"批量导入目录: {directory_path}")
        
        start_time = datetime.now()
        
        # 1. 处理所有文档
        documents = self.document_processor.process_directory(
            directory_path,
            recursive=recursive,
            file_patterns=file_patterns,
            additional_metadata=metadata
        )
        
        if not documents:
            logger.warning("没有找到可处理的文档")
            return {
                "success": False,
                "total_files": 0,
                "total_chunks": 0,
                "failed_files": 0
            }
        
        # 2. 批量生成embeddings
        logger.info(f"为 {len(documents)} 个文档块生成embeddings...")
        contents = [doc.content for doc in documents]
        embeddings = await self.embedding_service.embed_batch(contents, batch_size=50)
        
        for doc, embedding in zip(documents, embeddings):
            doc.embedding = embedding
        
        # 3. 批量存储
        logger.info("存储到向量数据库...")
        doc_ids = await self.vector_store.add_documents(documents)
        
        # 4. 统计信息
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # 统计文件数（从元数据中）
        unique_files = set()
        for doc in documents:
            file_name = doc.metadata.get('file_name')
            if file_name:
                unique_files.add(file_name)
        
        stats = {
            "success": True,
            "total_files": len(unique_files),
            "total_chunks": len(doc_ids),
            "elapsed_seconds": elapsed,
            "chunks_per_second": len(doc_ids) / elapsed if elapsed > 0 else 0
        }
        
        logger.info(f"批量导入完成: {stats}")
        return stats
    
    async def delete_document(self, doc_id: str) -> bool:
        """
        删除文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            bool: 是否成功
        """
        count = await self.vector_store.delete([doc_id])
        return count > 0
    
    async def delete_by_metadata(
        self,
        filter_metadata: Dict[str, Any]
    ) -> int:
        """
        根据元数据删除文档
        
        Args:
            filter_metadata: 元数据过滤条件
            
        Returns:
            int: 删除的文档数量
        """
        # 先使用get获取符合条件的文档ID
        try:
            results = self.vector_store.collection.get(
                where=filter_metadata,
                limit=10000,  # 获取所有匹配的
                include=[]  # 只需要ID
            )
            doc_ids = results.get("ids", [])
        except Exception as e:
            logger.error(f"查找文档失败: {e}")
            doc_ids = []
        
        if not doc_ids:
            logger.info("没有找到符合条件的文档")
            return 0
        
        # 批量删除
        count = await self.vector_store.delete(doc_ids)
        logger.info(f"删除了 {count} 个文档")
        return count
    
    async def update_document(
        self,
        doc_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新文档
        
        Args:
            doc_id: 文档ID
            content: 新内容
            metadata: 新元数据
            
        Returns:
            bool: 是否成功
        """
        # 如果更新内容，需要重新生成embedding
        new_embedding = None
        if content is not None:
            new_embedding = await self.embedding_service.embed_text(content)
        
        # 更新
        success = await self.vector_store.update(
            doc_id=doc_id,
            content=content,
            metadata=metadata,
            embedding=new_embedding
        )
        
        return success
    
    async def search(
        self,
        query: str,
        mode: RetrievalMode = RetrievalMode.HYBRID,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.0
    ) -> List[Any]:
        """
        搜索知识库
        
        Args:
            query: 查询文本
            mode: 检索模式
            k: 返回数量
            filter_metadata: 元数据过滤
            score_threshold: 分数阈值
            
        Returns:
            List[RetrievalResult]: 检索结果
        """
        results = await self.retrieval_service.retrieve(
            query=query,
            mode=mode,
            k=k,
            filter_metadata=filter_metadata,
            score_threshold=score_threshold
        )
        return results
    
    async def get_context(
        self,
        query: str,
        k: int = 3,
        max_length: int = 2000
    ) -> Tuple[List[Any], str]:
        """
        获取查询的上下文（用于Agent）
        
        Args:
            query: 查询文本
            k: 返回结果数
            max_length: 最大上下文长度
            
        Returns:
            Tuple[List, str]: (检索结果, 格式化上下文)
        """
        results, context = await self.retrieval_service.retrieve_with_context(
            query=query,
            mode=RetrievalMode.HYBRID,
            k=k,
            max_context_length=max_length
        )
        return results, context
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            Dict: 统计信息
        """
        vector_stats = await self.vector_store.get_stats()
        
        stats = {
            "kb_name": self.kb_name,
            "description": self.description,
            "collection_name": self.collection_name,
            "document_count": vector_stats.get("document_count", 0),
            "metadata": self.metadata,
            "vector_store": vector_stats
        }
        
        return stats
    
    async def clear(self) -> bool:
        """
        清空知识库
        
        Returns:
            bool: 是否成功
        """
        logger.warning(f"清空知识库: {self.kb_name}")
        success = await self.vector_store.clear()
        return success
    
    async def export_to_json(
        self,
        output_path: str,
        include_embeddings: bool = False
    ) -> Dict[str, Any]:
        """
        导出知识库为JSON
        
        Args:
            output_path: 输出文件路径
            include_embeddings: 是否包含embeddings
            
        Returns:
            Dict: 导出统计
        """
        logger.info(f"导出知识库到: {output_path}")
        
        # 获取所有文档（使用get方法）
        try:
            results = self.vector_store.collection.get(
                limit=100000,  # 大数量
                include=["documents", "metadatas", "embeddings"] if include_embeddings else ["documents", "metadatas"]
            )
            
            all_docs = []
            if results and results.get("documents"):
                for i in range(len(results["ids"])):
                    doc_data = {
                        "id": results["ids"][i],
                        "content": results["documents"][i],
                        "metadata": results.get("metadatas", [])[i] if results.get("metadatas") else {}
                    }
                    if include_embeddings and results.get("embeddings"):
                        doc_data["embedding"] = results["embeddings"][i]
                    all_docs.append(doc_data)
        except Exception as e:
            logger.error(f"获取文档失败: {e}")
            all_docs = []
        
        # 构建导出数据
        export_data = {
            "kb_name": self.kb_name,
            "description": self.description,
            "exported_at": datetime.now().isoformat(),
            "document_count": len(all_docs),
            "documents": all_docs  # 直接使用构建好的文档列表
        }
        
        # 写入文件
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        stats = {
            "success": True,
            "output_path": str(output_file),
            "document_count": len(all_docs),
            "file_size_bytes": output_file.stat().st_size
        }
        
        logger.info(f"导出完成: {stats}")
        return stats
    
    async def import_from_json(
        self,
        input_path: str,
        clear_existing: bool = False
    ) -> Dict[str, Any]:
        """
        从JSON导入知识库
        
        Args:
            input_path: 输入文件路径
            clear_existing: 是否清空现有数据
            
        Returns:
            Dict: 导入统计
        """
        logger.info(f"从JSON导入知识库: {input_path}")
        
        # 清空现有数据
        if clear_existing:
            await self.clear()
        
        # 读取JSON
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        documents_data = data.get("documents", [])
        
        # 构建Document对象
        documents = []
        for doc_data in documents_data:
            doc = Document(
                content=doc_data["content"],
                metadata=doc_data.get("metadata", {}),
                doc_id=doc_data.get("id"),
                embedding=doc_data.get("embedding")
            )
            documents.append(doc)
        
        # 如果没有embeddings，生成它们
        docs_without_embedding = [doc for doc in documents if doc.embedding is None]
        if docs_without_embedding:
            logger.info(f"为 {len(docs_without_embedding)} 个文档生成embeddings...")
            contents = [doc.content for doc in docs_without_embedding]
            embeddings = await self.embedding_service.embed_batch(contents)
            
            for doc, embedding in zip(docs_without_embedding, embeddings):
                doc.embedding = embedding
        
        # 批量添加
        doc_ids = await self.vector_store.add_documents(documents)
        
        stats = {
            "success": True,
            "imported_count": len(doc_ids),
            "source_file": input_path
        }
        
        logger.info(f"导入完成: {stats}")
        return stats
    
    async def list_documents(
        self,
        filter_metadata: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        列出知识库中的文档
        
        Args:
            filter_metadata: 元数据过滤
            limit: 返回数量限制
            
        Returns:
            List[Dict]: 文档信息列表
        """
        # 使用get方法获取文档（不需要查询向量）
        try:
            get_params = {"limit": limit}
            if filter_metadata:
                get_params["where"] = filter_metadata
            
            results = self.vector_store.collection.get(**get_params)
            
            docs_info = []
            if results and results.get("documents"):
                for i, (doc_id, content, metadata) in enumerate(zip(
                    results["ids"],
                    results["documents"],
                    results.get("metadatas", [{}] * len(results["ids"]))
                )):
                    info = {
                        "id": doc_id,
                        "content_preview": content[:100] + "..." if len(content) > 100 else content,
                        "content_length": len(content),
                        "metadata": metadata or {}
                    }
                    docs_info.append(info)
            
            return docs_info
        except Exception as e:
            logger.error(f"列出文档失败: {e}")
            return []


# 单例管理
_knowledge_bases: Dict[str, KnowledgeBaseService] = {}


def get_knowledge_base(
    kb_name: str = "default",
    description: str = "",
    chunk_size: int = 800,
    chunk_overlap: int = 150
) -> KnowledgeBaseService:
    """
    获取或创建知识库实例
    
    Args:
        kb_name: 知识库名称
        description: 描述
        chunk_size: 分块大小
        chunk_overlap: 重叠大小
        
    Returns:
        KnowledgeBaseService: 知识库服务实例
    """
    global _knowledge_bases
    
    if kb_name not in _knowledge_bases:
        _knowledge_bases[kb_name] = KnowledgeBaseService(
            kb_name=kb_name,
            description=description,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    return _knowledge_bases[kb_name]


def list_knowledge_bases() -> List[str]:
    """
    列出所有已创建的知识库
    
    Returns:
        List[str]: 知识库名称列表
    """
    return list(_knowledge_bases.keys())

