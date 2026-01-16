"""
RAG文档处理器
整合文档加载、分块、元数据提取等功能
"""
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import logging

from .chunking import ChunkingService, Chunk, ChunkingStrategy, get_chunking_service
from .loaders import LoaderFactory, get_loader_factory
from .vector_store import Document

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """文档处理器 - RAG系统的文档处理核心"""
    
    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
        chunking_strategy: str = ChunkingStrategy.FIXED_SIZE
    ):
        """
        初始化文档处理器
        
        Args:
            chunk_size: 块大小
            chunk_overlap: 块重叠大小
            chunking_strategy: 分块策略
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunking_strategy = chunking_strategy
        
        # 初始化服务
        self.chunking_service = get_chunking_service(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy=chunking_strategy
        )
        self.loader_factory = get_loader_factory()
        
        logger.info(
            f"DocumentProcessor初始化: chunk_size={chunk_size}, "
            f"overlap={chunk_overlap}, strategy={chunking_strategy}"
        )
    
    def process_file(
        self,
        file_path: str,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        处理单个文件：加载 -> 分块 -> 生成Document对象
        
        Args:
            file_path: 文件路径
            additional_metadata: 额外的元数据
            
        Returns:
            List[Document]: Document对象列表
        """
        logger.info(f"开始处理文件: {file_path}")
        
        # 1. 加载文档
        doc_data = self.loader_factory.load_document(file_path)
        if doc_data is None:
            logger.error(f"文件加载失败: {file_path}")
            return []
        
        content = doc_data["content"]
        file_metadata = doc_data["metadata"]
        
        # 合并额外元数据
        if additional_metadata:
            file_metadata.update(additional_metadata)
        
        # 2. 根据文件类型选择分块策略
        file_ext = Path(file_path).suffix.lower()
        strategy = self._select_strategy(file_ext)
        
        # 如果策略不同，重新创建分块服务
        if strategy != self.chunking_strategy:
            chunking_service = ChunkingService(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                strategy=strategy
            )
        else:
            chunking_service = self.chunking_service
        
        # 3. 分块
        chunks = chunking_service.chunk_text(content, file_metadata)
        logger.info(f"文档分块完成: {len(chunks)} 个块")
        
        # 4. 转换为Document对象
        documents = []
        for chunk in chunks:
            # 生成文档ID
            chunk_index = chunk.metadata.get("chunk_index", 0)
            doc_id = f"{Path(file_path).stem}_{chunk_index}"
            
            # 创建Document (使用doc_id参数而不是id)
            doc = Document(
                content=chunk.text,
                metadata=chunk.metadata,
                doc_id=doc_id,
                embedding=None  # 稍后由向量服务生成
            )
            documents.append(doc)
        
        logger.info(f"文件处理完成: {file_path} -> {len(documents)} 个文档")
        return documents
    
    def process_directory(
        self,
        directory_path: str,
        recursive: bool = True,
        file_patterns: Optional[List[str]] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        处理目录中的所有文件
        
        Args:
            directory_path: 目录路径
            recursive: 是否递归处理子目录
            file_patterns: 文件匹配模式列表（如 ['*.md', '*.txt']）
            additional_metadata: 额外元数据
            
        Returns:
            List[Document]: 所有文档列表
        """
        dir_path = Path(directory_path)
        
        if not dir_path.exists() or not dir_path.is_dir():
            logger.error(f"目录不存在或不是目录: {directory_path}")
            return []
        
        logger.info(f"开始处理目录: {directory_path} (recursive={recursive})")
        
        # 收集所有文件
        files = []
        if recursive:
            files = list(dir_path.rglob('*'))
        else:
            files = list(dir_path.glob('*'))
        
        # 过滤出文件（排除目录）
        files = [f for f in files if f.is_file()]
        
        # 应用文件模式过滤
        if file_patterns:
            filtered_files = []
            for pattern in file_patterns:
                filtered_files.extend([f for f in files if f.match(pattern)])
            files = list(set(filtered_files))  # 去重
        
        logger.info(f"找到 {len(files)} 个文件待处理")
        
        # 处理所有文件
        all_documents = []
        success_count = 0
        fail_count = 0
        
        for file_path in files:
            try:
                # 为每个文件添加目录元数据
                file_metadata = {
                    "source_directory": str(dir_path.absolute()),
                    "relative_path": str(file_path.relative_to(dir_path))
                }
                if additional_metadata:
                    file_metadata.update(additional_metadata)
                
                documents = self.process_file(str(file_path), file_metadata)
                all_documents.extend(documents)
                success_count += 1
                
            except Exception as e:
                logger.error(f"文件处理失败 {file_path}: {e}")
                fail_count += 1
        
        logger.info(
            f"目录处理完成: 成功 {success_count} 个, 失败 {fail_count} 个, "
            f"总计 {len(all_documents)} 个文档"
        )
        
        return all_documents
    
    def process_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        处理纯文本（不从文件加载）
        
        Args:
            text: 文本内容
            metadata: 元数据
            
        Returns:
            List[Document]: Document列表
        """
        if not text or not text.strip():
            logger.warning("空文本，返回空列表")
            return []
        
        # 分块
        base_metadata = {
            "source": "text_input",
            "character_count": len(text),
            "line_count": text.count('\n') + 1
        }
        if metadata:
            base_metadata.update(metadata)
        
        chunks = self.chunking_service.chunk_text(text, base_metadata)
        
        # 转换为Document
        import time
        timestamp = int(time.time() * 1000000)  # 微秒级时间戳
        documents = []
        for chunk in chunks:
            chunk_index = chunk.metadata.get("chunk_index", 0)
            doc_id = f"text_{timestamp}_{chunk_index}"
            
            doc = Document(
                content=chunk.text,
                metadata=chunk.metadata,
                doc_id=doc_id,
                embedding=None
            )
            documents.append(doc)
        
        logger.info(f"文本处理完成: {len(documents)} 个文档")
        return documents
    
    def _select_strategy(self, file_extension: str) -> str:
        """
        根据文件类型选择分块策略
        
        Args:
            file_extension: 文件扩展名
            
        Returns:
            str: 分块策略
        """
        # 代码文件使用代码策略
        code_extensions = [
            '.py', '.js', '.ts', '.jsx', '.tsx',
            '.java', '.cpp', '.c', '.h', '.go', '.rs'
        ]
        if file_extension in code_extensions:
            return ChunkingStrategy.CODE
        
        # Markdown使用段落策略
        if file_extension in ['.md', '.markdown']:
            return ChunkingStrategy.PARAGRAPH
        
        # 其他使用固定大小策略
        return ChunkingStrategy.FIXED_SIZE
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取处理器统计信息
        
        Returns:
            Dict: 统计信息
        """
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "chunking_strategy": self.chunking_strategy
        }


# 单例实例
_document_processor: Optional[DocumentProcessor] = None


def get_document_processor(
    chunk_size: int = 800,
    chunk_overlap: int = 150,
    chunking_strategy: str = ChunkingStrategy.FIXED_SIZE
) -> DocumentProcessor:
    """
    获取文档处理器单例
    
    Args:
        chunk_size: 块大小
        chunk_overlap: 重叠大小
        chunking_strategy: 分块策略
        
    Returns:
        DocumentProcessor: 处理器实例
    """
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            chunking_strategy=chunking_strategy
        )
    return _document_processor
