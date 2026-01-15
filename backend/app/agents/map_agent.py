"""
地图/路线Agent - 使用高德地图API
提供路线规划、POI搜索、地理编码等功能
"""
import os
import httpx
from typing import Dict, Any, List, Optional
from app.agents.base_agent import BaseAgent
from app.core.config import settings


class MapAgent(BaseAgent):
    """地图路线Agent"""
    
    def __init__(self):
        super().__init__(
            name="MapAgent",
            description="地图和路线规划助手，提供导航、POI搜索、距离计算等服务"
        )
        self.api_key = getattr(settings, 'AMAP_API_KEY', None) or os.getenv('AMAP_API_KEY')
        self.base_url = "https://restapi.amap.com/v3"
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行地图相关任务"""
        action = input_data.get("action", "route")
        user_input = input_data.get("user_input", "")
        
        if action == "route":
            return await self._plan_route(user_input)
        elif action == "poi":
            return await self._search_poi(user_input)
        elif action == "geocode":
            return await self._geocode(user_input)
        elif action == "distance":
            return await self._calculate_distance(user_input)
        else:
            return await self._plan_route(user_input)
    
    async def _plan_route(self, query: str) -> Dict[str, Any]:
        """路线规划"""
        # 解析起点和终点
        route_info = await self._parse_route_query(query)
        
        if not route_info.get("origin") or not route_info.get("destination"):
            return {
                "success": False,
                "message": "请告诉我起点和终点，例如：'从北京到上海怎么走'"
            }
        
        # 如果没有API key，使用LLM模拟
        if not self.api_key:
            return await self._simulate_route(route_info)
        
        try:
            # 获取起点坐标
            origin_coord = await self._get_location(route_info["origin"])
            dest_coord = await self._get_location(route_info["destination"])
            
            if not origin_coord or not dest_coord:
                return {
                    "success": False,
                    "message": "无法识别地点，请检查起点和终点名称"
                }
            
            # 根据交通方式选择API
            mode = route_info.get("mode", "driving")
            
            async with httpx.AsyncClient() as client:
                if mode == "driving":
                    response = await client.get(
                        f"{self.base_url}/direction/driving",
                        params={
                            "key": self.api_key,
                            "origin": origin_coord,
                            "destination": dest_coord,
                            "strategy": 0,  # 速度优先
                        }
                    )
                elif mode == "transit":
                    response = await client.get(
                        f"{self.base_url}/direction/transit/integrated",
                        params={
                            "key": self.api_key,
                            "origin": origin_coord,
                            "destination": dest_coord,
                            "city": route_info.get("city", "北京"),
                        }
                    )
                elif mode == "walking":
                    response = await client.get(
                        f"{self.base_url}/direction/walking",
                        params={
                            "key": self.api_key,
                            "origin": origin_coord,
                            "destination": dest_coord,
                        }
                    )
                else:
                    response = await client.get(
                        f"{self.base_url}/direction/driving",
                        params={
                            "key": self.api_key,
                            "origin": origin_coord,
                            "destination": dest_coord,
                        }
                    )
                
                data = response.json()
                
                if data.get("status") == "1":
                    return await self._format_route_result(data, mode, route_info)
                else:
                    return await self._simulate_route(route_info)
                    
        except Exception as e:
            print(f"路线规划错误: {e}")
            return await self._simulate_route(route_info)
    
    async def _search_poi(self, query: str) -> Dict[str, Any]:
        """POI搜索"""
        # 解析搜索查询
        search_info = await self._parse_poi_query(query)
        
        if not self.api_key:
            return await self._simulate_poi(search_info)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/place/text",
                    params={
                        "key": self.api_key,
                        "keywords": search_info.get("keywords", ""),
                        "city": search_info.get("city", ""),
                        "citylimit": "true" if search_info.get("city") else "false",
                        "offset": 10,
                    }
                )
                
                data = response.json()
                
                if data.get("status") == "1" and data.get("pois"):
                    return self._format_poi_result(data["pois"], search_info)
                else:
                    return await self._simulate_poi(search_info)
                    
        except Exception as e:
            print(f"POI搜索错误: {e}")
            return await self._simulate_poi(search_info)
    
    async def _geocode(self, address: str) -> Dict[str, Any]:
        """地理编码（地址转坐标）"""
        if not self.api_key:
            return {
                "success": True,
                "address": address,
                "location": "116.397428,39.90923",  # 模拟坐标（天安门）
                "message": "（模拟数据）"
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/geocode/geo",
                    params={
                        "key": self.api_key,
                        "address": address,
                    }
                )
                
                data = response.json()
                
                if data.get("status") == "1" and data.get("geocodes"):
                    geo = data["geocodes"][0]
                    return {
                        "success": True,
                        "address": address,
                        "formatted_address": geo.get("formatted_address"),
                        "location": geo.get("location"),
                        "province": geo.get("province"),
                        "city": geo.get("city"),
                        "district": geo.get("district"),
                    }
                else:
                    return {"success": False, "message": "无法找到该地址"}
                    
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    async def _get_location(self, address: str) -> Optional[str]:
        """获取地址的坐标"""
        result = await self._geocode(address)
        if result.get("success"):
            return result.get("location")
        return None
    
    async def _calculate_distance(self, query: str) -> Dict[str, Any]:
        """计算距离"""
        route_info = await self._parse_route_query(query)
        
        if not route_info.get("origin") or not route_info.get("destination"):
            return {
                "success": False,
                "message": "请告诉我两个地点，例如：'北京到上海有多远'"
            }
        
        if not self.api_key:
            return await self._simulate_distance(route_info)
        
        try:
            origin_coord = await self._get_location(route_info["origin"])
            dest_coord = await self._get_location(route_info["destination"])
            
            if not origin_coord or not dest_coord:
                return await self._simulate_distance(route_info)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/distance",
                    params={
                        "key": self.api_key,
                        "origins": origin_coord,
                        "destination": dest_coord,
                        "type": 1,  # 驾车距离
                    }
                )
                
                data = response.json()
                
                if data.get("status") == "1" and data.get("results"):
                    result = data["results"][0]
                    distance = int(result.get("distance", 0))
                    duration = int(result.get("duration", 0))
                    
                    return {
                        "success": True,
                        "origin": route_info["origin"],
                        "destination": route_info["destination"],
                        "distance_km": distance / 1000,
                        "duration_min": duration / 60,
                        "message": f"从{route_info['origin']}到{route_info['destination']}，驾车距离约 {distance/1000:.1f} 公里，预计耗时 {duration//60} 分钟"
                    }
                else:
                    return await self._simulate_distance(route_info)
                    
        except Exception as e:
            return await self._simulate_distance(route_info)
    
    async def _parse_route_query(self, query: str) -> Dict[str, Any]:
        """解析路线查询"""
        system_prompt = """你是一个路线查询解析器。从用户输入中提取：
1. origin: 起点
2. destination: 终点
3. mode: 交通方式 (driving/transit/walking)
4. city: 城市（如果是同城）

返回JSON格式：
{
    "origin": "起点",
    "destination": "终点",
    "mode": "driving",
    "city": ""
}

如果用户说"开车"、"自驾"，mode为driving
如果用户说"公交"、"地铁"、"坐车"，mode为transit
如果用户说"走路"、"步行"，mode为walking

只返回JSON，不要其他内容。"""
        
        try:
            response = await self.process_with_llm(query, system_prompt)
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            if response.endswith("```"):
                response = response[:-3]
            
            import json
            return json.loads(response.strip())
        except:
            # 简单的正则匹配作为后备
            import re
            patterns = [
                r"从(.+?)到(.+?)怎么",
                r"从(.+?)到(.+?)的路线",
                r"(.+?)到(.+?)怎么走",
                r"(.+?)去(.+?)怎么走",
            ]
            
            for pattern in patterns:
                match = re.search(pattern, query)
                if match:
                    return {
                        "origin": match.group(1).strip(),
                        "destination": match.group(2).strip(),
                        "mode": "driving"
                    }
            
            return {}
    
    async def _parse_poi_query(self, query: str) -> Dict[str, Any]:
        """解析POI搜索查询"""
        system_prompt = """从用户输入中提取POI搜索信息：
1. keywords: 搜索关键词
2. city: 城市
3. type: POI类型

返回JSON格式：
{
    "keywords": "关键词",
    "city": "城市",
    "type": "类型"
}

只返回JSON。"""
        
        try:
            response = await self.process_with_llm(query, system_prompt)
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            if response.endswith("```"):
                response = response[:-3]
            
            import json
            return json.loads(response.strip())
        except:
            return {"keywords": query, "city": "", "type": ""}
    
    async def _simulate_route(self, route_info: Dict[str, Any]) -> Dict[str, Any]:
        """模拟路线规划结果"""
        origin = route_info.get("origin", "起点")
        destination = route_info.get("destination", "终点")
        mode = route_info.get("mode", "driving")
        
        mode_names = {
            "driving": "驾车",
            "transit": "公共交通",
            "walking": "步行"
        }
        
        system_prompt = f"""你是一个地图导航助手。用户想从"{origin}"到"{destination}"，选择{mode_names.get(mode, '驾车')}出行。

请提供一个合理的路线建议，包括：
1. 预估距离
2. 预估时间
3. 主要路线（如经过哪些主要道路/地铁线）
4. 注意事项

用友好的方式回复。"""
        
        response = await self.process_with_llm("", system_prompt)
        
        return {
            "success": True,
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "message": response,
            "simulated": True
        }
    
    async def _format_route_result(self, data: Dict, mode: str, route_info: Dict) -> Dict[str, Any]:
        """格式化路线结果"""
        if mode == "driving" and data.get("route"):
            route = data["route"]
            paths = route.get("paths", [])
            if paths:
                path = paths[0]
                distance = int(path.get("distance", 0))
                duration = int(path.get("duration", 0))
                
                return {
                    "success": True,
                    "origin": route_info["origin"],
                    "destination": route_info["destination"],
                    "mode": "driving",
                    "distance_km": distance / 1000,
                    "duration_min": duration / 60,
                    "tolls": path.get("tolls", "0"),
                    "message": f"🚗 从{route_info['origin']}到{route_info['destination']}\n\n"
                              f"- 📏 距离：{distance/1000:.1f} 公里\n"
                              f"- ⏱️ 预计耗时：{duration//60} 分钟\n"
                              f"- 💰 过路费：约 {path.get('tolls', '0')} 元"
                }
        
        elif mode == "transit" and data.get("route"):
            # 公交路线
            route = data["route"]
            transits = route.get("transits", [])
            if transits:
                transit = transits[0]
                distance = int(transit.get("distance", 0))
                duration = int(transit.get("duration", 0))
                cost = transit.get("cost", "0")
                
                return {
                    "success": True,
                    "origin": route_info["origin"],
                    "destination": route_info["destination"],
                    "mode": "transit",
                    "distance_km": distance / 1000,
                    "duration_min": duration / 60,
                    "cost": cost,
                    "message": f"🚌 公共交通路线\n\n"
                              f"- 📏 距离：{distance/1000:.1f} 公里\n"
                              f"- ⏱️ 预计耗时：{duration//60} 分钟\n"
                              f"- 💰 费用：约 {cost} 元"
                }
        
        return await self._simulate_route(route_info)
    
    def _format_poi_result(self, pois: List[Dict], search_info: Dict) -> Dict[str, Any]:
        """格式化POI结果"""
        results = []
        for poi in pois[:5]:
            results.append({
                "name": poi.get("name"),
                "address": poi.get("address"),
                "type": poi.get("type"),
                "tel": poi.get("tel"),
                "distance": poi.get("distance"),
            })
        
        message_lines = [f"📍 搜索结果：{search_info.get('keywords', '')}\n"]
        for i, r in enumerate(results, 1):
            message_lines.append(f"{i}. **{r['name']}**")
            if r['address']:
                message_lines.append(f"   📍 {r['address']}")
            if r['tel']:
                message_lines.append(f"   📞 {r['tel']}")
            message_lines.append("")
        
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "message": "\n".join(message_lines)
        }
    
    async def _simulate_poi(self, search_info: Dict) -> Dict[str, Any]:
        """模拟POI搜索结果"""
        keywords = search_info.get("keywords", "")
        city = search_info.get("city", "")
        
        system_prompt = f"""你是一个地图搜索助手。用户在{city or '附近'}搜索"{keywords}"。

请提供3-5个相关的地点推荐，每个包含：
- 名称
- 大致地址
- 简短描述

用友好的列表方式回复。"""
        
        response = await self.process_with_llm("", system_prompt)
        
        return {
            "success": True,
            "keywords": keywords,
            "city": city,
            "message": response,
            "simulated": True
        }
    
    async def _simulate_distance(self, route_info: Dict) -> Dict[str, Any]:
        """模拟距离计算"""
        origin = route_info.get("origin", "")
        destination = route_info.get("destination", "")
        
        system_prompt = f"""你是一个地图助手。用户想知道从"{origin}"到"{destination}"的距离。

请提供：
1. 大约距离（公里）
2. 驾车预计时间
3. 其他交通方式的建议

用简洁友好的方式回复。"""
        
        response = await self.process_with_llm("", system_prompt)
        
        return {
            "success": True,
            "origin": origin,
            "destination": destination,
            "message": response,
            "simulated": True
        }
