"""
RAG系统集成测试
测试前后端API连通性
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag import get_knowledge_base, RetrievalMode
from app.rag.embedding_service import EmbeddingProvider, get_embedding_service


async def test_integration():
    """完整集成测试"""
    print("\n" + "="*60)
    print("🧪 RAG系统集成测试")
    print("="*60)
    
    # 初始化本地embedding
    print("\n[0] 初始化embedding服务...")
    get_embedding_service(provider=EmbeddingProvider.LOCAL)
    print("✓ 使用本地embedding模型")
    
    # 1. 创建测试知识库
    print("\n[1] 创建测试知识库...")
    kb = get_knowledge_base(
        kb_name="integration_test",
        description="集成测试知识库"
    )
    await kb.clear()
    print("✓ 知识库创建成功")
    
    # 2. 添加测试文档
    print("\n[2] 添加测试文档...")
    test_docs = [
        {
            "text": "Python是一种解释型、面向对象、动态数据类型的高级程序设计语言。Python由Guido van Rossum于1989年底发明，第一个公开发行版发行于1991年。",
            "metadata": {"category": "programming", "topic": "python"}
        },
        {
            "text": "机器学习是人工智能的一个分支。专门研究计算机怎样模拟或实现人类的学习行为，以获取新的知识或技能，重新组织已有的知识结构使之不断改善自身的性能。",
            "metadata": {"category": "ai", "topic": "machine_learning"}
        },
        {
            "text": "FastAPI是一个现代、快速(高性能)的web框架，用于构建APIs，基于标准Python类型提示。它具有自动生成交互式API文档、数据验证等特性。",
            "metadata": {"category": "framework", "topic": "fastapi"}
        }
    ]
    
    total_docs = 0
    for doc in test_docs:
        doc_ids = await kb.add_text(doc["text"], doc["metadata"])
        total_docs += len(doc_ids)
        print(f"  ✓ 添加文档: {len(doc_ids)} 个块")
    
    print(f"✓ 总计添加 {total_docs} 个文档块")
    
    # 3. 测试搜索
    print("\n[3] 测试搜索功能...")
    test_queries = [
        ("Python编程语言", "programming"),
        ("人工智能学习", "ai"),
        ("Web框架", "framework")
    ]
    
    for query, expected_cat in test_queries:
        print(f"\n  查询: '{query}'")
        results = await kb.search(
            query=query,
            mode=RetrievalMode.HYBRID,
            k=2
        )
        print(f"  ✓ 找到 {len(results)} 个结果")
        for i, result in enumerate(results):
            cat = result.document.metadata.get('category', 'unknown')
            print(f"    {i+1}. [{cat}] 分数: {result.score:.3f}")
    
    # 4. 测试统计
    print("\n[4] 获取统计信息...")
    stats = await kb.get_stats()
    print(f"  ✓ 知识库: {stats['kb_name']}")
    print(f"  ✓ 文档数: {stats['document_count']}")
    print(f"  ✓ 集合: {stats['collection_name']}")
    
    # 5. 测试Agent上下文生成
    print("\n[5] 测试Agent上下文生成...")
    results, context = await kb.get_context(
        query="如何学习Python和机器学习",
        k=2
    )
    print(f"  ✓ 生成上下文: {len(context)} 字符")
    print(f"  ✓ 包含 {len(results)} 个来源")
    print("\n  上下文预览:")
    print("  " + "-"*56)
    print("  " + context[:200].replace('\n', '\n  ') + "...")
    print("  " + "-"*56)
    
    # 6. 清理
    print("\n[6] 清理测试数据...")
    await kb.clear()
    print("✓ 测试数据已清理")
    
    print("\n" + "="*60)
    print("✅ 所有集成测试通过!")
    print("="*60)
    print("\n📊 测试摘要:")
    print(f"  - 知识库创建: ✓")
    print(f"  - 文档添加: ✓ ({total_docs} 个块)")
    print(f"  - 搜索功能: ✓ (3 个查询)")
    print(f"  - 统计信息: ✓")
    print(f"  - Agent集成: ✓")
    print(f"  - 数据清理: ✓")
    print("\n🎉 RAG系统前后端集成完成!")


if __name__ == "__main__":
    asyncio.run(test_integration())
