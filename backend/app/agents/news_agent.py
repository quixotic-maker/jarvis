"""新闻Agent - 负责新闻资讯获取"""
from typing import Dict, Any, List
import json
import aiohttp
import logging
from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.core.config import settings

logger = logging.getLogger(__name__)


class NewsAgent(BaseAgent):
    """新闻Agent，支持NewsAPI"""
    
    def __init__(self):
        super().__init__(
            name="NewsAgent",
            description="负责新闻获取、资讯推荐"
        )
        self.api_key = settings.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行新闻获取任务"""
        user_input = input_data.get("user_input", "")
        
        # 分析用户需求
        category, keyword = await self._parse_request(user_input)
        
        if self.api_key:
            return await self._get_real_news(category, keyword)
        else:
            return await self._get_mock_news(user_input, category)
    
    async def _parse_request(self, user_input: str) -> tuple:
        """解析用户请求"""
        # 新闻分类映射
        categories = {
            "科技": "technology",
            "技术": "technology",
            "AI": "technology",
            "人工智能": "technology",
            "财经": "business",
            "商业": "business",
            "金融": "business",
            "股票": "business",
            "娱乐": "entertainment",
            "体育": "sports",
            "健康": "health",
            "科学": "science",
        }
        
        # 查找分类
        category = "general"
        for key, value in categories.items():
            if key in user_input:
                category = value
                break
        
        # 提取关键词
        keyword = None
        keywords_to_check = ["关于", "有关", "查找", "搜索"]
        for kw in keywords_to_check:
            if kw in user_input:
                idx = user_input.find(kw) + len(kw)
                keyword = user_input[idx:].strip()[:20]  # 限制长度
                break
        
        return category, keyword
    
    async def _get_real_news(self, category: str, keyword: str = None) -> Dict[str, Any]:
        """调用NewsAPI获取真实新闻"""
        try:
            async with aiohttp.ClientSession() as session:
                if keyword:
                    # 搜索特定关键词
                    url = f"{self.base_url}/everything"
                    params = {
                        "q": keyword,
                        "sortBy": "publishedAt",
                        "pageSize": 5,
                        "apiKey": self.api_key,
                        "language": "zh"
                    }
                else:
                    # 按分类获取头条
                    url = f"{self.base_url}/top-headlines"
                    params = {
                        "category": category,
                        "country": "cn",
                        "pageSize": 5,
                        "apiKey": self.api_key
                    }
                
                async with session.get(url, params=params) as resp:
                    if resp.status != 200:
                        raise Exception(f"API请求失败: {resp.status}")
                    data = await resp.json()
                
                if data.get("status") != "ok":
                    raise Exception(data.get("message", "API返回错误"))
                
                articles = data.get("articles", [])
                news_list = [
                    {
                        "title": a.get("title", ""),
                        "description": a.get("description", "")[:200] if a.get("description") else "",
                        "source": a.get("source", {}).get("name", ""),
                        "url": a.get("url", ""),
                        "published_at": a.get("publishedAt", ""),
                        "image": a.get("urlToImage", "")
                    }
                    for a in articles[:5]
                ]
                
                return {
                    "success": True,
                    "category": category,
                    "keyword": keyword,
                    "news": news_list,
                    "count": len(news_list),
                    "source": "NewsAPI"
                }
                
        except Exception as e:
            logger.error(f"获取新闻失败: {e}")
            return await self._get_mock_news(f"获取{category}新闻", category)
    
    async def _get_mock_news(self, user_input: str, category: str) -> Dict[str, Any]:
        """使用LLM生成模拟新闻"""
        category_names = {
            "technology": "科技",
            "business": "财经",
            "entertainment": "娱乐",
            "sports": "体育",
            "health": "健康",
            "science": "科学",
            "general": "综合"
        }
        
        cat_name = category_names.get(category, "综合")
        
        system_prompt = f"""你是一个新闻助手。根据用户请求生成{cat_name}类新闻摘要。
当前日期：2026年1月15日

请生成5条真实合理的新闻，返回JSON格式：
{{
    "category": "{category}",
    "news": [
        {{
            "title": "新闻标题",
            "description": "新闻摘要（50-100字）",
            "source": "来源媒体",
            "published_at": "2026-01-15T10:00:00Z"
        }}
    ]
}}

注意：新闻内容要符合当前时间，可以是关于AI、科技发展、商业动态等话题。"""

        try:
            response = await self.process_with_llm(user_input, system_prompt)
            
            # 清理JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            news_data = json.loads(response)
            
            return {
                "success": True,
                "category": category,
                "news": news_data.get("news", []),
                "count": len(news_data.get("news", [])),
                "source": "AI生成（演示模式）",
                "note": "如需真实新闻，请配置NEWS_API_KEY"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"获取新闻失败: {str(e)}"
            }
