"""天气Agent - 负责天气查询和预报"""
from typing import Dict, Any
import json
import aiohttp
import logging

from app.agents.base_agent import BaseAgent
from app.core.config import settings

logger = logging.getLogger(__name__)


class WeatherAgent(BaseAgent):
    """天气Agent，支持和风天气API"""
    
    def __init__(self):
        super().__init__(
            name="WeatherAgent",
            description="负责天气查询、预报和天气相关建议"
        )
        self.api_key = settings.QWEATHER_API_KEY
        self.base_url = settings.QWEATHER_BASE_URL
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行天气查询任务"""
        user_input = input_data.get("user_input", "")
        
        # 从用户输入中提取城市
        city = await self._extract_city(user_input)
        
        if self.api_key:
            # 使用真实API
            return await self._get_real_weather(city)
        else:
            # 使用LLM模拟
            return await self._get_mock_weather(user_input, city)
    
    async def _extract_city(self, user_input: str) -> str:
        """从用户输入中提取城市名称"""
        # 常见城市列表
        common_cities = [
            "北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "重庆",
            "武汉", "西安", "苏州", "天津", "长沙", "郑州", "青岛", "厦门"
        ]
        
        for city in common_cities:
            if city in user_input:
                return city
        
        # 使用LLM提取
        try:
            system_prompt = "从用户输入中提取城市名称，只返回城市名，不要其他内容。如果没有明确城市，返回'北京'。"
            response = await self.process_with_llm(user_input, system_prompt)
            return response.strip().replace("市", "")
        except:
            return "北京"
    
    async def _get_real_weather(self, city: str) -> Dict[str, Any]:
        """调用和风天气API获取真实天气"""
        try:
            # 1. 先查询城市ID
            location_id = await self._get_location_id(city)
            if not location_id:
                return await self._get_mock_weather(f"查询{city}天气", city)
            
            async with aiohttp.ClientSession() as session:
                # 2. 获取实时天气
                now_url = f"{self.base_url}/weather/now"
                params = {"location": location_id, "key": self.api_key}
                
                async with session.get(now_url, params=params) as resp:
                    if resp.status != 200:
                        raise Exception(f"API请求失败: {resp.status}")
                    now_data = await resp.json()
                
                # 3. 获取3天预报
                forecast_url = f"{self.base_url}/weather/3d"
                async with session.get(forecast_url, params=params) as resp:
                    if resp.status != 200:
                        raise Exception(f"API请求失败: {resp.status}")
                    forecast_data = await resp.json()
                
                # 解析数据
                if now_data.get("code") != "200" or forecast_data.get("code") != "200":
                    raise Exception("API返回错误")
                
                current = now_data.get("now", {})
                daily = forecast_data.get("daily", [])
                
                weather = {
                    "location": city,
                    "current": {
                        "temperature": int(current.get("temp", 0)),
                        "feels_like": int(current.get("feelsLike", 0)),
                        "condition": current.get("text", "未知"),
                        "humidity": int(current.get("humidity", 0)),
                        "wind_dir": current.get("windDir", ""),
                        "wind_speed": current.get("windSpeed", ""),
                        "icon": current.get("icon", ""),
                    },
                    "forecast": [
                        {
                            "date": day.get("fxDate", ""),
                            "condition_day": day.get("textDay", ""),
                            "condition_night": day.get("textNight", ""),
                            "high": int(day.get("tempMax", 0)),
                            "low": int(day.get("tempMin", 0)),
                            "humidity": int(day.get("humidity", 0)),
                        }
                        for day in daily[:3]
                    ]
                }
                
                # 生成建议
                suggestion = self._generate_suggestion(weather)
                weather["suggestion"] = suggestion
                
                return {
                    "success": True,
                    "weather": weather,
                    "source": "和风天气API"
                }
                
        except Exception as e:
            logger.error(f"获取天气失败: {e}")
            return await self._get_mock_weather(f"查询{city}天气", city)
    
    async def _get_location_id(self, city: str) -> str:
        """获取城市LocationID"""
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://geoapi.qweather.com/v2/city/lookup"
                params = {"location": city, "key": self.api_key}
                
                async with session.get(url, params=params) as resp:
                    if resp.status != 200:
                        return None
                    data = await resp.json()
                    
                    if data.get("code") == "200" and data.get("location"):
                        return data["location"][0]["id"]
                    return None
        except:
            return None
    
    def _generate_suggestion(self, weather: Dict) -> str:
        """根据天气生成建议"""
        current = weather.get("current", {})
        temp = current.get("temperature", 20)
        condition = current.get("condition", "")
        humidity = current.get("humidity", 50)
        
        suggestions = []
        
        # 温度建议
        if temp < 10:
            suggestions.append("天气较冷，注意保暖，建议穿厚外套")
        elif temp < 20:
            suggestions.append("天气凉爽，建议穿薄外套")
        elif temp < 30:
            suggestions.append("天气舒适，适合户外活动")
        else:
            suggestions.append("天气炎热，注意防暑，多喝水")
        
        # 天气状况建议
        if "雨" in condition:
            suggestions.append("外出记得带伞")
        elif "雪" in condition:
            suggestions.append("注意路面湿滑，小心出行")
        elif "霾" in condition or "雾" in condition:
            suggestions.append("空气质量较差，建议戴口罩")
        
        # 湿度建议
        if humidity > 80:
            suggestions.append("湿度较大，衣物不易干燥")
        elif humidity < 30:
            suggestions.append("空气干燥，注意补水保湿")
        
        return "；".join(suggestions) if suggestions else "天气正常，祝您愉快！"
    
    async def _get_mock_weather(self, user_input: str, city: str) -> Dict[str, Any]:
        """使用LLM生成模拟天气数据"""
        system_prompt = f"""你是一个天气助手。根据用户查询提供天气信息。
当前城市：{city}
当前日期：2026年1月15日

请生成真实合理的天气数据，返回JSON格式：
{{
    "location": "{city}",
    "current": {{
        "temperature": 温度数值,
        "feels_like": 体感温度,
        "condition": "天气状况",
        "humidity": 湿度百分比,
        "wind_dir": "风向",
        "wind_speed": "风速km/h"
    }},
    "forecast": [
        {{"date": "2026-01-15", "condition_day": "白天天气", "condition_night": "夜间天气", "high": 最高温, "low": 最低温}},
        {{"date": "2026-01-16", "condition_day": "白天天气", "condition_night": "夜间天气", "high": 最高温, "low": 最低温}},
        {{"date": "2026-01-17", "condition_day": "白天天气", "condition_night": "夜间天气", "high": 最高温, "low": 最低温}}
    ],
    "suggestion": "穿衣和出行建议"
}}"""

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
            
            weather_data = json.loads(response)
            
            return {
                "success": True,
                "weather": weather_data,
                "source": "AI生成（演示模式）",
                "note": "如需真实天气数据，请配置QWEATHER_API_KEY"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"查询天气失败: {str(e)}"
            }
