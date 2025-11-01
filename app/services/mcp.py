#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

import json
from app.services.robust_mcp_client import RobustMultiServerMCPClient
from app.services.redis_tools import mcp_redis_client as r

def load_mcp_config_from_redis() -> dict:
    """
    从 Redis 加载 MCP 配置
    """
    try:
        data = r.get('mcp_config')
        if data:
            return json.loads(data)
        else:
            # 如果 Redis 中没有配置，返回默认配置
            return get_default_mcp_config()
    except Exception as e:
        print(f"从 Redis 加载 MCP 配置时出错: {e}")
        # 出错时返回默认配置
        return get_default_mcp_config()

def save_mcp_config_to_redis(cfg: dict):
    """
    将 MCP 配置保存到 Redis，并发布配置更新通知
    使用分布式锁防止并发更新冲突
    """
    try:
        # 使用 Redis 锁确保同时只有一个更新操作
        lock = r.lock("mcp_config_update_lock", timeout=10, blocking_timeout=5)
        if lock.acquire(blocking=True):
            try:
                r.set('mcp_config', json.dumps(cfg, indent=2))
                # 发布配置更新通知，通知所有实例更新配置
                r.publish('mcp_config_channel', 'update')
            finally:
                lock.release()
        else:
            raise Exception("无法获取配置更新锁，可能有其他更新操作正在进行")
    except Exception as e:
        print(f"保存 MCP 配置到 Redis 时出错: {e}")
        raise e

def get_default_mcp_config() -> dict:
    """
    获取默认的 MCP 配置
    """
    default_config = {
        "mcpServers": {
            "math&time": {
                "command": "python",
                "args": [
                    "mcp_server.py"
                ],
                "transport": "stdio",
                "disabled": False
            },
            "mcp-server-chart": {
                "url": "https://mcp.api-inference.modelscope.net/0b9983c4f5574f/mcp",
                "transport": "streamable_http",
                "disabled": False
            }
        }
    }
    return default_config

def filter_server_configs_for_client(server_configs: dict) -> dict:
    """
    过滤掉不在 MultiServerMCPClient 构造函数中使用的配置项
    这个函数现在不再需要，因为我们已经更新了 RobustMultiServerMCPClient 来处理 'disabled' 参数
    """
    # 直接返回原始配置，让 RobustMultiServerMCPClient 自己处理 'disabled' 参数
    return server_configs

# 启动时自动从 Redis 加载
mcp_config = load_mcp_config_from_redis()
filtered_server_configs = filter_server_configs_for_client(mcp_config["mcpServers"])
mcp_client = RobustMultiServerMCPClient(filtered_server_configs)