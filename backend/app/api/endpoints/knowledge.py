"""
知识大脑API端点

提供：
- 知识节点管理
- 知识连接管理
- 知识图谱查询
- 知识搜索
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.db.database import get_db
from app.api.schemas import BaseResponse, PaginatedResponse

router = APIRouter()


# ==================== Pydantic Models ====================

class KnowledgeNodeCreate(BaseModel):
    """创建知识节点"""
    label: str = Field(..., min_length=1, max_length=200, description="节点名称")
    node_type: str = Field(..., pattern="^(concept|skill|project|resource|person)$", description="节点类型")
    description: Optional[str] = Field(None, description="节点描述")
    tags: Optional[List[str]] = Field(default=None, description="标签")
    metadata: Optional[dict] = Field(default=None, description="元数据")


class KnowledgeNodeUpdate(BaseModel):
    """更新知识节点"""
    label: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class KnowledgeNodeResponse(BaseModel):
    """知识节点响应"""
    id: int
    user_id: str
    label: str
    node_type: str
    description: Optional[str]
    tags: List[str]
    metadata: Optional[dict]
    connections_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConnectionCreate(BaseModel):
    """创建知识连接"""
    from_node_id: int = Field(..., description="起始节点ID")
    to_node_id: int = Field(..., description="目标节点ID")
    relation_type: str = Field(..., description="关系类型")
    weight: float = Field(default=1.0, ge=0.0, le=1.0, description="连接权重")
    description: Optional[str] = Field(None, description="连接描述")


class ConnectionResponse(BaseModel):
    """知识连接响应"""
    id: int
    from_node_id: int
    to_node_id: int
    relation_type: str
    weight: float
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgeGraphResponse(BaseModel):
    """知识图谱响应"""
    nodes: List[KnowledgeNodeResponse]
    edges: List[ConnectionResponse]
    stats: dict


# ==================== 知识节点端点 ====================

@router.get("/nodes", summary="获取知识节点列表")
async def get_knowledge_nodes(
    user_id: str = Query(default="default_user"),
    node_type: Optional[str] = Query(default=None, pattern="^(concept|skill|project|resource|person)$"),
    search: Optional[str] = Query(default=None, description="搜索关键词"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db)
) -> PaginatedResponse[KnowledgeNodeResponse]:
    """
    获取用户的知识节点列表
    
    支持按类型筛选和关键词搜索
    """
    # TODO: 实现真实的数据库查询
    # 模拟数据
    demo_nodes = [
        {
            "id": 1,
            "user_id": user_id,
            "label": "React",
            "node_type": "skill",
            "description": "前端框架，用于构建用户界面",
            "tags": ["前端", "框架"],
            "metadata": {"level": "advanced"},
            "connections_count": 12,
            "created_at": datetime(2026, 1, 1, 10, 0, 0),
            "updated_at": datetime(2026, 1, 15, 10, 0, 0),
        },
        {
            "id": 2,
            "user_id": user_id,
            "label": "TypeScript",
            "node_type": "skill",
            "description": "JavaScript的超集，提供静态类型检查",
            "tags": ["编程语言", "类型系统"],
            "metadata": {"level": "intermediate"},
            "connections_count": 15,
            "created_at": datetime(2026, 1, 1, 10, 0, 0),
            "updated_at": datetime(2026, 1, 10, 10, 0, 0),
        },
        {
            "id": 3,
            "user_id": user_id,
            "label": "Jarvis项目",
            "node_type": "project",
            "description": "智能助手项目，第二大脑系统",
            "tags": ["AI", "助手", "知识管理"],
            "metadata": {"status": "active"},
            "connections_count": 25,
            "created_at": datetime(2026, 1, 1, 10, 0, 0),
            "updated_at": datetime.now(),
        },
        {
            "id": 4,
            "user_id": user_id,
            "label": "AI知识",
            "node_type": "concept",
            "description": "人工智能相关概念和理论",
            "tags": ["AI", "机器学习"],
            "metadata": {},
            "connections_count": 18,
            "created_at": datetime(2026, 1, 1, 10, 0, 0),
            "updated_at": datetime(2026, 1, 12, 10, 0, 0),
        },
        {
            "id": 5,
            "user_id": user_id,
            "label": "Python编程",
            "node_type": "skill",
            "description": "Python语言及其生态系统",
            "tags": ["编程语言", "Python"],
            "metadata": {"level": "advanced"},
            "connections_count": 20,
            "created_at": datetime(2026, 1, 1, 10, 0, 0),
            "updated_at": datetime(2026, 1, 10, 10, 0, 0),
        },
        {
            "id": 6,
            "user_id": user_id,
            "label": "机器学习",
            "node_type": "concept",
            "description": "机器学习算法和应用",
            "tags": ["AI", "算法"],
            "metadata": {},
            "connections_count": 22,
            "created_at": datetime(2026, 1, 1, 10, 0, 0),
            "updated_at": datetime(2026, 1, 10, 10, 0, 0),
        },
    ]
    
    # 按类型筛选
    if node_type:
        demo_nodes = [n for n in demo_nodes if n["node_type"] == node_type]
    
    # 搜索
    if search:
        search_lower = search.lower()
        demo_nodes = [
            n for n in demo_nodes
            if search_lower in n["label"].lower() or 
               (n["description"] and search_lower in n["description"].lower())
        ]
    
    total = len(demo_nodes)
    items = demo_nodes[skip:skip + limit]
    
    return PaginatedResponse(
        success=True,
        data=items,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.post("/nodes", summary="创建知识节点")
async def create_knowledge_node(
    node: KnowledgeNodeCreate,
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db)
) -> BaseResponse[KnowledgeNodeResponse]:
    """创建新的知识节点"""
    # TODO: 实现真实的数据库创建
    new_node = {
        "id": 7,
        "user_id": user_id,
        "label": node.label,
        "node_type": node.node_type,
        "description": node.description,
        "tags": node.tags or [],
        "metadata": node.metadata,
        "connections_count": 0,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    
    return BaseResponse(
        success=True,
        message="知识节点创建成功",
        data=new_node
    )


@router.get("/nodes/{node_id}", summary="获取知识节点详情")
async def get_knowledge_node(
    node_id: int,
    db: Session = Depends(get_db)
) -> BaseResponse[KnowledgeNodeResponse]:
    """获取指定知识节点的详情"""
    # TODO: 实现真实的数据库查询
    if node_id == 1:
        node = {
            "id": 1,
            "user_id": "default_user",
            "label": "React",
            "node_type": "skill",
            "description": "前端框架，用于构建用户界面",
            "tags": ["前端", "框架"],
            "metadata": {"level": "advanced"},
            "connections_count": 12,
            "created_at": datetime(2026, 1, 1, 10, 0, 0),
            "updated_at": datetime(2026, 1, 15, 10, 0, 0),
        }
        return BaseResponse(success=True, data=node)
    
    raise HTTPException(status_code=404, detail="知识节点不存在")


@router.put("/nodes/{node_id}", summary="更新知识节点")
async def update_knowledge_node(
    node_id: int,
    node: KnowledgeNodeUpdate,
    db: Session = Depends(get_db)
) -> BaseResponse[KnowledgeNodeResponse]:
    """更新知识节点信息"""
    # TODO: 实现真实的数据库更新
    updated_node = {
        "id": node_id,
        "user_id": "default_user",
        "label": node.label or "React",
        "node_type": "skill",
        "description": node.description or "前端框架，用于构建用户界面",
        "tags": node.tags or ["前端", "框架"],
        "metadata": node.metadata or {"level": "advanced"},
        "connections_count": 12,
        "created_at": datetime(2026, 1, 1, 10, 0, 0),
        "updated_at": datetime.now(),
    }
    
    return BaseResponse(
        success=True,
        message="知识节点更新成功",
        data=updated_node
    )


@router.delete("/nodes/{node_id}", summary="删除知识节点")
async def delete_knowledge_node(
    node_id: int,
    db: Session = Depends(get_db)
) -> BaseResponse[None]:
    """删除知识节点"""
    # TODO: 实现真实的数据库删除
    return BaseResponse(
        success=True,
        message="知识节点删除成功"
    )


# ==================== 知识连接端点 ====================

@router.get("/connections", summary="获取知识连接列表")
async def get_connections(
    node_id: Optional[int] = Query(default=None, description="节点ID，获取该节点的所有连接"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db)
) -> PaginatedResponse[ConnectionResponse]:
    """获取知识连接列表"""
    # TODO: 实现真实的数据库查询
    demo_connections = [
        {
            "id": 1,
            "from_node_id": 1,
            "to_node_id": 2,
            "relation_type": "依赖",
            "weight": 0.8,
            "description": "React项目通常使用TypeScript",
            "created_at": datetime(2026, 1, 1, 10, 0, 0),
        },
        {
            "id": 2,
            "from_node_id": 1,
            "to_node_id": 3,
            "relation_type": "应用",
            "weight": 1.0,
            "description": "Jarvis项目使用React框架",
            "created_at": datetime(2026, 1, 1, 10, 0, 0),
        },
        {
            "id": 3,
            "from_node_id": 4,
            "to_node_id": 6,
            "relation_type": "包含",
            "weight": 0.9,
            "description": "AI知识包含机器学习",
            "created_at": datetime(2026, 1, 1, 10, 0, 0),
        },
    ]
    
    # 按节点筛选
    if node_id is not None:
        demo_connections = [
            c for c in demo_connections
            if c["from_node_id"] == node_id or c["to_node_id"] == node_id
        ]
    
    total = len(demo_connections)
    items = demo_connections[skip:skip + limit]
    
    return PaginatedResponse(
        success=True,
        data=items,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.post("/connections", summary="创建知识连接")
async def create_connection(
    connection: ConnectionCreate,
    db: Session = Depends(get_db)
) -> BaseResponse[ConnectionResponse]:
    """创建新的知识连接"""
    # TODO: 实现真实的数据库创建
    new_connection = {
        "id": 4,
        "from_node_id": connection.from_node_id,
        "to_node_id": connection.to_node_id,
        "relation_type": connection.relation_type,
        "weight": connection.weight,
        "description": connection.description,
        "created_at": datetime.now(),
    }
    
    return BaseResponse(
        success=True,
        message="知识连接创建成功",
        data=new_connection
    )


@router.delete("/connections/{connection_id}", summary="删除知识连接")
async def delete_connection(
    connection_id: int,
    db: Session = Depends(get_db)
) -> BaseResponse[None]:
    """删除知识连接"""
    # TODO: 实现真实的数据库删除
    return BaseResponse(
        success=True,
        message="知识连接删除成功"
    )


# ==================== 知识图谱端点 ====================

@router.get("/graph", summary="获取知识图谱")
async def get_knowledge_graph(
    user_id: str = Query(default="default_user"),
    center_node_id: Optional[int] = Query(default=None, description="中心节点ID"),
    depth: int = Query(default=2, ge=1, le=5, description="探索深度"),
    db: Session = Depends(get_db)
) -> BaseResponse[KnowledgeGraphResponse]:
    """
    获取知识图谱数据
    
    - 如果指定center_node_id，则返回该节点周围指定深度的子图
    - 否则返回完整图谱
    """
    # TODO: 实现真实的图谱查询算法
    # 获取节点和连接（重用上面的模拟数据）
    nodes_response = await get_knowledge_nodes(user_id=user_id, db=db)
    connections_response = await get_connections(db=db)
    
    stats = {
        "total_nodes": nodes_response.total,
        "total_connections": connections_response.total,
        "node_types": {
            "concept": len([n for n in nodes_response.data if n["node_type"] == "concept"]),
            "skill": len([n for n in nodes_response.data if n["node_type"] == "skill"]),
            "project": len([n for n in nodes_response.data if n["node_type"] == "project"]),
            "resource": len([n for n in nodes_response.data if n["node_type"] == "resource"]),
            "person": len([n for n in nodes_response.data if n["node_type"] == "person"]),
        },
        "avg_connections": round(
            sum(n["connections_count"] for n in nodes_response.data) / len(nodes_response.data)
            if nodes_response.data else 0,
            2
        ),
    }
    
    graph_data = {
        "nodes": nodes_response.data,
        "edges": connections_response.data,
        "stats": stats,
    }
    
    return BaseResponse(
        success=True,
        data=graph_data
    )


@router.get("/search", summary="搜索知识")
async def search_knowledge(
    query: str = Query(..., min_length=1, description="搜索关键词"),
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db)
) -> BaseResponse[List[KnowledgeNodeResponse]]:
    """
    智能搜索知识节点
    
    支持模糊匹配和语义搜索
    """
    # TODO: 实现向量搜索和语义匹配
    # 暂时使用简单的关键词匹配
    all_nodes_response = await get_knowledge_nodes(
        user_id=user_id,
        search=query,
        limit=20,
        db=db
    )
    
    return BaseResponse(
        success=True,
        data=all_nodes_response.data,
        message=f"找到 {len(all_nodes_response.data)} 个相关节点"
    )
