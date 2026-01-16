"""
RAG文本分块服务
提供智能文本分块功能，支持多种分块策略
"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """文本块数据模型"""
    text: str                      # 块文本内容
    start_index: int               # 在原文中的起始位置
    end_index: int                 # 在原文中的结束位置
    metadata: Dict[str, Any]       # 块元数据
    chunk_id: Optional[str] = None # 块ID（可选）


class ChunkingStrategy:
    """分块策略枚举"""
    FIXED_SIZE = "fixed_size"           # 固定大小分块
    SENTENCE = "sentence"               # 按句子分块
    PARAGRAPH = "paragraph"             # 按段落分块
    SEMANTIC = "semantic"               # 语义分块（待实现）
    CODE = "code"                       # 代码结构分块


class ChunkingService:
    """文本分块服务"""
    
    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
        strategy: str = ChunkingStrategy.FIXED_SIZE
    ):
        """
        初始化分块服务
        
        Args:
            chunk_size: 目标块大小（字符数）
            chunk_overlap: 块之间的重叠字符数
            strategy: 分块策略
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
        
        # 句子分隔符（支持中英文）
        self.sentence_delimiters = r'[。！？!?.;；\n]+'
        # 段落分隔符
        self.paragraph_delimiters = r'\n\s*\n'
        
        logger.info(
            f"ChunkingService初始化: chunk_size={chunk_size}, "
            f"overlap={chunk_overlap}, strategy={strategy}"
        )
    
    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        将文本分块
        
        Args:
            text: 要分块的文本
            metadata: 附加元数据
            
        Returns:
            List[Chunk]: 文本块列表
        """
        if not text or not text.strip():
            logger.warning("空文本，返回空列表")
            return []
        
        # 根据策略选择分块方法
        if self.strategy == ChunkingStrategy.SENTENCE:
            return self._chunk_by_sentence(text, metadata)
        elif self.strategy == ChunkingStrategy.PARAGRAPH:
            return self._chunk_by_paragraph(text, metadata)
        elif self.strategy == ChunkingStrategy.CODE:
            return self._chunk_code(text, metadata)
        else:  # FIXED_SIZE
            return self._chunk_fixed_size(text, metadata)
    
    def _chunk_fixed_size(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        固定大小分块（带重叠）
        
        Args:
            text: 源文本
            metadata: 元数据
            
        Returns:
            List[Chunk]: 文本块列表
        """
        chunks = []
        text_length = len(text)
        start = 0
        chunk_index = 0
        
        while start < text_length:
            # 计算结束位置
            end = min(start + self.chunk_size, text_length)
            
            # 如果不是最后一块，尝试在句子边界处分割
            if end < text_length:
                # 在附近寻找句子结束符
                search_start = max(start + self.chunk_size - 100, start)
                search_text = text[search_start:min(end + 100, text_length)]
                
                # 查找句子分隔符
                matches = list(re.finditer(self.sentence_delimiters, search_text))
                if matches:
                    # 找到最接近目标位置的分隔符
                    target_pos = self.chunk_size - (search_start - start)
                    best_match = min(
                        matches,
                        key=lambda m: abs(m.start() - target_pos)
                    )
                    end = search_start + best_match.end()
            
            # 提取块文本
            chunk_text = text[start:end].strip()
            
            if chunk_text:  # 只添加非空块
                chunk_metadata = {
                    "chunk_index": chunk_index,
                    "chunk_size": len(chunk_text),
                    "strategy": self.strategy
                }
                if metadata:
                    chunk_metadata.update(metadata)
                
                chunks.append(Chunk(
                    text=chunk_text,
                    start_index=start,
                    end_index=end,
                    metadata=chunk_metadata
                ))
                chunk_index += 1
            
            # 移动到下一个块（考虑重叠）
            start = end - self.chunk_overlap
            
            # 如果剩余文本太短，直接跳到末尾
            if text_length - start < self.chunk_size // 2:
                start = text_length
        
        logger.info(f"固定大小分块完成: {len(chunks)}个块")
        return chunks
    
    def _chunk_by_sentence(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        按句子分块（每个块包含多个句子）
        
        Args:
            text: 源文本
            metadata: 元数据
            
        Returns:
            List[Chunk]: 文本块列表
        """
        # 分割句子
        sentences = re.split(self.sentence_delimiters, text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for i, sentence in enumerate(sentences):
            sentence_length = len(sentence)
            
            # 如果当前块加上新句子超过大小限制
            if current_size + sentence_length > self.chunk_size and current_chunk:
                # 创建当前块
                chunk_text = ' '.join(current_chunk)
                chunk_metadata = {
                    "chunk_index": chunk_index,
                    "sentence_count": len(current_chunk),
                    "strategy": self.strategy
                }
                if metadata:
                    chunk_metadata.update(metadata)
                
                # 计算在原文中的位置（近似）
                start_idx = text.find(current_chunk[0])
                end_idx = start_idx + len(chunk_text)
                
                chunks.append(Chunk(
                    text=chunk_text,
                    start_index=start_idx,
                    end_index=end_idx,
                    metadata=chunk_metadata
                ))
                
                chunk_index += 1
                
                # 保留重叠句子
                overlap_size = 0
                overlap_sentences = []
                for sent in reversed(current_chunk):
                    if overlap_size + len(sent) < self.chunk_overlap:
                        overlap_sentences.insert(0, sent)
                        overlap_size += len(sent)
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_size = overlap_size
            
            # 添加当前句子
            current_chunk.append(sentence)
            current_size += sentence_length
        
        # 处理最后一个块
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunk_metadata = {
                "chunk_index": chunk_index,
                "sentence_count": len(current_chunk),
                "strategy": self.strategy
            }
            if metadata:
                chunk_metadata.update(metadata)
            
            start_idx = text.find(current_chunk[0])
            end_idx = start_idx + len(chunk_text)
            
            chunks.append(Chunk(
                text=chunk_text,
                start_index=start_idx,
                end_index=end_idx,
                metadata=chunk_metadata
            ))
        
        logger.info(f"句子分块完成: {len(chunks)}个块, {len(sentences)}个句子")
        return chunks
    
    def _chunk_by_paragraph(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        按段落分块
        
        Args:
            text: 源文本
            metadata: 元数据
            
        Returns:
            List[Chunk]: 文本块列表
        """
        # 分割段落
        paragraphs = re.split(self.paragraph_delimiters, text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for paragraph in paragraphs:
            para_length = len(paragraph)
            
            # 如果单个段落就超过大小，需要进一步分块
            if para_length > self.chunk_size:
                # 如果有累积的块，先保存
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    chunks.append(self._create_chunk(
                        chunk_text, text, chunk_index, metadata, "paragraph"
                    ))
                    chunk_index += 1
                    current_chunk = []
                    current_size = 0
                
                # 对大段落使用固定大小分块
                sub_chunks = self._chunk_fixed_size(paragraph, metadata)
                for sub_chunk in sub_chunks:
                    sub_chunk.metadata["chunk_index"] = chunk_index
                    chunks.append(sub_chunk)
                    chunk_index += 1
                continue
            
            # 检查是否超过大小限制
            if current_size + para_length > self.chunk_size and current_chunk:
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append(self._create_chunk(
                    chunk_text, text, chunk_index, metadata, "paragraph"
                ))
                chunk_index += 1
                current_chunk = []
                current_size = 0
            
            current_chunk.append(paragraph)
            current_size += para_length
        
        # 处理最后一个块
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append(self._create_chunk(
                chunk_text, text, chunk_index, metadata, "paragraph"
            ))
        
        logger.info(f"段落分块完成: {len(chunks)}个块, {len(paragraphs)}个段落")
        return chunks
    
    def _chunk_code(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        代码结构分块（按函数/类分割）
        
        Args:
            text: 源代码
            metadata: 元数据
            
        Returns:
            List[Chunk]: 代码块列表
        """
        chunks = []
        lines = text.split('\n')
        
        current_chunk = []
        current_size = 0
        chunk_index = 0
        indent_level = 0
        
        # 检测函数/类定义的正则
        func_class_pattern = r'^\s*(def|class|function|const|let|var)\s+\w+'
        
        for i, line in enumerate(lines):
            line_length = len(line)
            
            # 检测是否是新的函数/类定义
            is_definition = re.match(func_class_pattern, line)
            
            # 如果是新定义且当前块不为空
            if is_definition and current_chunk and current_size > self.chunk_size // 2:
                chunk_text = '\n'.join(current_chunk)
                chunks.append(self._create_chunk(
                    chunk_text, text, chunk_index, metadata, "code"
                ))
                chunk_index += 1
                current_chunk = []
                current_size = 0
            
            # 如果当前块太大
            if current_size + line_length > self.chunk_size and current_chunk:
                chunk_text = '\n'.join(current_chunk)
                chunks.append(self._create_chunk(
                    chunk_text, text, chunk_index, metadata, "code"
                ))
                chunk_index += 1
                current_chunk = []
                current_size = 0
            
            current_chunk.append(line)
            current_size += line_length
        
        # 处理最后一个块
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunks.append(self._create_chunk(
                chunk_text, text, chunk_index, metadata, "code"
            ))
        
        logger.info(f"代码分块完成: {len(chunks)}个块")
        return chunks
    
    def _create_chunk(
        self,
        chunk_text: str,
        original_text: str,
        chunk_index: int,
        metadata: Optional[Dict[str, Any]],
        strategy: str
    ) -> Chunk:
        """创建Chunk对象的辅助方法"""
        chunk_metadata = {
            "chunk_index": chunk_index,
            "chunk_size": len(chunk_text),
            "strategy": strategy
        }
        if metadata:
            chunk_metadata.update(metadata)
        
        # 尝试找到在原文中的位置
        start_idx = original_text.find(chunk_text[:100])  # 用前100个字符定位
        if start_idx == -1:
            start_idx = 0
        end_idx = start_idx + len(chunk_text)
        
        return Chunk(
            text=chunk_text,
            start_index=start_idx,
            end_index=end_idx,
            metadata=chunk_metadata
        )


# 单例实例
_chunking_service: Optional[ChunkingService] = None


def get_chunking_service(
    chunk_size: int = 800,
    chunk_overlap: int = 150,
    strategy: str = ChunkingStrategy.FIXED_SIZE
) -> ChunkingService:
    """
    获取分块服务单例
    
    Args:
        chunk_size: 块大小
        chunk_overlap: 重叠大小
        strategy: 分块策略
        
    Returns:
        ChunkingService: 分块服务实例
    """
    global _chunking_service
    if _chunking_service is None:
        _chunking_service = ChunkingService(chunk_size, chunk_overlap, strategy)
    return _chunking_service
