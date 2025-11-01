# WebSPC AI 项目

## 项目概述

WebSPC AI 是一个基于 FastAPI 和 LangChain, Langgraph 的 AI 对话系统，集成了 MCP（Model Context Protocol）Client，可以自由切换不同的大模型作为 AI 引擎，不仅提供智能对话功能用于六西格玛和 SPC（统计过程控制）领域的咨询，而且支持工具的自动调用。

前端代码地址：https://gitee.com/valleyfo/webspc-frontend

后端代码地址：https://gitee.com/valleyfo/webspc-backend

## 核心功能

1. **AI 对话系统**: 基于选定大模型的流式对话接口
2. **MCP 集成**: 集成 MCP Client，对接MCP Server，提供额外的工具和资源
3. **会话管理**: Redis 持久化存储对话历史，支持多轮对话延续
4. **身份认证**: JWT Token 认证机制
5. **活跃会话跟踪**: 跟踪用户活跃会话，确保会话正确延续

## 技术架构

- **Web 框架**: FastAPI
- **AI 框架**: LangChain、LangGraph、OpenAI 兼容接口
- **大语言模型**: 自由切换不同的大模型
- **数据存储**: Redis (会话历史、活跃会话管理、LLM配置、MCP配置)
- **认证**: JWT
- **日志**: 统一日志配置

## 主要文件结构

- `app/main.py`: 主应用文件，包含 FastAPI 应用和路由
- `app/services/mcp.py`: MCP 服务实现
- `app/services/robust_mcp_client.py`: 增强版 MCP 客户端，支持部分服务器失败时的容错
- `app/services/utils.py`: 工具函数，包括 JWT 处理
- `app/services/redis_tools.py`: Redis 连接和会话管理工具
- `app/core/logger_config.py`: 统一日志配置
- `app/core/config.py`: 配置管理
- `app/api/chat.py`: 聊天接口
- `app/api/session.py`: 会话管理接口
- `app/api/mcp.py`: MCP 相关接口

## 关键功能实现

### 会话管理

系统实现了改进的会话管理机制：

1. **会话延续**: 当用户在同一个会话中进行多轮对话时，系统会自动延续当前会话
2. **新建会话**: 前端可通过不传递 conversation_id 或传递 "default" 值来创建新会话
3. **会话结束**: 提供专门的 API 端点 `/chat/end_session` 来显式结束会话并确保数据保存到 Redis
4. **活跃会话跟踪**: 系统使用 Redis 集合跟踪每个用户的活跃会话

### MCP (Model Context Protocol) 集成

- `robust_mcp_client.py` 实现了增强版 MCP 客户端，能够在部分服务器连接失败时继续工作
- 系统支持多服务器配置，并可重试连接失败的服务器

### Redis 会话存储

- `RedisChatMessageHistory` 类继承自 `ChatMessageHistory`，实现了 Redis 持久化
- 会话数据在每次添加消息时自动保存到 Redis
- 设置了 8 小时的过期时间

## API 端点

- `POST /chat/stream` - 流式对话接口
- `POST /chat/end_session` - 结束会话接口
- `GET /mcp` - 获取 MCP 配置
- `POST /mcp/retry` - 重试 MCP 服务器连接
- `POST /mcp` - 更新 MCP 配置
- `GET /session/history` - 获取历史会话记录
- `GET /session/detail` - 获取会话详情

## 环境配置

需要配置以下环境变量：

- `ENV`: 运行环境（dev/prod）
- `FRONTEND_URL`: 前端URL地址（生产环境为前端域名）
- `REDIS_HOST`: Redis 服务器主机（可选，默认 localhost）
- `REDIS_PORT`: Redis 服务器端口（可选，默认 6379）
- `REDIS_SESSION_DB`: Redis 会话数据库索引（可选，默认 0，用于会话历史）
- `REDIS_MODEL_DB`: Redis 模型数据库索引（可选，默认 1，用于模型配置）
- `REDIS_MCP_DB`: Redis MCP数据库索引（可选，默认 2，用于MCP配置）
- `LOCALMODEL_API_KEY`: 本地模型 API 密钥（不需要，仅用于占位）
- `SILICONFLOW_API_KEY`: SiliconFlow API 密钥（根据需要进行配置）
- `MODELSCOPE_API_KEY`: MODELSCOPE API 密钥（根据需要进行配置）
- `DASHCOPE_API_KEY`: DASHCOPE API 密钥（根据需要进行配置）
- `ZHIPIAI_API_KEY`: ZHIPIAI API 密钥（根据需要进行配置）
- `MOONSHOT_API_KEY`: MOONSHOT API 密钥（根据需要进行配置）
- `DOUBAO_API_KEY`: DOUBAO API 密钥（根据需要进行配置）
- `DEEPSEEK_API_KEY`: DEEPSEEK API 密钥（根据需要进行配置）
- `JWT_SECRET`: 使用环境变量配置JWT_SECRET

## 安装和运行

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 配置环境变量（设置 SILICONFLOW_API_KEY 等）

3. 运行服务器：
   开发环境：
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
   ```
   生产环境：
   ```
   # 使用k8s或K3s部署
   ```
## 开发约定

- 日志统一使用 logger_config.py 中的配置
- 使用 Redis 存储会话历史，LLM配置，MCP配置,确保数据持久化
- JWT 令牌用于用户身份验证
- 所有 API 端点都需要有效的 JWT 令牌验证
- 代码遵循 Python 编码规范

## 特殊说明

- 系统专门针对六西格玛和 SPC 领域进行了优化
- 系统提示词中包含了 SPC 控制图的八条判异准则
- 如果 MCP 服务器返回的数据里有链接地址，AI 会返回该地址
- 项目使用了 LangGraph 的 ReAct 代理模式，支持工具调用

## 项目演示地址：https://webspc.top

用户名：admin

登录密码：联系作者获取

## 技术支持：

作者：王宇

Email: wynmamtf@163.com

QQ: 271989251

Weixin: valleyfo

备注：技术支持包括但不限于
    定制业务开发,
    项目部署,
    程序使用讲解，代码讲解，SPC理论培训等。