"""知识图谱Agent - 负责知识图谱的构建和查询"""
from typing import Dict, Any, List
import json
from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.db.models import KnowledgeNode, KnowledgeRelation


class KnowledgeGraphAgent(BaseAgent):
    """知识图谱Agent，负责知识的结构化存储和图谱查询"""
    
    def __init__(self):
        super().__init__(
            name="KnowledgeGraphAgent",
            description="负责构建和查询知识图谱，支持实体识别、关系抽取和图谱推理"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行知识图谱任务"""
        action = input_data.get("action", "extract")
        user_input = input_data.get("user_input", "")
        db = input_data.get("db")
        
        if action == "extract":
            return await self._extract_knowledge(user_input, db)
        elif action == "query":
            return await self._query_graph(user_input, db)
        elif action == "build":
            return await self._build_graph(user_input, db)
        else:
            return {"success": False, "error": "不支持的操作"}
    
    async def _extract_knowledge(self, text: str, db) -> Dict[str, Any]:
        """从文本中提取知识（实体和关系）"""
        system_prompt = """你是一个知识抽取专家。从文本中提取实体和关系，构建知识图谱。

返回格式：
{
    "entities": [
        {
            "name": "实体名称",
            "type": "实体类型（人物/组织/概念/事件等）",
            "properties": {
                "key": "value"
            }
        }
    ],
    "relations": [
        {
            "source": "源实体",
            "target": "目标实体",
            "relation": "关系类型",
            "properties": {
                "key": "value"
            }
        }
    ]
}"""

        prompt = f"文本内容：\n{text}\n\n请提取知识图谱（JSON格式）。"
        
        try:
            response = await self.process_with_llm(prompt, system_prompt)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            knowledge = json.loads(response)
            
            # 保存实体到数据库
            saved_entities = []
            for entity in knowledge.get("entities", []):
                node = KnowledgeNode(
                    name=entity["name"],
                    entity_type=entity["type"],
                    properties=json.dumps(entity.get("properties", {}), ensure_ascii=False)
                )
                db.add(node)
                saved_entities.append(entity["name"])
            
            # 保存关系到数据库
            saved_relations = []
            for relation in knowledge.get("relations", []):
                # 查找或创建源实体和目标实体
                source_node = db.query(KnowledgeNode).filter(
                    KnowledgeNode.name == relation["source"]
                ).first()
                target_node = db.query(KnowledgeNode).filter(
                    KnowledgeNode.name == relation["target"]
                ).first()
                
                if source_node and target_node:
                    rel = KnowledgeRelation(
                        source_id=source_node.id,
                        target_id=target_node.id,
                        relation_type=relation["relation"],
                        properties=json.dumps(relation.get("properties", {}), ensure_ascii=False)
                    )
                    db.add(rel)
                    saved_relations.append(f"{relation['source']} -> {relation['relation']} -> {relation['target']}")
            
            db.commit()
            
            return {
                "success": True,
                "message": "知识抽取成功",
                "entities": saved_entities,
                "relations": saved_relations,
                "count": {
                    "entities": len(saved_entities),
                    "relations": len(saved_relations)
                }
            }
        except Exception as e:
            return {"success": False, "error": f"知识抽取失败: {str(e)}"}
    
    async def _query_graph(self, query: str, db) -> Dict[str, Any]:
        """查询知识图谱"""
        system_prompt = """你是一个知识图谱查询专家。根据用户查询，生成图谱查询策略。

返回格式：
{
    "query_type": "entity_search/relation_search/path_search",
    "target_entity": "目标实体",
    "relation_type": "关系类型",
    "depth": 2
}"""

        prompt = f"用户查询：{query}\n\n请生成查询策略（JSON格式）。"
        
        try:
            response = await self.process_with_llm(prompt, system_prompt)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            query_strategy = json.loads(response)
            
            # 执行图谱查询
            target = query_strategy.get("target_entity")
            nodes = db.query(KnowledgeNode).filter(
                KnowledgeNode.name.contains(target)
            ).limit(10).all()
            
            results = []
            for node in nodes:
                # 查找该节点的所有关系
                outgoing = db.query(KnowledgeRelation).filter(
                    KnowledgeRelation.source_id == node.id
                ).all()
                
                incoming = db.query(KnowledgeRelation).filter(
                    KnowledgeRelation.target_id == node.id
                ).all()
                
                results.append({
                    "entity": node.name,
                    "type": node.entity_type,
                    "outgoing_relations": len(outgoing),
                    "incoming_relations": len(incoming)
                })
            
            return {
                "success": True,
                "query_strategy": query_strategy,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"success": False, "error": f"图谱查询失败: {str(e)}"}
    
    async def _build_graph(self, topic: str, db) -> Dict[str, Any]:
        """根据主题构建知识图谱"""
        system_prompt = """你是一个知识图谱构建专家。根据主题，生成完整的知识图谱结构。

包括：
1. 核心概念和实体
2. 实体间的关系
3. 属性和特征
4. 层次结构"""

        prompt = f"主题：{topic}\n\n请构建知识图谱并返回JSON格式的实体和关系。"
        
        try:
            response = await self.process_with_llm(prompt, system_prompt)
            # 解析并保存知识图谱
            return await self._extract_knowledge(response, db)
        except Exception as e:
            return {"success": False, "error": f"构建图谱失败: {str(e)}"}
