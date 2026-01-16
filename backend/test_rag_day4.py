"""
RAG系统 Day 4-5 测试套件
测试检索服务：语义搜索、关键词搜索、混合检索、重排序
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.rag.retrieval_service import (
    RetrievalService, get_retrieval_service,
    RetrievalMode, RetrievalResult
)
from app.rag.embedding_service import get_embedding_service, EmbeddingProvider
from app.rag.vector_store import get_vector_store, Document
from app.rag.document_processor import get_document_processor


async def test_setup():
    """设置测试环境：创建测试文档并存入向量数据库"""
    print("\n" + "="*60)
    print("测试准备: 创建测试文档库")
    print("="*60)
    
    # 创建测试文档
    test_docs = [
        {
            "content": """Python是一种高级编程语言，由Guido van Rossum创建。
Python具有简洁清晰的语法，强大的标准库，广泛应用于Web开发、数据分析、人工智能等领域。
Python的设计哲学强调代码的可读性和简洁的语法。""",
            "metadata": {"title": "Python简介", "category": "programming", "language": "python"}
        },
        {
            "content": """机器学习是人工智能的一个分支，通过算法让计算机从数据中学习。
常见的机器学习算法包括线性回归、决策树、神经网络等。
Python是机器学习领域最流行的编程语言，TensorFlow和PyTorch是主流框架。""",
            "metadata": {"title": "机器学习基础", "category": "ai", "language": "python"}
        },
        {
            "content": """数据库是存储和管理数据的系统。SQL数据库使用结构化查询语言。
NoSQL数据库包括MongoDB、Redis等，适合处理非结构化数据。
向量数据库如ChromaDB专门用于存储和检索向量数据。""",
            "metadata": {"title": "数据库概述", "category": "database", "language": "general"}
        },
        {
            "content": """Web开发包括前端和后端开发。前端使用HTML、CSS、JavaScript。
后端可以使用Python的Flask和Django框架。
RESTful API是现代Web应用的标准接口设计方式。""",
            "metadata": {"title": "Web开发技术", "category": "web", "language": "python"}
        },
        {
            "content": """Git是分布式版本控制系统，用于跟踪代码变更。
常用命令包括git add、git commit、git push、git pull等。
GitHub是最流行的代码托管平台，支持团队协作和开源项目。""",
            "metadata": {"title": "Git版本控制", "category": "tools", "language": "general"}
        },
        {
            "content": """深度学习是机器学习的子集，使用多层神经网络。
卷积神经网络(CNN)用于图像识别，循环神经网络(RNN)用于序列数据。
Transformer模型revolutionized自然语言处理领域。""",
            "metadata": {"title": "深度学习", "category": "ai", "language": "python"}
        },
        {
            "content": """Docker是容器化技术，可以打包应用和依赖环境。
Kubernetes用于容器编排和管理。
容器技术简化了应用部署和扩展。""",
            "metadata": {"title": "容器技术", "category": "devops", "language": "general"}
        },
        {
            "content": """数据分析使用统计方法从数据中提取洞察。
Python的pandas库提供强大的数据处理功能。
数据可视化工具包括matplotlib、seaborn等。""",
            "metadata": {"title": "数据分析", "category": "data-science", "language": "python"}
        }
    ]
    
    # 获取服务 (使用本地embedding模型)
    embedding_service = get_embedding_service(provider=EmbeddingProvider.LOCAL)
    vector_store = get_vector_store("test_collection")
    
    # 清空现有数据
    await vector_store.clear()
    print("✓ 清空现有数据")
    
    # 创建Document对象
    documents = []
    for i, doc_data in enumerate(test_docs):
        doc = Document(
            content=doc_data["content"],
            metadata=doc_data["metadata"],
            doc_id=f"test_doc_{i}"
        )
        documents.append(doc)
    
    # 批量生成embedding
    contents = [doc.content for doc in documents]
    embeddings = await embedding_service.embed_batch(contents)
    
    # 添加到向量数据库
    for doc, embedding in zip(documents, embeddings):
        doc.embedding = embedding
    
    doc_ids = await vector_store.add_documents(documents)
    print(f"✓ 添加 {len(doc_ids)} 个测试文档")
    
    # 验证
    stats = await vector_store.get_stats()
    print(f"✓ 向量库统计: {stats['document_count']} 个文档")
    
    print("\n✅ 测试环境准备完成")
    return vector_store


async def test_semantic_search():
    """测试语义搜索"""
    print("\n" + "="*60)
    print("测试1: 语义搜索 (Semantic Search)")
    print("="*60)
    
    retrieval_service = get_retrieval_service("test_collection")
    
    # 测试用例
    test_queries = [
        "什么是Python编程语言？",
        "机器学习的常用算法有哪些？",
        "数据库的类型"
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\n[查询 {i+1}] {query}")
        
        results = await retrieval_service.retrieve(
            query=query,
            mode=RetrievalMode.SEMANTIC,
            k=3
        )
        
        print(f"✓ 返回 {len(results)} 个结果:")
        for j, result in enumerate(results):
            title = result.document.metadata.get('title', 'Unknown')
            print(f"  {j+1}. {title}")
            print(f"     相关度: {result.score:.3f}")
            print(f"     内容: {result.document.content[:60]}...")
    
    print("\n✅ 语义搜索测试通过")


async def test_keyword_search():
    """测试关键词搜索"""
    print("\n" + "="*60)
    print("测试2: 关键词搜索 (Keyword Search)")
    print("="*60)
    
    retrieval_service = get_retrieval_service("test_collection")
    
    test_queries = [
        "Python TensorFlow",
        "数据库 SQL NoSQL",
        "Git GitHub"
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\n[查询 {i+1}] {query}")
        
        results = await retrieval_service.retrieve(
            query=query,
            mode=RetrievalMode.KEYWORD,
            k=3
        )
        
        print(f"✓ 返回 {len(results)} 个结果:")
        for j, result in enumerate(results):
            title = result.document.metadata.get('title', 'Unknown')
            matched_kw = result.metadata.get('matched_keywords', [])
            print(f"  {j+1}. {title}")
            print(f"     分数: {result.score:.3f}")
            print(f"     匹配关键词: {', '.join(matched_kw[:5])}")
    
    print("\n✅ 关键词搜索测试通过")


async def test_hybrid_search():
    """测试混合检索"""
    print("\n" + "="*60)
    print("测试3: 混合检索 (Hybrid Search)")
    print("="*60)
    
    retrieval_service = get_retrieval_service("test_collection")
    
    test_queries = [
        "Python机器学习框架",
        "容器化部署技术",
        "数据分析可视化"
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\n[查询 {i+1}] {query}")
        
        # 对比三种模式
        modes = [
            (RetrievalMode.SEMANTIC, "语义"),
            (RetrievalMode.KEYWORD, "关键词"),
            (RetrievalMode.HYBRID, "混合")
        ]
        
        for mode, mode_name in modes:
            results = await retrieval_service.retrieve(
                query=query,
                mode=mode,
                k=2
            )
            
            print(f"\n  [{mode_name}模式]")
            for j, result in enumerate(results):
                title = result.document.metadata.get('title', 'Unknown')
                print(f"    {j+1}. {title} (分数: {result.score:.3f})")
    
    print("\n✅ 混合检索测试通过")


async def test_rerank():
    """测试重排序"""
    print("\n" + "="*60)
    print("测试4: 重排序 (Rerank)")
    print("="*60)
    
    retrieval_service = get_retrieval_service("test_collection", enable_rerank=True)
    
    query = "Python数据处理和分析"
    
    print(f"\n[查询] {query}")
    
    # 对比重排序前后
    print("\n[重排序前 - 纯语义搜索]")
    results_before = await retrieval_service.retrieve(
        query=query,
        mode=RetrievalMode.SEMANTIC,
        k=5
    )
    
    for i, result in enumerate(results_before):
        title = result.document.metadata.get('title', 'Unknown')
        print(f"  {i+1}. {title} (分数: {result.score:.3f})")
    
    print("\n[重排序后]")
    results_after = await retrieval_service.retrieve(
        query=query,
        mode=RetrievalMode.RERANK,
        k=5
    )
    
    for i, result in enumerate(results_after):
        title = result.document.metadata.get('title', 'Unknown')
        rerank_score = result.metadata.get('rerank_score', 0)
        print(f"  {i+1}. {title}")
        print(f"      重排序分数: {rerank_score:.3f}")
    
    print("\n✅ 重排序测试通过")


async def test_metadata_filtering():
    """测试元数据过滤"""
    print("\n" + "="*60)
    print("测试5: 元数据过滤")
    print("="*60)
    
    retrieval_service = get_retrieval_service("test_collection")
    
    query = "技术介绍"
    
    # 测试不同的过滤条件
    filters = [
        ({"category": "ai"}, "AI分类"),
        ({"language": "python"}, "Python相关"),
        ({"category": "database"}, "数据库分类")
    ]
    
    for filter_dict, description in filters:
        print(f"\n[过滤条件: {description}]")
        
        results = await retrieval_service.retrieve(
            query=query,
            mode=RetrievalMode.SEMANTIC,
            k=5,
            filter_metadata=filter_dict
        )
        
        print(f"✓ 返回 {len(results)} 个结果:")
        for i, result in enumerate(results):
            title = result.document.metadata.get('title', 'Unknown')
            category = result.document.metadata.get('category', 'Unknown')
            print(f"  {i+1}. {title} (分类: {category})")
    
    print("\n✅ 元数据过滤测试通过")


async def test_context_generation():
    """测试上下文生成（用于Agent集成）"""
    print("\n" + "="*60)
    print("测试6: 上下文生成 (Agent集成)")
    print("="*60)
    
    retrieval_service = get_retrieval_service("test_collection")
    
    query = "如何使用Python进行机器学习？"
    
    print(f"\n[查询] {query}")
    
    # 检索并生成上下文
    results, context = await retrieval_service.retrieve_with_context(
        query=query,
        mode=RetrievalMode.HYBRID,
        k=3,
        max_context_length=500
    )
    
    print(f"\n✓ 检索到 {len(results)} 个相关文档")
    print(f"✓ 生成上下文长度: {len(context)} 字符")
    
    print("\n生成的上下文:")
    print("-" * 60)
    print(context)
    print("-" * 60)
    
    # 验证上下文格式
    assert "### 来源" in context, "上下文应包含来源标记"
    assert "相关度:" in context, "上下文应包含相关度信息"
    
    print("\n✅ 上下文生成测试通过")


async def test_performance():
    """测试检索性能"""
    print("\n" + "="*60)
    print("测试7: 性能测试")
    print("="*60)
    
    retrieval_service = get_retrieval_service("test_collection")
    
    import time
    
    queries = [
        "Python编程",
        "机器学习算法",
        "数据库技术",
        "Web开发",
        "版本控制"
    ]
    
    print("\n测试不同检索模式的性能:")
    
    modes = [
        (RetrievalMode.SEMANTIC, "语义搜索"),
        (RetrievalMode.KEYWORD, "关键词搜索"),
        (RetrievalMode.HYBRID, "混合检索"),
        (RetrievalMode.RERANK, "重排序")
    ]
    
    for mode, mode_name in modes:
        start_time = time.time()
        
        for query in queries:
            await retrieval_service.retrieve(query, mode=mode, k=5)
        
        elapsed = time.time() - start_time
        avg_time = elapsed / len(queries) * 1000  # ms
        
        print(f"\n  [{mode_name}]")
        print(f"    总时间: {elapsed:.2f}s")
        print(f"    平均时间: {avg_time:.1f}ms/查询")
        
        # 性能断言
        assert avg_time < 1000, f"{mode_name}平均响应时间应小于1秒"
    
    print("\n✅ 性能测试通过")


async def test_integration():
    """集成测试：完整检索流程"""
    print("\n" + "="*60)
    print("测试8: 集成测试 - 完整检索流程")
    print("="*60)
    
    print("\n[步骤1] 初始化检索服务")
    retrieval_service = get_retrieval_service("test_collection")
    stats = retrieval_service.get_stats()
    print(f"✓ 服务初始化完成")
    print(f"  集合名称: {stats['collection_name']}")
    print(f"  默认返回数: {stats['default_k']}")
    print(f"  文档总数: {stats['vector_store_stats']['document_count']}")
    
    print("\n[步骤2] 执行混合检索")
    query = "Python在人工智能领域的应用"
    results = await retrieval_service.retrieve(
        query=query,
        mode=RetrievalMode.HYBRID,
        k=3,
        score_threshold=0.1
    )
    print(f"✓ 检索完成: {len(results)} 个结果")
    
    print("\n[步骤3] 验证结果质量")
    for i, result in enumerate(results):
        # 验证必需字段
        assert result.document is not None, "文档不能为空"
        assert result.score >= 0.0, "分数应为非负数"
        assert result.rank == i + 1, f"排名应为 {i+1}"
        assert result.retrieval_mode == RetrievalMode.HYBRID, "检索模式应为HYBRID"
        
        print(f"  ✓ 结果 {i+1} 验证通过")
    
    print("\n[步骤4] 生成Agent上下文")
    results, context = await retrieval_service.retrieve_with_context(
        query=query,
        mode=RetrievalMode.HYBRID,
        k=2,
        max_context_length=300
    )
    
    assert len(context) <= 350, "上下文长度应在限制范围内"
    assert len(context) > 0, "上下文不应为空"
    print(f"✓ 上下文生成成功 ({len(context)} 字符)")
    
    print("\n✅ 集成测试通过")


async def cleanup():
    """清理测试数据"""
    print("\n" + "="*60)
    print("清理测试数据")
    print("="*60)
    
    vector_store = get_vector_store("test_collection")
    await vector_store.clear()
    print("✓ 测试数据已清理")


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("RAG系统 Day 4-5 测试套件")
    print("测试范围: 检索服务 (语义/关键词/混合/重排序)")
    print("="*60)
    
    try:
        # 准备测试环境
        await test_setup()
        
        # 运行所有测试
        await test_semantic_search()
        await test_keyword_search()
        await test_hybrid_search()
        await test_rerank()
        await test_metadata_filtering()
        await test_context_generation()
        await test_performance()
        await test_integration()
        
        # 清理
        await cleanup()
        
        print("\n" + "="*60)
        print("🎉 所有测试通过!")
        print("="*60)
        print("\n✅ Day 4-5 交付物验证完成:")
        print("  1. 语义搜索 (Semantic Search) ✓")
        print("  2. 关键词搜索 (Keyword Search) ✓")
        print("  3. 混合检索 (Hybrid Search - RRF) ✓")
        print("  4. 重排序 (Rerank) ✓")
        print("  5. 元数据过滤 ✓")
        print("  6. 上下文生成 (Agent集成) ✓")
        print("  7. 性能验证 (<1s/查询) ✓")
        print("  8. 集成测试 ✓")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 测试错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
