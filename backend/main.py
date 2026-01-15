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
    description="一个多Agent智能助手系统，提供信息检索、日程规划、即时通知等功能",
    version="1.0.0",
    lifespan=lifespan
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
