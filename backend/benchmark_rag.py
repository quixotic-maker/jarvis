"""
RAG系统性能基准测试
测试向量检索、文档处理、缓存等性能指标
"""
import time
import asyncio
from pathlib import Path
import statistics

from app.rag import get_knowledge_base, RetrievalMode
from app.rag.embedding_service import get_embedding_service, EmbeddingProvider
from app.utils.cache import get_search_cache


class PerformanceBenchmark:
    """性能基准测试"""
    
    def __init__(self):
        self.kb_name = "benchmark_kb"
        self.kb = None
        self.results = {}
    
    async def setup(self):
        """初始化测试环境"""
        print("\n" + "="*60)
        print("RAG系统性能基准测试")
        print("="*60)
        
        # 使用本地embedding以获得一致的测试环境
        print("\n[1] 初始化embedding服务...")
        get_embedding_service(provider=EmbeddingProvider.LOCAL)
        print("✓ 使用本地embedding模型")
        
        # 创建测试知识库
        print("\n[2] 创建测试知识库...")
        self.kb = get_knowledge_base(
            self.kb_name,
            "性能测试知识库",
            chunk_size=500,
            chunk_overlap=50
        )
        print(f"✓ 知识库创建完成: {self.kb_name}")
    
    async def benchmark_document_processing(self, num_docs=100):
        """
        测试文档处理性能
        
        Args:
            num_docs: 测试文档数量
        """
        print(f"\n[3] 测试文档处理性能 (n={num_docs})...")
        
        # 生成测试文档
        test_docs = [
            f"这是测试文档 {i}。内容包含了关于人工智能、机器学习、深度学习的相关知识。"
            f"Python是一种流行的编程语言，广泛应用于数据科学和机器学习领域。"
            f"文档ID: {i}" * 5  # 重复以增加长度
            for i in range(num_docs)
        ]
        
        # 测试添加文档
        times = []
        for i, doc in enumerate(test_docs):
            start = time.time()
            await self.kb.add_text(
                doc,
                metadata={"doc_id": i, "category": "test"}
            )
            elapsed = time.time() - start
            times.append(elapsed)
            
            if (i + 1) % 20 == 0:
                print(f"  • 已处理 {i+1}/{num_docs} 个文档")
        
        # 统计结果
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        
        self.results['document_processing'] = {
            'total_docs': num_docs,
            'avg_time_per_doc': avg_time,
            'median_time': median_time,
            'total_time': sum(times),
            'docs_per_second': 1 / avg_time
        }
        
        print(f"\n  ✓ 文档处理完成:")
        print(f"    - 总文档数: {num_docs}")
        print(f"    - 平均耗时: {avg_time:.3f}秒/文档")
        print(f"    - 中位数: {median_time:.3f}秒")
        print(f"    - 处理速度: {1/avg_time:.2f} 文档/秒")
    
    async def benchmark_search_performance(self, num_queries=50):
        """
        测试搜索性能
        
        Args:
            num_queries: 测试查询数量
        """
        print(f"\n[4] 测试搜索性能 (n={num_queries})...")
        
        # 测试查询
        test_queries = [
            "人工智能机器学习",
            "Python编程语言",
            "深度学习神经网络",
            "数据科学分析",
            "自然语言处理"
        ] * (num_queries // 5)
        
        modes = {
            "semantic": RetrievalMode.SEMANTIC,
            "keyword": RetrievalMode.KEYWORD,
            "hybrid": RetrievalMode.HYBRID,
            "rerank": RetrievalMode.RERANK
        }
        
        mode_results = {}
        
        for mode_name, mode in modes.items():
            print(f"\n  测试 {mode_name} 模式...")
            times = []
            
            for i, query in enumerate(test_queries):
                start = time.time()
                results = await self.kb.search(
                    query,
                    mode=mode,
                    k=5
                )
                elapsed = time.time() - start
                times.append(elapsed)
                
                if (i + 1) % 10 == 0:
                    print(f"    • 已完成 {i+1}/{num_queries} 个查询")
            
            avg_time = statistics.mean(times)
            mode_results[mode_name] = {
                'avg_time': avg_time,
                'median_time': statistics.median(times),
                'min_time': min(times),
                'max_time': max(times),
                'queries_per_second': 1 / avg_time
            }
            
            print(f"    ✓ 平均耗时: {avg_time:.3f}秒")
            print(f"    ✓ 查询速度: {1/avg_time:.2f} 查询/秒")
        
        self.results['search_performance'] = mode_results
    
    async def benchmark_cache_performance(self, num_queries=100):
        """
        测试缓存性能
        
        Args:
            num_queries: 测试查询数量
        """
        print(f"\n[5] 测试缓存性能 (n={num_queries})...")
        
        cache = get_search_cache()
        cache.clear()  # 清空缓存
        
        query = "测试缓存查询"
        
        # 第一次查询（无缓存）
        print("\n  第一次查询（冷启动）...")
        cold_times = []
        for i in range(10):
            start = time.time()
            await self.kb.search(query, k=5)
            cold_times.append(time.time() - start)
        
        avg_cold = statistics.mean(cold_times)
        print(f"    ✓ 平均耗时: {avg_cold:.3f}秒")
        
        # 第二次查询（有缓存）
        print("\n  重复查询（缓存命中）...")
        hot_times = []
        for i in range(num_queries):
            start = time.time()
            await self.kb.search(query, k=5)
            hot_times.append(time.time() - start)
        
        avg_hot = statistics.mean(hot_times)
        speedup = avg_cold / avg_hot
        
        print(f"    ✓ 平均耗时: {avg_hot:.3f}秒")
        print(f"    ✓ 加速比: {speedup:.2f}x")
        
        self.results['cache_performance'] = {
            'cold_start_time': avg_cold,
            'cached_time': avg_hot,
            'speedup': speedup,
            'cache_hit_rate': 100.0
        }
    
    async def benchmark_concurrent_load(self, num_concurrent=10):
        """
        测试并发负载
        
        Args:
            num_concurrent: 并发查询数
        """
        print(f"\n[6] 测试并发负载 (并发数={num_concurrent})...")
        
        query = "并发测试查询"
        
        # 并发查询
        async def run_query():
            start = time.time()
            await self.kb.search(query, k=5)
            return time.time() - start
        
        print(f"  启动 {num_concurrent} 个并发查询...")
        start_time = time.time()
        tasks = [run_query() for _ in range(num_concurrent)]
        times = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        avg_time = statistics.mean(times)
        throughput = num_concurrent / total_time
        
        self.results['concurrent_load'] = {
            'num_concurrent': num_concurrent,
            'total_time': total_time,
            'avg_query_time': avg_time,
            'throughput': throughput
        }
        
        print(f"\n  ✓ 并发测试完成:")
        print(f"    - 并发数: {num_concurrent}")
        print(f"    - 总耗时: {total_time:.3f}秒")
        print(f"    - 平均查询时间: {avg_time:.3f}秒")
        print(f"    - 吞吐量: {throughput:.2f} 查询/秒")
    
    async def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("性能测试总结")
        print("="*60)
        
        print("\n📄 文档处理性能:")
        doc_perf = self.results['document_processing']
        print(f"  • 处理速度: {doc_perf['docs_per_second']:.2f} 文档/秒")
        print(f"  • 平均耗时: {doc_perf['avg_time_per_doc']:.3f} 秒/文档")
        
        print("\n🔍 搜索性能:")
        for mode, metrics in self.results['search_performance'].items():
            print(f"  • {mode.upper()}模式:")
            print(f"    - 查询速度: {metrics['queries_per_second']:.2f} 查询/秒")
            print(f"    - 平均耗时: {metrics['avg_time']:.3f} 秒")
            print(f"    - 耗时范围: {metrics['min_time']:.3f}~{metrics['max_time']:.3f} 秒")
        
        print("\n💾 缓存性能:")
        cache_perf = self.results['cache_performance']
        print(f"  • 无缓存: {cache_perf['cold_start_time']:.3f} 秒")
        print(f"  • 有缓存: {cache_perf['cached_time']:.3f} 秒")
        print(f"  • 加速比: {cache_perf['speedup']:.2f}x")
        
        print("\n⚡ 并发性能:")
        concurrent = self.results['concurrent_load']
        print(f"  • 并发数: {concurrent['num_concurrent']}")
        print(f"  • 吞吐量: {concurrent['throughput']:.2f} 查询/秒")
        
        # 性能评级
        print("\n📊 性能评级:")
        doc_speed = doc_perf['docs_per_second']
        search_speed = self.results['search_performance']['hybrid']['queries_per_second']
        
        def rate_performance(value, thresholds):
            if value >= thresholds[0]:
                return "优秀 ⭐⭐⭐⭐⭐"
            elif value >= thresholds[1]:
                return "良好 ⭐⭐⭐⭐"
            elif value >= thresholds[2]:
                return "一般 ⭐⭐⭐"
            else:
                return "需优化 ⭐⭐"
        
        print(f"  • 文档处理: {rate_performance(doc_speed, [5, 2, 1])}")
        print(f"  • 搜索速度: {rate_performance(search_speed, [20, 10, 5])}")
        print(f"  • 缓存效果: {rate_performance(cache_perf['speedup'], [10, 5, 2])}")
        
        print("\n" + "="*60)
        print("✅ 所有性能测试完成!")
        print("="*60)
    
    async def cleanup(self):
        """清理测试数据"""
        print("\n[7] 清理测试数据...")
        await self.kb.clear()
        print("✓ 测试数据已清理")


async def run_benchmark():
    """运行完整的性能基准测试"""
    benchmark = PerformanceBenchmark()
    
    try:
        # 设置
        await benchmark.setup()
        
        # 文档处理测试
        await benchmark.benchmark_document_processing(num_docs=50)
        
        # 搜索性能测试
        await benchmark.benchmark_search_performance(num_queries=20)
        
        # 缓存性能测试
        await benchmark.benchmark_cache_performance(num_queries=50)
        
        # 并发负载测试
        await benchmark.benchmark_concurrent_load(num_concurrent=10)
        
        # 打印总结
        await benchmark.print_summary()
        
    finally:
        # 清理
        await benchmark.cleanup()


if __name__ == "__main__":
    asyncio.run(run_benchmark())
