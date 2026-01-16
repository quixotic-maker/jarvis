"""
Knowledge Base API Endpoints
提供知识库管理的RESTful API
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from pathlib import Path
import tempfile
import shutil

from app.rag import (
    get_knowledge_base,
    list_knowledge_bases,
    RetrievalMode
)
from app.utils.logger import logger

router = APIRouter(prefix="/api/knowledge-base", tags=["知识库"])


# ============================================================================
# Pydantic Models
# ============================================================================

class KnowledgeBaseCreate(BaseModel):
    """创建知识库请求"""
    name: str = Field(..., description="知识库名称")
    description: str = Field("", description="知识库描述")
    chunk_size: int = Field(800, ge=100, le=2000, description="分块大小")
    chunk_overlap: int = Field(150, ge=0, le=500, description="分块重叠")


class KnowledgeBaseInfo(BaseModel):
    """知识库信息响应"""
    name: str
    description: str
    document_count: int
    metadata: Dict[str, Any]


class DocumentInfo(BaseModel):
    """文档信息"""
    id: str
    content_preview: str
    content_length: int
    metadata: Dict[str, Any]


class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., description="查询文本")
    mode: str = Field("hybrid", description="检索模式: semantic/keyword/hybrid/rerank")
    k: int = Field(5, ge=1, le=20, description="返回数量")
    filter_metadata: Optional[Dict[str, Any]] = Field(None, description="元数据过滤")


class SearchResult(BaseModel):
    """搜索结果"""
    document_id: str
    content: str
    score: float
    rank: int
    metadata: Dict[str, Any]


class AddTextRequest(BaseModel):
    """添加文本请求"""
    text: str = Field(..., description="文本内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class BatchImportRequest(BaseModel):
    """批量导入请求"""
    directory: str = Field(..., description="目录路径")
    file_patterns: List[str] = Field(["*.txt", "*.md", "*.pdf"], description="文件模式")
    recursive: bool = Field(True, description="递归扫描")


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/", response_model=List[str])
async def list_knowledge_bases_api():
    """
    列出所有知识库
    
    Returns:
        List[str]: 知识库名称列表
    """
    try:
        kb_names = list_knowledge_bases()
        return kb_names
    except Exception as e:
        logger.error(f"列出知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=KnowledgeBaseInfo)
async def create_knowledge_base(request: KnowledgeBaseCreate):
    """
    创建或获取知识库
    
    Args:
        request: 创建请求
        
    Returns:
        KnowledgeBaseInfo: 知识库信息
    """
    try:
        kb = get_knowledge_base(
            kb_name=request.name,
            description=request.description,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap
        )
        
        stats = await kb.get_stats()
        
        return KnowledgeBaseInfo(
            name=kb.kb_name,
            description=kb.description,
            document_count=stats['document_count'],
            metadata=kb.metadata
        )
    except Exception as e:
        logger.error(f"创建知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{kb_name}", response_model=KnowledgeBaseInfo)
async def get_knowledge_base_info(kb_name: str):
    """
    获取知识库信息
    
    Args:
        kb_name: 知识库名称
        
    Returns:
        KnowledgeBaseInfo: 知识库信息
    """
    try:
        kb = get_knowledge_base(kb_name)
        stats = await kb.get_stats()
        
        return KnowledgeBaseInfo(
            name=kb.kb_name,
            description=kb.description,
            document_count=stats['document_count'],
            metadata=kb.metadata
        )
    except Exception as e:
        logger.error(f"获取知识库信息失败: {e}")
        raise HTTPException(status_code=404, detail=f"知识库 '{kb_name}' 不存在")


@router.delete("/{kb_name}")
async def delete_knowledge_base(kb_name: str):
    """
    删除知识库（清空所有文档）
    
    Args:
        kb_name: 知识库名称
        
    Returns:
        Dict: 删除结果
    """
    try:
        kb = get_knowledge_base(kb_name)
        await kb.clear()
        
        return {"success": True, "message": f"知识库 '{kb_name}' 已清空"}
    except Exception as e:
        logger.error(f"删除知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{kb_name}/documents", response_model=List[DocumentInfo])
async def list_documents(
    kb_name: str,
    limit: int = 100,
    filter_metadata: Optional[str] = None
):
    """
    列出知识库中的文档
    
    Args:
        kb_name: 知识库名称
        limit: 返回数量限制
        filter_metadata: 元数据过滤（JSON字符串）
        
    Returns:
        List[DocumentInfo]: 文档列表
    """
    try:
        kb = get_knowledge_base(kb_name)
        
        # 解析filter
        filter_dict = None
        if filter_metadata:
            import json
            filter_dict = json.loads(filter_metadata)
        
        docs = await kb.list_documents(
            filter_metadata=filter_dict,
            limit=limit
        )
        
        return [DocumentInfo(**doc) for doc in docs]
    except Exception as e:
        logger.error(f"列出文档失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{kb_name}/search", response_model=List[SearchResult])
async def search_documents(kb_name: str, request: SearchRequest):
    """
    搜索知识库
    
    Args:
        kb_name: 知识库名称
        request: 搜索请求
        
    Returns:
        List[SearchResult]: 搜索结果
    """
    try:
        kb = get_knowledge_base(kb_name)
        
        # 转换模式
        mode_map = {
            "semantic": RetrievalMode.SEMANTIC,
            "keyword": RetrievalMode.KEYWORD,
            "hybrid": RetrievalMode.HYBRID,
            "rerank": RetrievalMode.RERANK
        }
        mode = mode_map.get(request.mode, RetrievalMode.HYBRID)
        
        results = await kb.search(
            query=request.query,
            mode=mode,
            k=request.k,
            filter_metadata=request.filter_metadata
        )
        
        # 转换结果
        search_results = []
        for result in results:
            search_results.append(SearchResult(
                document_id=result.document.id,
                content=result.document.content,
                score=result.score,
                rank=result.rank,
                metadata=result.document.metadata
            ))
        
        return search_results
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{kb_name}/text")
async def add_text(kb_name: str, request: AddTextRequest):
    """
    添加文本到知识库
    
    Args:
        kb_name: 知识库名称
        request: 添加文本请求
        
    Returns:
        Dict: 添加结果
    """
    try:
        kb = get_knowledge_base(kb_name)
        
        doc_ids = await kb.add_text(
            text=request.text,
            metadata=request.metadata
        )
        
        return {
            "success": True,
            "document_ids": doc_ids,
            "count": len(doc_ids)
        }
    except Exception as e:
        logger.error(f"添加文本失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{kb_name}/upload")
async def upload_document(
    kb_name: str,
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None)
):
    """
    上传文档到知识库
    
    Args:
        kb_name: 知识库名称
        file: 上传的文件
        metadata: 元数据（JSON字符串）
        
    Returns:
        Dict: 上传结果
    """
    try:
        kb = get_knowledge_base(kb_name)
        
        # 解析metadata
        metadata_dict = {}
        if metadata:
            import json
            metadata_dict = json.loads(metadata)
        
        # 保存临时文件
        temp_dir = Path(tempfile.mkdtemp())
        temp_file = temp_dir / file.filename
        
        with open(temp_file, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # 添加文档
        doc_ids = await kb.add_document(
            str(temp_file),
            metadata=metadata_dict
        )
        
        # 清理临时文件
        shutil.rmtree(temp_dir)
        
        return {
            "success": True,
            "filename": file.filename,
            "document_ids": doc_ids,
            "count": len(doc_ids)
        }
    except Exception as e:
        logger.error(f"上传文档失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{kb_name}/import")
async def batch_import(kb_name: str, request: BatchImportRequest):
    """
    批量导入目录
    
    Args:
        kb_name: 知识库名称
        request: 批量导入请求
        
    Returns:
        Dict: 导入统计
    """
    try:
        kb = get_knowledge_base(kb_name)
        
        stats = await kb.add_directory(
            directory=request.directory,
            recursive=request.recursive,
            file_patterns=request.file_patterns
        )
        
        return stats
    except Exception as e:
        logger.error(f"批量导入失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{kb_name}/export")
async def export_knowledge_base(kb_name: str, include_embeddings: bool = False):
    """
    导出知识库为JSON
    
    Args:
        kb_name: 知识库名称
        include_embeddings: 是否包含embeddings
        
    Returns:
        Dict: 导出统计
    """
    try:
        kb = get_knowledge_base(kb_name)
        
        # 导出到临时文件
        temp_dir = Path(tempfile.mkdtemp())
        output_file = temp_dir / f"{kb_name}_export.json"
        
        stats = await kb.export_to_json(
            str(output_file),
            include_embeddings=include_embeddings
        )
        
        return stats
    except Exception as e:
        logger.error(f"导出知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{kb_name}/stats")
async def get_knowledge_base_stats(kb_name: str):
    """
    获取知识库统计信息
    
    Args:
        kb_name: 知识库名称
        
    Returns:
        Dict: 统计信息
    """
    try:
        kb = get_knowledge_base(kb_name)
        stats = await kb.get_stats()
        return stats
    except Exception as e:
        logger.error(f"获取统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
