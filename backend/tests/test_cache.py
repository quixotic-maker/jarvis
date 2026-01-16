"""
缓存系统测试
"""
import pytest
import time
from app.utils.cache import SimpleCache, CacheEntry


class TestCacheEntry:
    """缓存条目测试"""
    
    def test_cache_entry_creation(self):
        """测试缓存条目创建"""
        entry = CacheEntry("test_value", ttl_seconds=60)
        assert entry.value == "test_value"
        assert not entry.is_expired()
    
    def test_cache_entry_expiration(self):
        """测试缓存过期"""
        entry = CacheEntry("test_value", ttl_seconds=1)
        assert not entry.is_expired()
        
        time.sleep(1.1)
        assert entry.is_expired()


class TestSimpleCache:
    """简单缓存测试"""
    
    def test_cache_initialization(self):
        """测试缓存初始化"""
        cache = SimpleCache(max_size=100, default_ttl=300)
        assert cache.size() == 0
        assert cache._max_size == 100
        assert cache._default_ttl == 300
    
    def test_cache_set_and_get(self):
        """测试设置和获取缓存"""
        cache = SimpleCache()
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        assert cache.size() == 1
    
    def test_cache_get_nonexistent(self):
        """测试获取不存在的键"""
        cache = SimpleCache()
        assert cache.get("nonexistent") is None
    
    def test_cache_expiration(self):
        """测试缓存过期"""
        cache = SimpleCache()
        
        cache.set("key1", "value1", ttl=1)
        assert cache.get("key1") == "value1"
        
        time.sleep(1.1)
        assert cache.get("key1") is None
        assert cache.size() == 0
    
    def test_cache_update(self):
        """测试更新缓存"""
        cache = SimpleCache()
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        cache.set("key1", "value2")
        assert cache.get("key1") == "value2"
        assert cache.size() == 1
    
    def test_cache_delete(self):
        """测试删除缓存"""
        cache = SimpleCache()
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        cache.delete("key1")
        assert cache.get("key1") is None
        assert cache.size() == 0
    
    def test_cache_clear(self):
        """测试清空缓存"""
        cache = SimpleCache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        assert cache.size() == 3
        
        cache.clear()
        assert cache.size() == 0
        assert cache.get("key1") is None
    
    def test_lru_eviction(self):
        """测试LRU淘汰策略"""
        cache = SimpleCache(max_size=3)
        
        # 添加3个条目
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        assert cache.size() == 3
        
        # 添加第4个条目，应该淘汰最少使用的key1
        cache.set("key4", "value4")
        assert cache.size() == 3
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
    
    def test_lru_access_update(self):
        """测试LRU访问更新"""
        cache = SimpleCache(max_size=3)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # 访问key1，使其成为最近使用
        cache.get("key1")
        
        # 添加新条目，应该淘汰key2（最少使用）
        cache.set("key4", "value4")
        assert cache.get("key1") == "value1"  # 应该保留
        assert cache.get("key2") is None      # 应该被淘汰
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"
    
    def test_cache_complex_key(self):
        """测试复杂键（字典）"""
        cache = SimpleCache()
        
        key = {"query": "test", "mode": "semantic", "k": 5}
        cache.set(key, "result_data")
        
        # 相同的字典应该命中缓存
        assert cache.get(key) == "result_data"
        
        # 顺序不同但内容相同的字典也应该命中
        key2 = {"k": 5, "mode": "semantic", "query": "test"}
        assert cache.get(key2) == "result_data"
    
    def test_cache_stats(self):
        """测试缓存统计"""
        cache = SimpleCache(max_size=100, default_ttl=300)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        stats = cache.stats()
        assert stats["size"] == 2
        assert stats["max_size"] == 100
        assert stats["default_ttl"] == 300
        assert "oldest_entry_age" in stats
    
    def test_cache_with_different_ttls(self):
        """测试不同TTL"""
        cache = SimpleCache(default_ttl=10)
        
        cache.set("key1", "value1", ttl=1)   # 1秒过期
        cache.set("key2", "value2", ttl=60)  # 60秒过期
        cache.set("key3", "value3")          # 默认10秒
        
        time.sleep(1.1)
        
        assert cache.get("key1") is None     # 已过期
        assert cache.get("key2") == "value2"  # 未过期
        assert cache.get("key3") == "value3"  # 未过期


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
