# WebSPC AI Project

## Project Overview

WebSPC AI is an AI chat system built on FastAPI and LangChain, Langgraph that integrates MCP (Model Context Protocol) Client. It can freely switch between different large models as AI engines, providing intelligent chat functionality for Six Sigma and SPC (Statistical Process Control) consulting, as well as supporting automatic tool calling.

Frontend code address: https://gitee.com/valleyfo/webspc-frontend

Backend code address: https://gitee.com/valleyfo/webspc-backend

## Core Features

1. **AI Chat System**: Streaming chat interface based on the selected large model
2. **MCP Integration**: Integration with MCP Client to connect with MCP Server, providing additional tools and resources
3. **Session Management**: Redis persistent storage for chat history, supporting multi-turn conversation continuity
4. **Authentication**: JWT Token authentication mechanism
5. **Active Session Tracking**: Tracking of user active sessions to ensure session continuity

## Technical Architecture

- **Web Framework**: FastAPI
- **AI Framework**: LangChain, LangGraph, OpenAI compatible interface
- **Large Language Models**: Freely switch between different large models
- **Data Storage**: Redis (chat history, active session management, LLM configuration, MCP configuration)
- **Authentication**: JWT
- **Logging**: Unified logging configuration

## Main File Structure

- `app/main.py`: Main application file, contains FastAPI application and routes
- `app/services/mcp.py`: MCP service implementation
- `app/services/robust_mcp_client.py`: Enhanced MCP client with fault tolerance when some servers fail
- `app/services/utils.py`: Utility functions, including JWT handling
- `app/services/redis_tools.py`: Redis connection and session management tools
- `app/core/logger_config.py`: Unified logging configuration
- `app/core/config.py`: Configuration management
- `app/api/chat.py`: Chat interface
- `app/api/session.py`: Session management interface
- `app/api/mcp.py`: MCP related interfaces

## Key Function Implementation

### Session Management

The system implements an improved session management mechanism:

1. **Session Continuation**: When users engage in multiple rounds of conversation in the same session, the system automatically continues the current session
2. **New Session Creation**: Frontend can create a new session by not passing conversation_id or passing the "default" value
3. **Session End**: Provides a dedicated API endpoint `/chat/end_session` to explicitly end a session and ensure data is saved to Redis
4. **Active Session Tracking**: The system uses Redis sets to track each user's active sessions

### MCP (Model Context Protocol) Integration

- `robust_mcp_client.py` implements an enhanced MCP client that can continue working when some server connections fail
- The system supports multi-server configuration and can retry connections to failed servers

### Redis Session Storage

- The `RedisChatMessageHistory` class inherits from `ChatMessageHistory` and implements Redis persistence
- Session data is automatically saved to Redis each time a message is added
- Sets an 8-hour expiration time

## API Endpoints

- `POST /chat/stream` - Streaming chat interface
- `POST /chat/end_session` - End session interface
- `GET /mcp` - Get MCP configuration
- `POST /mcp/retry` - Retry MCP server connection
- `POST /mcp` - Update MCP configuration
- `GET /session/history` - Get historical session records
- `GET /session/detail` - Get session details

## Environment Configuration

The following environment variables need to be configured:

- `ENV`: Runtime environment (dev/prod)
- `FRONTEND_URL`: Frontend URL address (frontend domain in production)
- `REDIS_SESSION_HOST`: Redis-session instance server host (optional, default localhost)
- `REDIS_MODEL_HOST`: Redis-model instance server host (optional, default localhost)
- `REDIS_MCP_HOST`: Redis-mcp instance server host (optional, default localhost)
- `REDIS_SESSION_PORT`: Redis-session instance server port (optional, default 6379)
- `REDIS_MODEL_PORT`: Redis-mdoel instance server port (optional, default 6380)
- `REDIS_MCP_PORT`: Redis-mcp instance server port (optional, default 6381)
- `LOCALMODEL_API_KEY`: Local model API key (not required, only for placeholder)
- `SILICONFLOW_API_KEY`: SiliconFlow API key (configure as needed)
- `MODELSCOPE_API_KEY`: MODELSCOPE API key (configure as needed)
- `DASHCOPE_API_KEY`: DASHCOPE API key (configure as needed)
- `ZHIPIAI_API_KEY`: ZHIPIAI API key (configure as needed)
- `MOONSHOT_API_KEY`: MOONSHOT API key (configure as needed)
- `DOUBAO_API_KEY`: DOUBAO API key (configure as needed)
- `DEEPSEEK_API_KEY`: DEEPSEEK API key (configure as needed)
- `JWT_SECRET`: Use environment variable to configure JWT_SECRET

## Installation and Running

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables (set SILICONFLOW_API_KEY, etc.)

3. Run the server:
   Development environment:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
   ```
   Production environment:
   ```
   # Deploy using k8s or K3s
   ```

## Development Conventions

- Logs use the configuration in logger_config.py
- Use Redis to store chat history, LLM configurations, and MCP configurations to ensure data persistence
- JWT tokens are used for user authentication
- All API endpoints require valid JWT token verification
- Code follows Python coding standards

## Special Notes

- The system is specifically optimized for Six Sigma and SPC fields
- The system prompt includes the eight rules of SPC control chart interpretation
- If the MCP server returns data with link addresses, the AI will return those addresses
- The project uses LangGraph's ReAct agent mode, supporting tool calling

## Project Demo Address: https://webspc.top

Username: admin

Login password: Contact the author for access

## Technical Support:

Author: Yu Wang

Email: wynmamtf@163.com

QQ: 271989251

Weixin: valleyfo

Note: Technical support includes but is not limited to
    Custom business development,
    Project deployment,
    Program usage explanation, code explanation, SPC theory training, etc.