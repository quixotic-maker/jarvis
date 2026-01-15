"""Agentic RAG Agent - 高级检索增强生成"""
from typing import Dict, Any, List
import json

from app.agents.base_agent import BaseAgent
from app.db.models import DocumentChunk


class AgenticRAGAgent(BaseAgent):
    """
    Agentic RAG Agent - 主动式检索增强生成
    
    相比传统RAG，Agentic RAG具有以下特点：
    1. 自主查询规划 - 智能分解复杂查询
    2. 迭代检索 - 多轮检索优化结果
    3. 自我反思 - 评估检索质量并调整
    4. 推理链 - 构建逻辑推理路径
    5. 工具调用 - 主动调用其他Agent获取信息
    """
    
    def __init__(self):
        super().__init__(
            name="AgenticRAGAgent",
            description="主动式检索增强生成，支持查询规划、迭代检索、自我反思和多Agent协作"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行Agentic RAG任务"""
        user_input = input_data.get("user_input", "")
        db = input_data.get("db")
        max_iterations = input_data.get("max_iterations", 3)
        
        return await self._agentic_rag_pipeline(user_input, db, max_iterations)
    
    async def _agentic_rag_pipeline(self, query: str, db, max_iterations: int) -> Dict[str, Any]:
        """Agentic RAG完整流程"""
        
        # 第1步：查询规划 - 分解复杂查询
        query_plan = await self._plan_query(query)
        
        # 第2步：迭代检索 - 多轮检索和优化
        retrieved_contexts = []
        reasoning_chain = []
        
        for iteration in range(max_iterations):
            # 执行检索
            search_result = await self._retrieve_documents(
                query, 
                query_plan.get("sub_queries", [query]),
                db
            )
            
            retrieved_contexts.append(search_result)
            
            # 自我反思 - 评估检索质量
            reflection = await self._self_reflect(query, search_result)
            reasoning_chain.append({
                "iteration": iteration + 1,
                "retrieved_docs": len(search_result.get("chunks", [])),
                "reflection": reflection
            })
            
            # 如果质量满意，跳出循环
            if reflection.get("quality_score", 0) >= 0.8:
                break
            
            # 否则，优化查询策略
            if iteration < max_iterations - 1:
                query_plan = await self._refine_query_plan(query, reflection)
        
        # 第3步：整合上下文
        integrated_context = self._integrate_contexts(retrieved_contexts)
        
        # 第4步：推理生成答案
        answer = await self._reason_and_generate(query, integrated_context, reasoning_chain)
        
        return {
            "success": True,
            "answer": answer.get("response"),
            "reasoning_chain": reasoning_chain,
            "query_plan": query_plan,
            "iterations": len(reasoning_chain),
            "sources": integrated_context.get("sources", []),
            "confidence": answer.get("confidence", 0.0)
        }
    
    async def _plan_query(self, query: str) -> Dict[str, Any]:
        """查询规划 - 智能分解复杂查询"""
        system_prompt = """你是一个查询规划专家。分析用户查询，制定检索策略。

返回格式：
{
    "query_type": "simple/complex/multi-hop",
    "sub_queries": ["子查询1", "子查询2"],
    "search_strategy": "broad/precise/hierarchical",
    "required_info": ["需要的信息1", "需要的信息2"],
    "reasoning_steps": ["推理步骤1", "推理步骤2"]
}"""

        prompt = f"用户查询：{query}\n\n请制定查询计划（JSON格式）。"
        
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
            
            return json.loads(response)
        except Exception as e:
            return {
                "query_type": "simple",
                "sub_queries": [query],
                "search_strategy": "broad"
            }
    
    async def _retrieve_documents(self, original_query: str, sub_queries: List[str], db) -> Dict[str, Any]:
        """检索文档 - 支持多个子查询"""
        all_chunks = []
        
        for sub_query in sub_queries:
            chunks = db.query(DocumentChunk).filter(
                DocumentChunk.content.contains(sub_query) | 
                DocumentChunk.keywords.contains(sub_query)
            ).limit(3).all()
            
            all_chunks.extend(chunks)
        
        # 去重
        unique_chunks = list({chunk.id: chunk for chunk in all_chunks}.values())
        
        return {
            "chunks": [{
                "id": chunk.id,
                "content": chunk.content,
                "summary": chunk.summary,
                "keywords": chunk.keywords
            } for chunk in unique_chunks],
            "total": len(unique_chunks)
        }
    
    async def _self_reflect(self, query: str, search_result: Dict[str, Any]) -> Dict[str, Any]:
        """自我反思 - 评估检索质量"""
        chunks = search_result.get("chunks", [])
        
        if not chunks:
            return {
                "quality_score": 0.0,
                "issues": ["未找到相关文档"],
                "suggestions": ["扩大搜索范围", "尝试同义词"]
            }
        
        # 构建反思提示
        context_preview = "\n".join([
            f"{i+1}. {chunk['summary']}" 
            for i, chunk in enumerate(chunks[:3])
        ])
        
        system_prompt = """你是一个检索质量评估专家。评估检索结果的相关性和完整性。

返回格式：
{
    "quality_score": 0.85,
    "relevance": "high/medium/low",
    "coverage": "complete/partial/insufficient",
    "issues": ["问题1", "问题2"],
    "suggestions": ["改进建议1", "改进建议2"]
}"""

        prompt = f"""用户查询：{query}

检索到的文档摘要：
{context_preview}

请评估检索质量（JSON格式）。"""
        
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
            
            return json.loads(response)
        except Exception as e:
            return {
                "quality_score": 0.5,
                "relevance": "medium",
                "coverage": "partial"
            }
    
    async def _refine_query_plan(self, original_query: str, reflection: Dict[str, Any]) -> Dict[str, Any]:
        """优化查询计划 - 基于反思结果"""
        suggestions = reflection.get("suggestions", [])
        
        system_prompt = """你是一个查询优化专家。根据反思结果，优化检索策略。

返回优化后的查询计划（JSON格式）。"""

        prompt = f"""原始查询：{original_query}

反思结果：
- 质量分数：{reflection.get('quality_score', 0)}
- 问题：{', '.join(reflection.get('issues', []))}
- 建议：{', '.join(suggestions)}

请生成优化后的查询计划。"""
        
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
            
            return json.loads(response)
        except Exception as e:
            return {"sub_queries": [original_query]}
    
    def _integrate_contexts(self, retrieved_contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """整合多轮检索的上下文"""
        all_chunks = []
        for context in retrieved_contexts:
            all_chunks.extend(context.get("chunks", []))
        
        # 去重
        unique_chunks = list({chunk["id"]: chunk for chunk in all_chunks}.values())
        
        return {
            "chunks": unique_chunks,
            "sources": [{
                "id": chunk["id"],
                "summary": chunk["summary"]
            } for chunk in unique_chunks]
        }
    
    async def _reason_and_generate(self, query: str, context: Dict[str, Any], reasoning_chain: List[Dict]) -> Dict[str, Any]:
        """推理和生成最终答案"""
        chunks = context.get("chunks", [])
        
        # 构建丰富的上下文
        context_text = "\n\n".join([
            f"文档{i+1}:\n{chunk['content']}\n摘要: {chunk['summary']}"
            for i, chunk in enumerate(chunks)
        ])
        
        # 构建推理链文本
        reasoning_text = "\n".join([
            f"迭代{step['iteration']}: 检索到{step['retrieved_docs']}个文档，质量分数: {step['reflection'].get('quality_score', 0)}"
            for step in reasoning_chain
        ])
        
        system_prompt = """你是一个高级推理助手。基于检索到的文档和推理链，生成全面准确的答案。

要求：
1. 综合多个文档信息
2. 展示推理过程
3. 引用具体来源
4. 评估答案可信度
5. 指出不确定的地方

返回格式：
{
    "response": "详细答案",
    "reasoning_process": "推理过程说明",
    "confidence": 0.9,
    "sources_used": [1, 2, 3],
    "uncertainties": ["不确定点1"]
}"""

        prompt = f"""用户问题：{query}

检索过程：
{reasoning_text}

相关文档：
{context_text}

请基于以上信息生成答案（JSON格式）。"""
        
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
            
            return json.loads(response)
        except Exception as e:
            return {
                "response": "生成答案时出现错误",
                "confidence": 0.0,
                "error": str(e)
            }
