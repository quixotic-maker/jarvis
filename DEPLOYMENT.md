# Jarvis部署指南

## 📋 目录
- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [Docker部署](#docker部署)
- [手动部署](#手动部署)
- [环境配置](#环境配置)
- [生产部署建议](#生产部署建议)
- [故障排除](#故障排除)

---

## 系统要求

### 硬件要求
- **CPU**: 2核心及以上
- **内存**: 4GB及以上（推荐8GB）
- **存储**: 10GB可用空间

### 软件要求
- Docker 20.10+ & Docker Compose 1.29+
- 或 Python 3.11+ & Node.js 18+
- PostgreSQL 15+（如不使用Docker）
- Redis 7+（可选，用于缓存）

---

## 快速开始

### 使用Docker Compose（推荐）

**1. 克隆仓库**
```bash
git clone https://github.com/your-org/jarvis.git
cd jarvis
```

**2. 配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，填入必要的API密钥
nano .env
```

**3. 启动所有服务**
```bash
docker-compose up -d
```

**4. 验证部署**
```bash
# 检查所有容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 访问应用
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

**5. 停止服务**
```bash
docker-compose down
```

---

## Docker部署

### 单独构建镜像

**Backend**
```bash
cd backend
docker build -t jarvis-backend:latest .
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  --name jarvis-backend \
  jarvis-backend:latest
```

**Frontend**
```bash
cd frontend
docker build -t jarvis-frontend:latest .
docker run -d \
  -p 3000:80 \
  --name jarvis-frontend \
  jarvis-frontend:latest
```

### 使用预构建镜像
```bash
# 从Docker Hub拉取
docker pull jarvis/backend:latest
docker pull jarvis/frontend:latest

# 运行
docker-compose -f docker-compose.prod.yml up -d
```

---

## 手动部署

### Backend部署

**1. 安装Python依赖**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. 配置数据库**
```bash
# 创建PostgreSQL数据库
createdb jarvis_db

# 运行数据库迁移
alembic upgrade head
```

**3. 启动服务**
```bash
# 开发模式
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式（使用gunicorn）
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Frontend部署

**1. 安装Node依赖**
```bash
cd frontend
npm install
```

**2. 构建生产版本**
```bash
npm run build
```

**3. 使用Nginx托管**
```bash
# 复制构建产物到nginx目录
sudo cp -r build/* /var/www/jarvis/

# 配置nginx（参考nginx.conf）
sudo systemctl restart nginx
```

---

## 环境配置

### 必需配置项

```bash
# 数据库连接
DATABASE_URL=postgresql://user:password@localhost:5432/jarvis_db

# LLM API密钥（至少配置一个）
OPENAI_API_KEY=sk-xxx
# 或
ANTHROPIC_API_KEY=sk-ant-xxx
```

### 可选配置项

```bash
# Redis缓存
REDIS_URL=redis://localhost:6379

# CORS设置
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Embedding模型
EMBEDDING_PROVIDER=local  # 或 openai
EMBEDDING_MODEL=all-MiniLM-L6-v2

# 日志级别
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

---

## 生产部署建议

### 1. 使用HTTPS
```bash
# 使用Let's Encrypt获取证书
sudo certbot --nginx -d yourdomain.com

# 或配置Nginx反向代理
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. 配置进程管理器（Systemd）

**Backend Service**
```ini
# /etc/systemd/system/jarvis-backend.service
[Unit]
Description=Jarvis Backend API
After=network.target postgresql.service

[Service]
Type=notify
User=jarvis
WorkingDirectory=/opt/jarvis/backend
Environment="PATH=/opt/jarvis/backend/venv/bin"
ExecStart=/opt/jarvis/backend/venv/bin/gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl enable jarvis-backend
sudo systemctl start jarvis-backend
sudo systemctl status jarvis-backend
```

### 3. 数据库优化
```sql
-- 创建索引以提高查询性能
CREATE INDEX idx_documents_metadata ON documents USING GIN (metadata);
CREATE INDEX idx_schedules_user ON schedules (user_id, start_time);
CREATE INDEX idx_tasks_status ON tasks (status, priority);
```

### 4. 配置日志轮转
```bash
# /etc/logrotate.d/jarvis
/var/log/jarvis/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 jarvis jarvis
    sharedscripts
    postrotate
        systemctl reload jarvis-backend
    endscript
}
```

### 5. 监控和告警
```bash
# 使用Prometheus + Grafana
pip install prometheus-client

# 在应用中暴露metrics端点
from prometheus_client import make_asgi_app

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

---

## 故障排除

### 常见问题

**1. 数据库连接失败**
```bash
# 检查PostgreSQL是否运行
sudo systemctl status postgresql

# 验证连接字符串
psql "postgresql://user:pass@host:5432/dbname"

# 检查防火墙
sudo ufw allow 5432/tcp
```

**2. API返回500错误**
```bash
# 查看详细错误日志
docker-compose logs backend

# 或手动运行查看错误
cd backend
python main.py
```

**3. 前端无法连接后端**
```bash
# 检查CORS配置
# 在.env中添加：
CORS_ORIGINS=http://localhost:3000

# 验证API可访问性
curl http://localhost:8000/api/health
```

**4. Embedding模型下载失败**
```bash
# 手动下载模型
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# 或使用离线模型
export TRANSFORMERS_OFFLINE=1
```

**5. 内存不足**
```bash
# 减少worker数量
gunicorn --workers 2 ...

# 限制Docker容器内存
docker-compose up -d --scale backend=1 --memory="2g"
```

### 性能问题

**数据库查询慢**
```sql
-- 分析慢查询
SELECT * FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;

-- 添加缓存
CACHE_TTL=300  # 5分钟缓存
```

**API响应慢**
```bash
# 启用缓存
ENABLE_CACHE=true
CACHE_BACKEND=redis

# 增加worker数量
WORKERS=8
```

---

## 更新和维护

### 更新应用
```bash
# 拉取最新代码
git pull origin main

# 重建并重启容器
docker-compose down
docker-compose build
docker-compose up -d

# 或手动更新
cd backend && pip install -r requirements.txt
cd ../frontend && npm install && npm run build
sudo systemctl restart jarvis-backend
```

### 备份数据
```bash
# 备份数据库
docker exec jarvis-postgres pg_dump -U jarvis jarvis_db > backup_$(date +%Y%m%d).sql

# 备份向量数据
docker cp jarvis-backend:/app/data/vector_stores ./backup/vector_stores/

# 恢复数据
docker exec -i jarvis-postgres psql -U jarvis jarvis_db < backup.sql
```

---

## 安全建议

1. **定期更新依赖**
   ```bash
   pip list --outdated
   npm outdated
   ```

2. **使用强密码**
   - 数据库密码至少16字符
   - 定期轮换API密钥

3. **限制网络访问**
   ```bash
   # 仅允许必要端口
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw deny 5432/tcp  # 数据库仅内网访问
   ```

4. **配置防火墙和WAF**
   - 使用Cloudflare或AWS WAF
   - 限制API请求频率

5. **启用审计日志**
   ```python
   # 记录所有API调用
   LOG_ALL_REQUESTS=true
   ```

---

## 支持

- 📧 Email: support@jarvis.ai
- 💬 Discord: https://discord.gg/jarvis
- 📖 文档: https://docs.jarvis.ai
- 🐛 问题反馈: https://github.com/your-org/jarvis/issues
