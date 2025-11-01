#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

import os, redis
from typing import Final
from app.core.config import settings

REDIS_HOST: Final = os.getenv("REDIS_HOST", settings.redis_host)
REDIS_PORT: Final = int(os.getenv("REDIS_PORT", settings.redis_port))
REDIS_SESSION_DB:   Final = int(os.getenv("REDIS_SESSION_DB", settings.redis_session_db))
REDIS_MODEL_DB: Final = int(os.getenv("REDIS_MODEL_DB", settings.redis_model_db))
# 添加 MCP 配置专用的数据库索引
REDIS_MCP_DB: Final = int(os.getenv("REDIS_MCP_DB", settings.redis_mcp_db))  # 默认使用数据库 2

# 1. 为会话历史建立连接池
_session_redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_SESSION_DB,
    decode_responses=True,      # 统一强制 str
    max_connections=20,
)

# 2. 为模型配置建立连接池
_model_redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_MODEL_DB,
    decode_responses=True,      # 统一强制 str
    max_connections=20,
)

# 3. 为 MCP 配置建立连接池
_mcp_redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_MCP_DB,
    decode_responses=True,      # 统一强制 str
    max_connections=10,         # MCP 配置可能不需要太多连接
)

# 3. 全局客户端
session_redis_client: redis.Redis = redis.Redis(connection_pool=_session_redis_pool)
model_redis_client: redis.Redis = redis.Redis(connection_pool=_model_redis_pool)
mcp_redis_client: redis.Redis = redis.Redis(connection_pool=_mcp_redis_pool)


# 针对活跃会话操作的三个原子函数
# redis_tools.py  (已有 redis_client)
ACTIVE_SET_KEY_TPL = "active_set:{user_id}"
TTL_SECONDS = 28800

def get_active_sessions(user_id: str) -> list[str]:
    """返回用户所有活跃 conversation_id 列表（无则空列表）"""
    key = ACTIVE_SET_KEY_TPL.format(user_id=user_id)
    return list(session_redis_client.smembers(key))   # Redis Set -> Python list

def add_active_session(user_id: str, conversation_id: str) -> None:
    """把 conversation_id 加入用户活跃集合，并刷新 TTL"""
    key = ACTIVE_SET_KEY_TPL.format(user_id=user_id)
    session_redis_client.delete(key)
    session_redis_client.sadd(key, conversation_id)          # 去重加入
    session_redis_client.expire(key, TTL_SECONDS)            # 每次更新过期时间

def remove_active_session(user_id: str, conversation_id: str) -> None:
    """从用户活跃集合里移除指定 conversation_id"""
    key = ACTIVE_SET_KEY_TPL.format(user_id=user_id)
    session_redis_client.srem(key, conversation_id)