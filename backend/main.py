"""
Jarvis - 多Agent智能助手系统
主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.routes import api_router
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    init_db()
    print("🚀 Jarvis 系统启动中...")
    yield
    # 关闭时的清理工作
    print("👋 Jarvis 系统关闭")


app = FastAPI(
    title=settings.APP_NAME,
    description="""
## Jarvis - 多Agent智能助手系统

一个功能完整的多Agent智能助手系统，集成了RAG（检索增强生成）、
LLM服务、知识库管理等核心功能。

### 主要功能模块

#### 🤖 Agent系统
- 21个专业化智能Agent
- 智能任务分发和协作
- 自然语言理解

#### 📚 知识库管理
- 向量数据库存储
- 多种检索模式（语义/关键词/混合/重排）
- 文档处理和分块
- 批量导入导出

#### 🔍 RAG系统
- 文档向量化
- 智能检索
- 上下文生成
- Agent集成

#### 💬 LLM服务
- 多提供商支持（OpenAI/Azure/Anthropic/本地）
- 流式响应
- 提示工程

### API使用指南

所有API端点都遵循RESTful设计规范，返回JSON格式数据。

### 认证
当前版本暂未启用认证，生产环境请添加适当的安全措施。
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Jarvis Development Team",
        "email": "support@jarvis.ai",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """健康检查端点"""
    return {
        "message": "Welcome to Jarvis - Your Multi-Agent Assistant",
        "status": "running",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
