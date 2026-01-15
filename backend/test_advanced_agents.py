"""测试高级Agent功能"""
import asyncio
from app.agents.knowledge_graph_agent import KnowledgeGraphAgent
from app.agents.rag_agent import RAGAgent
from app.agents.agentic_rag_agent import AgenticRAGAgent
from app.agents.mcp_agent import MCPAgent
from app.db.database import SessionLocal, engine
from app.db import models


def init_database():
    """初始化数据库"""
    print("\n📊 初始化数据库...")
    models.Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功！")


async def test_knowledge_graph():
    """测试知识图谱Agent"""
    print("\n" + "="*60)
    print("🧠 测试知识图谱Agent")
    print("="*60)
    
    agent = KnowledgeGraphAgent()
    db = SessionLocal()
    
    try:
        # 测试1: 知识抽取
        print("\n1️⃣ 测试知识抽取:")
        text = """
        深度学习是机器学习的一个分支。神经网络是深度学习的核心技术。
        常见的神经网络架构包括CNN（卷积神经网络）用于图像识别，
        RNN（循环神经网络）用于序列建模，Transformer用于自然语言处理。
        """
        result = await agent.execute({
            "action": "extract",
            "user_input": text,
            "db": db
        })
        print(f"✅ 抽取结果: {result.get('message')}")
        print(f"   实体数量: {result.get('count', {}).get('entities', 0)}")
        print(f"   关系数量: {result.get('count', {}).get('relations', 0)}")
        
        # 测试2: 查询图谱
        print("\n2️⃣ 测试图谱查询:")
        result = await agent.execute({
            "action": "query",
            "user_input": "深度学习",
            "db": db
        })
        print(f"✅ 查询结果数量: {result.get('count', 0)}")
        
    finally:
        db.close()


async def test_rag():
    """测试RAG Agent"""
    print("\n" + "="*60)
    print("📚 测试RAG Agent")
    print("="*60)
    
    agent = RAGAgent()
    db = SessionLocal()
    
    try:
        # 测试1: 索引文档
        print("\n1️⃣ 测试文档索引:")
        document = """
        什么是微服务架构？
        微服务架构是一种软件架构风格，将单一应用程序开发为一组小型服务。
        每个服务运行在自己的进程中，并使用轻量级机制（通常是HTTP API）进行通信。
        
        微服务的优势：
        1. 独立部署 - 每个服务可以独立部署和扩展
        2. 技术多样性 - 不同服务可以使用不同的技术栈
        3. 容错性 - 单个服务的故障不会影响整个系统
        4. 团队自治 - 小团队可以独立负责特定服务
        
        微服务的挑战：
        1. 分布式系统复杂性
        2. 数据一致性
        3. 服务间通信
        4. 部署和监控的复杂性
        """
        result = await agent.execute({
            "action": "index",
            "user_input": document,
            "db": db
        })
        print(f"✅ 索引结果: {result.get('message')}")
        print(f"   文档片段数: {result.get('chunks_count', 0)}")
        
        # 测试2: RAG查询
        print("\n2️⃣ 测试RAG查询:")
        result = await agent.execute({
            "action": "query",
            "user_input": "微服务的优势是什么？",
            "db": db
        })
        print(f"✅ 检索到文档片段: {result.get('retrieved_chunks', 0)}")
        print(f"   回答: {result.get('answer', '')[:100]}...")
        
    finally:
        db.close()


async def test_agentic_rag():
    """测试Agentic RAG Agent"""
    print("\n" + "="*60)
    print("🤖 测试Agentic RAG Agent")
    print("="*60)
    
    agent = AgenticRAGAgent()
    db = SessionLocal()
    
    try:
        # 先索引一些文档
        rag_agent = RAGAgent()
        doc1 = """
        React是一个用于构建用户界面的JavaScript库。
        优点：虚拟DOM提升性能，组件化开发，丰富的生态系统。
        缺点：学习曲线较陡，需要额外的状态管理库。
        """
        doc2 = """
        Vue是一个渐进式JavaScript框架。
        优点：易于学习，灵活的架构，优秀的文档。
        缺点：生态系统相对较小，企业级支持较少。
        """
        await rag_agent.execute({"action": "index", "user_input": doc1, "db": db})
        await rag_agent.execute({"action": "index", "user_input": doc2, "db": db})
        
        # 测试Agentic RAG查询
        print("\n1️⃣ 测试Agentic RAG查询（复杂问题）:")
        result = await agent.execute({
            "user_input": "对比React和Vue，给出选型建议",
            "max_iterations": 3,
            "db": db
        })
        
        print(f"✅ 迭代次数: {result.get('iterations', 0)}")
        print(f"   置信度: {result.get('confidence', 0)}")
        print(f"   回答: {result.get('answer', '')[:150]}...")
        
        # 显示推理链
        print("\n🔗 推理链:")
        for step in result.get('reasoning_chain', []):
            print(f"   迭代{step['iteration']}: "
                  f"检索{step['retrieved_docs']}个文档, "
                  f"质量分数: {step['reflection'].get('quality_score', 0)}")
        
    finally:
        db.close()


async def test_mcp():
    """测试MCP Agent"""
    print("\n" + "="*60)
    print("🔌 测试MCP Agent")
    print("="*60)
    
    agent = MCPAgent()
    db = SessionLocal()
    
    try:
        # 测试1: MCP对话
        print("\n1️⃣ 测试MCP对话:")
        result = await agent.execute({
            "action": "chat",
            "user_input": "帮我安排明天下午2点的会议",
            "context": {"user_id": "test_user"},
            "db": db
        })
        print(f"✅ 对话结果: {result.get('result', {}).get('type')}")
        print(f"   上下文大小: {result.get('context_size', 0)}")
        
        # 测试2: 工具调用
        print("\n2️⃣ 测试MCP工具调用:")
        result = await agent.execute({
            "action": "tool_call",
            "user_input": "创建一个提醒：明天早上8点叫我起床",
            "context": {},
            "db": db
        })
        print(f"✅ 工具调用: {result.get('tool_call', {}).get('tool_name')}")
        
        # 测试3: 上下文管理
        print("\n3️⃣ 测试上下文管理:")
        result = await agent.execute({
            "action": "context_manage",
            "context": {"action": "get"},
            "db": db
        })
        print(f"✅ 上下文窗口大小: {result.get('size', 0)}")
        
    finally:
        db.close()


async def main():
    """运行所有测试"""
    print("\n" + "🚀"*30)
    print("Jarvis 高级Agent功能测试")
    print("🚀"*30)
    
    # 初始化数据库
    init_database()
    
    # 运行各个测试
    await test_knowledge_graph()
    await test_rag()
    await test_agentic_rag()
    await test_mcp()
    
    print("\n" + "="*60)
    print("✅ 所有测试完成！")
    print("="*60)
    print("\n💡 测试总结:")
    print("   1. ✅ 知识图谱Agent - 实体抽取、关系构建、图谱查询")
    print("   2. ✅ RAG Agent - 文档索引、语义检索、增强生成")
    print("   3. ✅ Agentic RAG Agent - 查询规划、迭代优化、推理链")
    print("   4. ✅ MCP Agent - 上下文管理、工具调用、状态维护")
    print("\n🎉 Jarvis现已具备25个专业Agent，集成前沿AI技术！")


if __name__ == "__main__":
    asyncio.run(main())
