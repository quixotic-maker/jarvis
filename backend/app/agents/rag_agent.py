"""RAG Agent - 检索增强生成"""
from typing import Dict, Any, List
import json
from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.db.models import DocumentChunk, VectorEmbedding


class RAGAgent(BaseAgent):
    """RAG Agent，负责文档检索和增强生成"""
    
    def __init__(self):
        super().__init__(
            name="RAGAgent",
            description="检索增强生成Agent，支持文档索引、语义检索和上下文增强回答"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行RAG任务"""
        action = input_data.get("action", "query")
        user_input = input_data.get("user_input", "")
        db = input_data.get("db")
        
        if action == "index":
            return await self._index_document(user_input, db)
        elif action == "query":
            return await self._rag_query(user_input, db)
        else:
            return {"success": False, "error": "不支持的操作"}
    
    async def _index_document(self, document: str, db) -> Dict[str, Any]:
        """索引文档（分块和向量化）"""
        system_prompt = """你是一个文档分析专家。将长文档切分成语义完整的片段。

返回格式：
{
    "chunks": [
        {
            "content": "片段内容",
            "summary": "片段摘要",
            "keywords": ["关键词1", "关键词2"]
        }
    ],
    "metadata": {
        "title": "文档标题",
        "category": "分类"
    }
}"""

        prompt = f"文档内容：\n{document}\n\n请进行智能分块（JSON格式）。"
        
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
            
            doc_data = json.loads(response)
            
            # 保存文档片段
            chunk_ids = []
            for i, chunk in enumerate(doc_data.get("chunks", [])):
                doc_chunk = DocumentChunk(
                    content=chunk["content"],
                    summary=chunk.get("summary", ""),
                    keywords=",".join(chunk.get("keywords", [])),
                    doc_metadata=json.dumps(doc_data.get("metadata", {}), ensure_ascii=False),
                    chunk_index=i
                )
                db.add(doc_chunk)
                db.flush()
                chunk_ids.append(doc_chunk.id)
            
            db.commit()
            
            return {
                "success": True,
                "message": "文档索引成功",
                "chunks_count": len(chunk_ids),
                "chunk_ids": chunk_ids
            }
        except Exception as e:
            return {"success": False, "error": f"文档索引失败: {str(e)}"}
    
    async def _rag_query(self, query: str, db) -> Dict[str, Any]:
        """RAG查询（检索+生成）"""
        # 1. 检索相关文档片段
        chunks = db.query(DocumentChunk).filter(
            DocumentChunk.content.contains(query) | 
            DocumentChunk.keywords.contains(query)
        ).limit(5).all()
        
        if not chunks:
            return {
                "success": True,
                "answer": "未找到相关文档，无法提供基于文档的回答。",
                "sources": []
            }
        
        # 2. 构建增强上下文
        context = "\n\n".join([
            f"文档片段{i+1}:\n{chunk.content}\n摘要: {chunk.summary}"
            for i, chunk in enumerate(chunks)
        ])
        
        # 3. 使用LLM生成增强回答
        system_prompt = """你是一个知识助手。基于提供的文档片段回答用户问题。

要求：
1. 回答要准确，基于文档内容
2. 如果文档中没有相关信息，明确说明
3. 引用具体的文档片段
4. 提供完整的解释"""

        prompt = f"""用户问题：{query}

相关文档：
{context}

请基于以上文档回答问题。"""
        
        try:
            answer = await self.process_with_llm(prompt, system_prompt)
            
            return {
                "success": True,
                "answer": answer,
                "sources": [{
                    "chunk_id": chunk.id,
                    "summary": chunk.summary,
                    "keywords": chunk.keywords
                } for chunk in chunks],
                "retrieved_chunks": len(chunks)
            }
        except Exception as e:
            return {"success": False, "error": f"RAG查询失败: {str(e)}"}
