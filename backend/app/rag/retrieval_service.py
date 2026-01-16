"""
RAG检索服务
提供智能文档检索功能，支持语义搜索、关键词搜索和混合检索
"""
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import logging
import re
from dataclasses import dataclass

from .embedding_service import get_embedding_service
from .vector_store import get_vector_store, Document, SearchResult

logger = logging.getLogger(__name__)


class RetrievalMode(str, Enum):
    """检索模式"""
    SEMANTIC = "semantic"           # 纯语义搜索
    KEYWORD = "keyword"             # 纯关键词搜索
    HYBRID = "hybrid"               # 混合检索
    RERANK = "rerank"              # 语义搜索 + 重排序


@dataclass
class RetrievalResult:
    """检索结果"""
    document: Document
    score: float                    # 相关性分数 (0-1)
    rank: int                       # 排名
    retrieval_mode: str             # 检索模式
    metadata: Dict[str, Any]        # 额外元数据
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "document": self.document.to_dict(),
            "score": self.score,
            "rank": self.rank,
            "retrieval_mode": self.retrieval_mode,
            "metadata": self.metadata
        }


class RetrievalService:
    """检索服务 - RAG系统的核心检索引擎"""
    
    def __init__(
        self,
        collection_name: str = "default",
        default_k: int = 5,
        score_threshold: float = 0.0,
        enable_rerank: bool = True
    ):
        """
        初始化检索服务
        
        Args:
            collection_name: 向量集合名称
            default_k: 默认返回结果数量
            score_threshold: 分数阈值（低于此分数的结果会被过滤）
            enable_rerank: 是否启用重排序
        """
        self.collection_name = collection_name
        self.default_k = default_k
        self.score_threshold = score_threshold
        self.enable_rerank = enable_rerank
        
        # 初始化服务
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store(collection_name)
        
        logger.info(
            f"RetrievalService初始化: collection={collection_name}, "
            f"k={default_k}, threshold={score_threshold}"
        )
    
    async def retrieve(
        self,
        query: str,
        mode: RetrievalMode = RetrievalMode.HYBRID,
        k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[RetrievalResult]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            mode: 检索模式
            k: 返回结果数量
            filter_metadata: 元数据过滤条件
            score_threshold: 分数阈值
            
        Returns:
            List[RetrievalResult]: 检索结果列表
        """
        k = k or self.default_k
        score_threshold = score_threshold or self.score_threshold
        
        logger.info(f"开始检索: query='{query[:50]}...', mode={mode}, k={k}")
        
        # 根据模式选择检索方法
        if mode == RetrievalMode.SEMANTIC:
            results = await self._semantic_search(
                query, k, filter_metadata, score_threshold
            )
        elif mode == RetrievalMode.KEYWORD:
            results = await self._keyword_search(
                query, k, filter_metadata, score_threshold
            )
        elif mode == RetrievalMode.HYBRID:
            results = await self._hybrid_search(
                query, k, filter_metadata, score_threshold
            )
        elif mode == RetrievalMode.RERANK:
            results = await self._semantic_search_with_rerank(
                query, k * 2, filter_metadata, score_threshold
            )
            results = results[:k]  # 取top-k
        else:
            raise ValueError(f"不支持的检索模式: {mode}")
        
        logger.info(f"检索完成: 返回 {len(results)} 个结果")
        return results
    
    async def _semantic_search(
        self,
        query: str,
        k: int,
        filter_metadata: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.0
    ) -> List[RetrievalResult]:
        """
        语义搜索
        
        Args:
            query: 查询文本
            k: 返回数量
            filter_metadata: 元数据过滤
            score_threshold: 分数阈值
            
        Returns:
            List[RetrievalResult]: 检索结果
        """
        # 1. 生成查询向量
        query_embedding = await self.embedding_service.embed_text(query)
        
        # 2. 向量搜索
        search_results = await self.vector_store.search_with_embedding(
            embedding=query_embedding,
            k=k,
            filter_metadata=filter_metadata
        )
        
        # 3. 转换为RetrievalResult并过滤分数
        results = []
        for i, result in enumerate(search_results):
            # 只保留分数高于阈值的结果
            if result.score >= score_threshold:
                retrieval_result = RetrievalResult(
                    document=result.document,
                    score=result.score,
                    rank=i + 1,
                    retrieval_mode=RetrievalMode.SEMANTIC,
                    metadata={
                        "search_type": "vector",
                        "original_rank": result.rank
                    }
                )
                results.append(retrieval_result)
        
        logger.info(f"语义搜索完成: 返回 {len(results)} 个结果 (阈值={score_threshold})")
        return results
    
    async def _keyword_search(
        self,
        query: str,
        k: int,
        filter_metadata: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.0
    ) -> List[RetrievalResult]:
        """
        关键词搜索（基于BM25算法的简化版）
        
        Args:
            query: 查询文本
            k: 返回数量
            filter_metadata: 元数据过滤
            score_threshold: 分数阈值
            
        Returns:
            List[RetrievalResult]: 检索结果
        """
        # 1. 提取关键词
        keywords = self._extract_keywords(query)
        
        # 2. 获取所有文档（如果有元数据过滤，先过滤）
        # 注意：这里简化实现，实际应该有专门的关键词索引
        all_results = await self.vector_store.search(
            query=query,
            k=100,  # 获取更多候选
            filter_metadata=filter_metadata,
            score_threshold=0.0  # 不使用向量分数
        )
        
        # 3. 计算关键词匹配分数
        scored_results = []
        for result in all_results:
            score = self._calculate_keyword_score(
                query, keywords, result.document.content
            )
            if score >= score_threshold:
                scored_results.append((result, score))
        
        # 4. 按分数排序
        scored_results.sort(key=lambda x: x[1], reverse=True)
        scored_results = scored_results[:k]
        
        # 5. 转换为RetrievalResult
        results = []
        for i, (result, score) in enumerate(scored_results):
            retrieval_result = RetrievalResult(
                document=result.document,
                score=score,
                rank=i + 1,
                retrieval_mode=RetrievalMode.KEYWORD,
                metadata={
                    "search_type": "keyword",
                    "matched_keywords": keywords
                }
            )
            results.append(retrieval_result)
        
        return results
    
    async def _hybrid_search(
        self,
        query: str,
        k: int,
        filter_metadata: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.0
    ) -> List[RetrievalResult]:
        """
        混合搜索（语义 + 关键词）
        
        Args:
            query: 查询文本
            k: 返回数量
            filter_metadata: 元数据过滤
            score_threshold: 分数阈值
            
        Returns:
            List[RetrievalResult]: 检索结果
        """
        # 1. 并行执行语义搜索和关键词搜索
        semantic_results = await self._semantic_search(
            query, k * 2, filter_metadata, 0.0
        )
        keyword_results = await self._keyword_search(
            query, k * 2, filter_metadata, 0.0
        )
        
        # 2. 合并结果（使用Reciprocal Rank Fusion算法）
        merged_results = self._reciprocal_rank_fusion(
            semantic_results, keyword_results, k=60
        )
        
        # 3. 过滤低分结果
        merged_results = [r for r in merged_results if r.score >= score_threshold]
        
        # 4. 取top-k
        merged_results = merged_results[:k]
        
        # 5. 更新检索模式
        for result in merged_results:
            result.retrieval_mode = RetrievalMode.HYBRID
        
        return merged_results
    
    async def _semantic_search_with_rerank(
        self,
        query: str,
        k: int,
        filter_metadata: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.0
    ) -> List[RetrievalResult]:
        """
        语义搜索 + 重排序
        
        Args:
            query: 查询文本
            k: 候选数量（实际返回会更少）
            filter_metadata: 元数据过滤
            score_threshold: 分数阈值
            
        Returns:
            List[RetrievalResult]: 重排序后的结果
        """
        # 1. 语义搜索获取候选
        candidates = await self._semantic_search(
            query, k, filter_metadata, 0.0
        )
        
        # 2. 重排序
        if self.enable_rerank and len(candidates) > 1:
            reranked = self._rerank_results(query, candidates)
        else:
            reranked = candidates
        
        # 3. 过滤低分结果
        reranked = [r for r in reranked if r.score >= score_threshold]
        
        # 4. 更新检索模式和排名
        for i, result in enumerate(reranked):
            result.retrieval_mode = RetrievalMode.RERANK
            result.rank = i + 1
        
        return reranked
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        提取关键词（简化版）
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 关键词列表
        """
        # 移除标点，转小写
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # 分词
        words = text.split()
        
        # 过滤停用词（简化版）
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            '的', '了', '和', '是', '在', '有', '就', '不', '人', '都', '我', '他'
        }
        keywords = [w for w in words if w not in stop_words and len(w) > 1]
        
        return keywords
    
    def _calculate_keyword_score(
        self,
        query: str,
        keywords: List[str],
        content: str
    ) -> float:
        """
        计算关键词匹配分数（简化BM25）
        
        Args:
            query: 查询文本
            keywords: 关键词列表
            content: 文档内容
            
        Returns:
            float: 分数 (0-1)
        """
        content_lower = content.lower()
        
        # 计算匹配的关键词数量和频率
        matched_count = 0
        total_frequency = 0
        
        for keyword in keywords:
            if keyword in content_lower:
                matched_count += 1
                # 计算频率
                frequency = content_lower.count(keyword)
                total_frequency += frequency
        
        if not keywords:
            return 0.0
        
        # 归一化分数
        match_ratio = matched_count / len(keywords)
        frequency_score = min(total_frequency / (len(keywords) * 3), 1.0)
        
        # 综合分数
        score = 0.6 * match_ratio + 0.4 * frequency_score
        
        return min(score, 1.0)
    
    def _reciprocal_rank_fusion(
        self,
        results1: List[RetrievalResult],
        results2: List[RetrievalResult],
        k: int = 60
    ) -> List[RetrievalResult]:
        """
        Reciprocal Rank Fusion算法合并两个结果列表
        
        Args:
            results1: 第一个结果列表
            results2: 第二个结果列表
            k: RRF参数（默认60）
            
        Returns:
            List[RetrievalResult]: 合并后的结果
        """
        # 构建文档ID到结果的映射
        doc_scores: Dict[str, Tuple[RetrievalResult, float]] = {}
        
        # 处理第一个列表
        for i, result in enumerate(results1):
            doc_id = result.document.id
            rrf_score = 1.0 / (k + i + 1)
            doc_scores[doc_id] = (result, rrf_score)
        
        # 处理第二个列表
        for i, result in enumerate(results2):
            doc_id = result.document.id
            rrf_score = 1.0 / (k + i + 1)
            
            if doc_id in doc_scores:
                # 累加分数
                existing_result, existing_score = doc_scores[doc_id]
                doc_scores[doc_id] = (existing_result, existing_score + rrf_score)
            else:
                doc_scores[doc_id] = (result, rrf_score)
        
        # 排序
        sorted_items = sorted(
            doc_scores.values(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # 构建结果列表
        merged = []
        for i, (result, score) in enumerate(sorted_items):
            # 创建新的RetrievalResult
            merged_result = RetrievalResult(
                document=result.document,
                score=score,
                rank=i + 1,
                retrieval_mode="hybrid",
                metadata={
                    "rrf_score": score,
                    "fusion_method": "reciprocal_rank_fusion"
                }
            )
            merged.append(merged_result)
        
        return merged
    
    def _rerank_results(
        self,
        query: str,
        results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """
        重排序结果（基于查询-文档相关性）
        
        Args:
            query: 查询文本
            results: 候选结果
            
        Returns:
            List[RetrievalResult]: 重排序后的结果
        """
        # 简化版重排序：结合语义分数和关键词匹配
        keywords = self._extract_keywords(query)
        
        scored_results = []
        for result in results:
            # 原始语义分数
            semantic_score = result.score
            
            # 关键词匹配分数
            keyword_score = self._calculate_keyword_score(
                query, keywords, result.document.content
            )
            
            # 文档长度惩罚（太短或太长的文档）
            doc_length = len(result.document.content)
            length_penalty = 1.0
            if doc_length < 100:
                length_penalty = 0.8
            elif doc_length > 2000:
                length_penalty = 0.9
            
            # 综合分数 (语义70% + 关键词30%)
            final_score = (
                0.7 * semantic_score + 
                0.3 * keyword_score
            ) * length_penalty
            
            scored_results.append((result, final_score))
        
        # 排序
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        # 更新分数和排名
        reranked = []
        for i, (result, score) in enumerate(scored_results):
            result.score = score
            result.rank = i + 1
            result.metadata["rerank_score"] = score
            reranked.append(result)
        
        return reranked
    
    async def retrieve_with_context(
        self,
        query: str,
        mode: RetrievalMode = RetrievalMode.HYBRID,
        k: int = 3,
        max_context_length: int = 2000
    ) -> Tuple[List[RetrievalResult], str]:
        """
        检索并生成上下文字符串（用于Agent集成）
        
        Args:
            query: 查询文本
            mode: 检索模式
            k: 返回结果数量
            max_context_length: 最大上下文长度
            
        Returns:
            Tuple[List[RetrievalResult], str]: (检索结果, 上下文字符串)
        """
        # 检索
        results = await self.retrieve(query, mode, k)
        
        # 构建上下文
        context_parts = []
        current_length = 0
        
        for i, result in enumerate(results):
            # 添加来源标记
            source_info = result.document.metadata.get('file_name', f'Document {i+1}')
            header = f"\n### 来源 {i+1}: {source_info} (相关度: {result.score:.2f})\n"
            
            content = result.document.content
            
            # 检查是否超过长度限制
            if current_length + len(header) + len(content) > max_context_length:
                # 截断内容
                remaining = max_context_length - current_length - len(header)
                if remaining > 100:
                    content = content[:remaining] + "..."
                else:
                    break
            
            context_parts.append(header + content)
            current_length += len(header) + len(content)
        
        context = "\n".join(context_parts)
        
        return results, context
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取检索服务统计信息
        
        Returns:
            Dict: 统计信息
        """
        return {
            "collection_name": self.collection_name,
            "default_k": self.default_k,
            "score_threshold": self.score_threshold,
            "enable_rerank": self.enable_rerank,
            "vector_store_stats": self.vector_store.get_stats()
        }


# 单例实例
_retrieval_services: Dict[str, RetrievalService] = {}


def get_retrieval_service(
    collection_name: str = "default",
    default_k: int = 5,
    score_threshold: float = 0.0,
    enable_rerank: bool = True
) -> RetrievalService:
    """
    获取检索服务单例
    
    Args:
        collection_name: 集合名称
        default_k: 默认返回数量
        score_threshold: 分数阈值
        enable_rerank: 启用重排序
        
    Returns:
        RetrievalService: 检索服务实例
    """
    global _retrieval_services
    
    if collection_name not in _retrieval_services:
        _retrieval_services[collection_name] = RetrievalService(
            collection_name=collection_name,
            default_k=default_k,
            score_threshold=score_threshold,
            enable_rerank=enable_rerank
        )
    
    return _retrieval_services[collection_name]

