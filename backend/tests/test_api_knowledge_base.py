"""
Knowledge Base API 测试
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from app.rag.embedding_service import get_embedding_service, EmbeddingProvider

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_embedding():
    """设置本地embedding以避免API密钥"""
    get_embedding_service(provider=EmbeddingProvider.LOCAL)
    yield


@pytest.fixture
def test_kb_name():
    """测试知识库名称"""
    return "test_kb_api"


class TestKnowledgeBaseAPI:
    """知识库API测试"""
    
    def test_list_knowledge_bases(self):
        """测试列出知识库"""
        response = client.get("/api/knowledge-base/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_knowledge_base(self, test_kb_name):
        """测试创建知识库"""
        payload = {
            "name": test_kb_name,
            "description": "API测试知识库",
            "chunk_size": 500,
            "chunk_overlap": 100
        }
        response = client.post("/api/knowledge-base/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == test_kb_name
        assert data["description"] == "API测试知识库"
        assert "document_count" in data
    
    def test_get_knowledge_base_info(self, test_kb_name):
        """测试获取知识库信息"""
        # 先创建
        self.test_create_knowledge_base(test_kb_name)
        
        # 获取信息
        response = client.get(f"/api/knowledge-base/{test_kb_name}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_kb_name
        assert "document_count" in data
    
    def test_add_text_document(self, test_kb_name):
        """测试添加文本文档"""
        # 确保知识库存在
        self.test_create_knowledge_base(test_kb_name)
        
        # 添加文本
        payload = {
            "text": "这是一个测试文档。Python是一种流行的编程语言。",
            "metadata": {"category": "test", "source": "api_test"}
        }
        response = client.post(
            f"/api/knowledge-base/{test_kb_name}/text",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "document_ids" in data
        assert len(data["document_ids"]) > 0
    
    def test_search_documents(self, test_kb_name):
        """测试搜索文档"""
        # 先添加文档
        self.test_add_text_document(test_kb_name)
        
        # 搜索
        payload = {
            "query": "Python编程",
            "mode": "semantic",
            "k": 3
        }
        response = client.post(
            f"/api/knowledge-base/{test_kb_name}/search",
            json=payload
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)
        
        if len(results) > 0:
            result = results[0]
            assert "document_id" in result
            assert "content" in result
            assert "score" in result
            assert "rank" in result
    
    def test_search_cache(self, test_kb_name):
        """测试搜索缓存功能"""
        # 添加文档
        self.test_add_text_document(test_kb_name)
        
        # 第一次搜索
        payload = {
            "query": "Python",
            "mode": "hybrid",
            "k": 2
        }
        response1 = client.post(
            f"/api/knowledge-base/{test_kb_name}/search",
            json=payload
        )
        assert response1.status_code == 200
        results1 = response1.json()
        
        # 第二次相同搜索（应该命中缓存）
        response2 = client.post(
            f"/api/knowledge-base/{test_kb_name}/search",
            json=payload
        )
        assert response2.status_code == 200
        results2 = response2.json()
        
        # 结果应该一致
        assert len(results1) == len(results2)
    
    def test_list_documents(self, test_kb_name):
        """测试列出文档"""
        # 添加文档
        self.test_add_text_document(test_kb_name)
        
        # 列出文档
        response = client.get(
            f"/api/knowledge-base/{test_kb_name}/documents",
            params={"limit": 10}
        )
        assert response.status_code == 200
        documents = response.json()
        assert isinstance(documents, list)
        
        if len(documents) > 0:
            doc = documents[0]
            assert "id" in doc
            assert "content_preview" in doc
            assert "metadata" in doc
    
    def test_get_stats(self, test_kb_name):
        """测试获取统计信息"""
        # 添加文档
        self.test_add_text_document(test_kb_name)
        
        # 获取统计
        response = client.get(f"/api/knowledge-base/{test_kb_name}/stats")
        assert response.status_code == 200
        stats = response.json()
        assert "document_count" in stats
        assert stats["document_count"] > 0
    
    def test_cache_stats(self):
        """测试缓存统计"""
        response = client.get("/api/knowledge-base/cache/stats")
        assert response.status_code == 200
        stats = response.json()
        assert "size" in stats
        assert "max_size" in stats
        assert "default_ttl" in stats
    
    def test_clear_cache(self):
        """测试清空缓存"""
        response = client.post("/api/knowledge-base/cache/clear")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "cleared_entries" in data
    
    def test_delete_knowledge_base(self, test_kb_name):
        """测试删除知识库"""
        # 创建知识库
        self.test_create_knowledge_base(test_kb_name)
        
        # 删除
        response = client.delete(f"/api/knowledge-base/{test_kb_name}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_kb_not_found(self):
        """测试知识库不存在的情况"""
        response = client.get("/api/knowledge-base/nonexistent_kb_xyz")
        assert response.status_code == 404


class TestSearchModes:
    """测试不同搜索模式"""
    
    @pytest.fixture
    def kb_with_data(self, test_kb_name):
        """创建带数据的知识库"""
        # 创建知识库
        payload = {
            "name": test_kb_name,
            "description": "搜索模式测试",
        }
        client.post("/api/knowledge-base/", json=payload)
        
        # 添加多个文档
        docs = [
            "Python是一种解释型的高级编程语言",
            "机器学习是人工智能的重要分支",
            "深度学习使用神经网络进行数据处理",
        ]
        for doc in docs:
            client.post(
                f"/api/knowledge-base/{test_kb_name}/text",
                json={"text": doc}
            )
        return test_kb_name
    
    def test_semantic_search(self, kb_with_data):
        """测试语义搜索"""
        payload = {
            "query": "编程语言",
            "mode": "semantic",
            "k": 2
        }
        response = client.post(
            f"/api/knowledge-base/{kb_with_data}/search",
            json=payload
        )
        assert response.status_code == 200
        assert len(response.json()) > 0
    
    def test_keyword_search(self, kb_with_data):
        """测试关键词搜索"""
        payload = {
            "query": "Python",
            "mode": "keyword",
            "k": 2
        }
        response = client.post(
            f"/api/knowledge-base/{kb_with_data}/search",
            json=payload
        )
        assert response.status_code == 200
    
    def test_hybrid_search(self, kb_with_data):
        """测试混合搜索"""
        payload = {
            "query": "人工智能学习",
            "mode": "hybrid",
            "k": 3
        }
        response = client.post(
            f"/api/knowledge-base/{kb_with_data}/search",
            json=payload
        )
        assert response.status_code == 200
    
    def test_rerank_search(self, kb_with_data):
        """测试重排序搜索"""
        payload = {
            "query": "神经网络",
            "mode": "rerank",
            "k": 2
        }
        response = client.post(
            f"/api/knowledge-base/{kb_with_data}/search",
            json=payload
        )
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
