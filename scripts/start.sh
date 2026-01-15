#!/bin/bash

echo "🚀 Jarvis 项目启动脚本"
echo ""

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 启动后端
echo "📦 启动后端服务..."
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
if [ ! -f "venv/installed" ]; then
    echo "安装Python依赖..."
    pip install -r requirements.txt
    touch venv/installed
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告：未找到.env文件，复制.env.example为.env"
    cp .env.example .env
    echo "❗ 请编辑backend/.env文件，填入你的API密钥"
fi

# 后台启动后端
echo "启动FastAPI服务器..."
nohup python main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端PID: $BACKEND_PID"

cd ..

# 等待后端启动
echo "等待后端启动..."
sleep 3

# 启动前端
echo "📦 启动前端服务..."
cd frontend

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装Node依赖..."
    npm install
fi

# 启动前端
echo "启动Vite开发服务器..."
npm run dev &
FRONTEND_PID=$!
echo "前端PID: $FRONTEND_PID"

cd ..

# 创建日志目录
mkdir -p logs

# 保存PID
echo $BACKEND_PID > logs/backend.pid
echo $FRONTEND_PID > logs/frontend.pid

echo ""
echo "✅ Jarvis 启动成功！"
echo ""
echo "📍 访问地址："
echo "   前端: http://localhost:3000"
echo "   后端API: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "💡 停止服务："
echo "   运行 ./scripts/stop.sh"
echo ""
