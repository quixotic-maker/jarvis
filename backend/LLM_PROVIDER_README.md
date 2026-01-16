# Jarvis LLM Provider系统

## 🎯 概述

Jarvis的LLM Provider系统提供了一个统一的抽象层，支持多个LLM提供商，包括OpenAI、Anthropic和Ollama（本地模型）。

## 🏗️ 架构

```
app/core/
├── llm_provider.py      # 抽象基类
├── llm_config.py        # 配置管理
├── llm_factory.py       # Provider工厂
└── providers/
    ├── openai_provider.py      # OpenAI实现
    ├── anthropic_provider.py   # Anthropic实现
    └── ollama_provider.py      # Ollama实现
```

## 🚀 快速开始

### 1. 配置环境变量

复制 `.env.example` 到 `.env` 并填入你的API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# OpenAI
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Anthropic
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Ollama (本地)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# 默认Provider
DEFAULT_PROVIDER=OPENAI
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- `openai>=1.10.0` - OpenAI官方SDK
- `anthropic>=0.8.1` - Anthropic官方SDK
- `tiktoken>=0.5.2` - Token计数库
- `httpx>=0.26.0` - HTTP客户端（用于Ollama）

### 3. 测试Provider

运行测试脚本：

```bash
cd backend
python test_llm_providers.py
```

## 💻 使用方法

### Python代码中使用

```python
from app.core.llm_factory import get_provider
from app.core.llm_config import LLMProviderType
from app.core.llm_provider import ChatRequest, Message

# 1. 使用默认provider
provider = get_provider()

# 2. 指定provider类型
provider = get_provider(LLMProviderType.OPENAI)

# 3. 创建聊天请求
request = ChatRequest(
    messages=[
        Message(role="user", content="Hello, how are you?")
    ],
    temperature=0.7,
    max_tokens=100
)

# 4. 非流式对话
response = await provider.chat(request)
print(response.content)
print(response.usage)  # token使用情况

# 5. 流式对话
async for chunk in provider.chat_stream(request):
    print(chunk, end="", flush=True)

# 6. Token计数
token_count = await provider.count_tokens("Hello world", "gpt-3.5-turbo")
print(f"Tokens: {token_count}")

# 7. 获取可用模型
models = provider.get_available_models()
print(f"Available models: {models}")
```

### REST API使用

#### 1. 聊天补全

```bash
curl -X POST http://localhost:8000/api/v2/llm/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "你好，请介绍一下人工智能"}
    ],
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 500,
    "stream": false
  }'
```

响应：
```json
{
  "status": "success",
  "message": "聊天补全成功",
  "data": {
    "content": "人工智能（AI）是...",
    "model": "gpt-3.5-turbo",
    "usage": {
      "prompt_tokens": 12,
      "completion_tokens": 156,
      "total_tokens": 168
    },
    "finish_reason": "stop"
  }
}
```

#### 2. 流式对话

```bash
curl -X POST http://localhost:8000/api/v2/llm/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "写一首诗"}
    ],
    "provider": "openai",
    "stream": true
  }'
```

响应（SSE流）：
```
data: {"content": "春"}
data: {"content": "天"}
data: {"content": "来"}
...
data: [DONE]
```

#### 3. 获取可用模型

```bash
curl http://localhost:8000/api/v2/llm/models?provider=openai
```

响应：
```json
{
  "status": "success",
  "message": "获取模型列表成功",
  "data": {
    "provider": "openai",
    "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
  }
}
```

#### 4. Token计数

```bash
curl -X POST http://localhost:8000/api/v2/llm/count-tokens \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, world!",
    "model": "gpt-3.5-turbo",
    "provider": "openai"
  }'
```

## 🔧 Provider详解

### DeepSeek Provider ⭐ 推荐

**支持的模型**:
- deepseek-chat (通用对话模型)
- deepseek-coder (代码专用模型)

**特性**:
- ✅ 兼容OpenAI API格式
- ✅ **极高性价比**（约为GPT-3.5的1/5成本）
- ✅ 32K上下文窗口
- ✅ 中文能力强
- ✅ 精确的token计数（使用tiktoken）
- ✅ 流式对话支持

**定价**（每1000 tokens）:
- deepseek-chat: $0.00014 (输入) / $0.00028 (输出)
- deepseek-coder: $0.00014 (输入) / $0.00028 (输出)
- **约¥1/百万tokens** - 性价比之王！

**配置方法**:
```env
# 在.env中配置DeepSeek
DEEPSEEK_API_KEY=sk-your-deepseek-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# 使用OpenAI provider调用DeepSeek
DEFAULT_PROVIDER=OPENAI
```

系统会自动检测：如果配置了`DEEPSEEK_API_KEY`，OpenAI provider会优先使用DeepSeek配置。

### OpenAI Provider

**支持的模型**:
- GPT-4
- GPT-4 Turbo
- GPT-3.5 Turbo

**特性**:
- ✅ 精确的token计数（使用tiktoken）
- ✅ 准确的成本计算
- ✅ 流式对话支持
- ✅ 完整的API支持

**定价**（每1000 tokens）:
- GPT-4: $0.03 (输入) / $0.06 (输出)
- GPT-4 Turbo: $0.01 (输入) / $0.03 (输出)
- GPT-3.5 Turbo: $0.0005 (输入) / $0.0015 (输出)

### Anthropic Provider

**支持的模型**:
- Claude-3 Opus
- Claude-3 Sonnet
- Claude-3 Haiku

**特性**:
- ✅ System消息自动分离
- ✅ 流式对话支持
- ✅ 成本跟踪
- ⚠️ Token计数为近似值（每3字符约1 token）

**定价**（每1000 tokens）:
- Claude-3 Opus: $0.015 (输入) / $0.075 (输出)
- Claude-3 Sonnet: $0.003 (输入) / $0.015 (输出)
- Claude-3 Haiku: $0.00025 (输入) / $0.00125 (输出)

### Ollama Provider

**支持的模型**:
- Llama 2
- Mistral
- Mixtral
- Code Llama
- Phi
- Qwen

**特性**:
- ✅ 本地运行，免费
- ✅ 流式对话支持
- ✅ 完全私密
- ⚠️ Token计数为近似值
- ⚠️ 需要本地运行Ollama服务

**使用前提**:
```bash
# 安装Ollama
curl https://ollama.ai/install.sh | sh

# 启动Ollama服务
ollama serve

# 下载模型
ollama pull llama2
```

## 📊 成本跟踪

系统自动跟踪所有LLM调用的成本：

```python
# 成本自动计算并记录
response = await provider.chat(request)

# 访问成本信息
usage_stats = UsageStats(
    provider=LLMProviderType.OPENAI,
    model="gpt-3.5-turbo",
    prompt_tokens=100,
    completion_tokens=50,
    total_tokens=150,
    cost=0.000225  # 自动计算
)
```

## 🔐 安全性

1. **API密钥管理**: 所有密钥存储在环境变量中
2. **请求验证**: 自动验证所有请求参数
3. **错误处理**: 完善的异常处理机制
4. **速率限制**: 内置速率限制支持（可配置）

## 🎯 最佳实践

### 1. 选择合适的Provider

- **OpenAI**: 最强大，适合复杂任务
- **Anthropic**: 长上下文，适合文档分析
- **Ollama**: 免费本地，适合开发测试

### 2. 优化成本

```python
# 使用更便宜的模型处理简单任务
provider = get_provider(LLMProviderType.OPENAI)
config_override = {"model": "gpt-3.5-turbo"}
cheap_provider = get_provider(
    LLMProviderType.OPENAI,
    config_override=config_override
)
```

### 3. 流式响应

对于用户交互，使用流式响应提供更好的体验：

```python
async for chunk in provider.chat_stream(request):
    # 实时显示给用户
    yield chunk
```

### 4. 错误处理

```python
try:
    response = await provider.chat(request)
except ValueError as e:
    # 参数验证错误
    print(f"Invalid request: {e}")
except RuntimeError as e:
    # API调用失败
    print(f"API error: {e}")
```

## 🧪 测试

运行完整测试套件：

```bash
python test_llm_providers.py
```

测试覆盖：
- ✅ 非流式对话
- ✅ 流式对话
- ✅ Token计数
- ✅ 模型列表
- ✅ 成本计算

## 🚀 未来计划

- [ ] 添加更多Provider（Google PaLM、Cohere等）
- [ ] 实现自动重试和fallback机制
- [ ] 添加缓存层减少重复调用
- [ ] 数据库持久化使用统计
- [ ] Web UI管理界面
- [ ] 成本预算和告警

## 📝 API文档

访问 http://localhost:8000/docs 查看完整的Swagger API文档。

## 🤝 贡献

欢迎贡献新的Provider实现！只需继承 `LLMProvider` 基类并实现所有抽象方法。

## 📄 许可

MIT License
