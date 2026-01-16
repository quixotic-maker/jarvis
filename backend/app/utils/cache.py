"""
简单的内存缓存实现
用于缓存RAG搜索结果
"""
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import hashlib
import json


class CacheEntry:
    """缓存条目"""
    
    def __init__(self, value: Any, ttl_seconds: int = 300):
        self.value = value
        self.created_at = datetime.now()
        self.ttl = timedelta(seconds=ttl_seconds)
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return datetime.now() - self.created_at > self.ttl


class SimpleCache:
    """
    简单的内存缓存
    
    特性:
    - TTL支持（自动过期）
    - LRU淘汰策略
    - 最大容量限制
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        初始化缓存
        
        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认TTL（秒）
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._access_order: list = []  # 记录访问顺序，用于LRU
    
    def _make_key(self, key: Any) -> str:
        """
        生成缓存键
        
        Args:
            key: 任意可序列化的对象
            
        Returns:
            str: MD5哈希键
        """
        if isinstance(key, str):
            key_str = key
        else:
            key_str = json.dumps(key, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: Any) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[Any]: 缓存值，如果不存在或已过期返回None
        """
        cache_key = self._make_key(key)
        
        if cache_key not in self._cache:
            return None
        
        entry = self._cache[cache_key]
        
        # 检查是否过期
        if entry.is_expired():
            del self._cache[cache_key]
            if cache_key in self._access_order:
                self._access_order.remove(cache_key)
            return None
        
        # 更新访问顺序（LRU）
        if cache_key in self._access_order:
            self._access_order.remove(cache_key)
        self._access_order.append(cache_key)
        
        return entry.value
    
    def set(self, key: Any, value: Any, ttl: Optional[int] = None):
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: TTL（秒），None则使用默认值
        """
        cache_key = self._make_key(key)
        ttl_seconds = ttl if ttl is not None else self._default_ttl
        
        # 如果达到最大容量，移除最少使用的条目
        if len(self._cache) >= self._max_size and cache_key not in self._cache:
            if self._access_order:
                lru_key = self._access_order.pop(0)
                del self._cache[lru_key]
        
        # 添加新条目
        self._cache[cache_key] = CacheEntry(value, ttl_seconds)
        
        # 更新访问顺序
        if cache_key in self._access_order:
            self._access_order.remove(cache_key)
        self._access_order.append(cache_key)
    
    def delete(self, key: Any):
        """删除缓存条目"""
        cache_key = self._make_key(key)
        if cache_key in self._cache:
            del self._cache[cache_key]
        if cache_key in self._access_order:
            self._access_order.remove(cache_key)
    
    def clear(self):
        """清空所有缓存"""
        self._cache.clear()
        self._access_order.clear()
    
    def size(self) -> int:
        """返回当前缓存条目数"""
        return len(self._cache)
    
    def stats(self) -> Dict[str, Any]:
        """返回缓存统计信息"""
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "default_ttl": self._default_ttl,
            "oldest_entry_age": (
                (datetime.now() - self._cache[self._access_order[0]].created_at).total_seconds()
                if self._access_order else 0
            )
        }


# 全局缓存实例
_search_cache = SimpleCache(max_size=500, default_ttl=300)  # 5分钟TTL


def get_search_cache() -> SimpleCache:
    """获取搜索结果缓存实例"""
    return _search_cache
