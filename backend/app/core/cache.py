"""Redis缓存管理（可选模块）"""
from typing import Optional, Any
import json
from app.core.config import settings

# Redis客户端（延迟初始化）
_redis_client = None


def get_redis_client():
    """获取Redis客户端（单例模式）"""
    global _redis_client
    
    if not settings.REDIS_ENABLED:
        return None
    
    if _redis_client is None:
        try:
            import redis
            _redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # 测试连接
            _redis_client.ping()
            print("✅ Redis连接成功")
        except Exception as e:
            print(f"⚠️ Redis连接失败: {e}")
            print("   系统将继续运行（不使用缓存）")
            return None
    
    return _redis_client


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.client = get_redis_client()
        self.default_ttl = 3600  # 默认缓存1小时
    
    @property
    def is_available(self) -> bool:
        """检查缓存是否可用"""
        return self.client is not None
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not self.is_available:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"⚠️ 缓存读取失败: {e}")
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        if not self.is_available:
            return False
        
        try:
            self.client.setex(
                key,
                ttl or self.default_ttl,
                json.dumps(value, ensure_ascii=False)
            )
            return True
        except Exception as e:
            print(f"⚠️ 缓存写入失败: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.is_available:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"⚠️ 缓存删除失败: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存"""
        if not self.is_available:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            print(f"⚠️ 批量删除缓存失败: {e}")
            return 0


# 全局缓存管理器实例
cache = CacheManager()


# 缓存装饰器
def cached(key_prefix: str, ttl: int = 3600):
    """缓存装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存key
            cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            await cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
