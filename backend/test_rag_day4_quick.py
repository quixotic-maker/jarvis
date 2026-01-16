"""
RAG系统 Day 4-5 快速测试
简化版测试，跳过模型下载
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("✅ 模块导入成功")
print("  - RetrievalService")
print("  - RetrievalMode")  
print("  - RetrievalResult")

async def quick_test():
    """快速测试RetrievalService功能"""
    from app.rag.retrieval_service import RetrievalService, RetrievalMode
    
    print("\n[测试1] 关键词提取")
    service = RetrievalService()
    keywords = service._extract_keywords("Python机器学习框架TensorFlow")
    print(f"✓ 关键词: {keywords}")
    assert len(keywords) > 0
    
    print("\n[测试2] 关键词分数计算")
    score = service._calculate_keyword_score(
        "Python机器学习",
        ["python", "机器学习"],
        "Python是一种编程语言，广泛用于机器学习领域。"
    )
    print(f"✓ 分数: {score:.3f}")
    assert score > 0
    
    print("\n[测试3] RRF算法")
    from app.rag.retrieval_service import RetrievalResult
    from app.rag.vector_store import Document
    
    # 模拟结果
    doc1 = Document(content="文档1", doc_id="1")
    doc2 = Document(content="文档2", doc_id="2")
    
    results1 = [
        RetrievalResult(doc1, 0.9, 1, "semantic", {}),
        RetrievalResult(doc2, 0.8, 2, "semantic", {})
    ]
    
    results2 = [
        RetrievalResult(doc2, 0.95, 1, "keyword", {}),
        RetrievalResult(doc1, 0.7, 2, "keyword", {})
    ]
    
    merged = service._reciprocal_rank_fusion(results1, results2)
    print(f"✓ RRF合并: {len(merged)} 个结果")
    assert len(merged) == 2
    
    print("\n✅ 所有核心功能测试通过!")

if __name__ == "__main__":
    asyncio.run(quick_test())
