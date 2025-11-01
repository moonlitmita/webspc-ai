#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from fastapi import APIRouter, Depends
from app.services.mcp import mcp_client, load_mcp_config_from_redis, save_mcp_config_to_redis
from app.services.auth import verify_token
from app.core.lifespan import reload_agent

router = APIRouter(prefix="/ai/mcp", tags=["mcp"])

@router.get("")
async def get_mcp_config(user_id: str = Depends(verify_token)):
    mcp_config = load_mcp_config_from_redis()
    # 获取失败的服务器列表
    failed_servers = []
    if hasattr(mcp_client, 'get_failed_servers'):
        failed_servers = list(mcp_client.get_failed_servers())
    
    return {
        "code": 200, 
        "data": {
            "mcp_config": mcp_config, 
            "failed_servers": failed_servers,
            "message": "MCP 配置获取成功!"
        }
    }

@router.post("/retry")
async def retry_mcp_connections(user_id: str = Depends(verify_token)):
    # print('user_id_retry', user_id)
    """重试连接失败的MCP服务器"""
    if hasattr(mcp_client, 'retry_failed_servers'):
        try:
            new_tools = await mcp_client.retry_failed_servers()
            # 重新创建代理，包含新连接的工具
            if new_tools:
                # 获取所有工具（包括之前成功的和新连接的）
                all_tools = await mcp_client.get_tools()
                await reload_agent(user_id=user_id)   # 统一重载
                return {
                    "code": 200, 
                    "data": {
                        "new_tools": [t.name for t in new_tools],
                        "all_tools": [t.name for t in all_tools],
                        "message": f"成功重新连接到 {len(new_tools)} 个服务器"
                    }
                }
            else:
                return {
                    "code": 200, 
                    "data": {
                        "new_tools": [],
                        "message": "没有新的服务器连接成功"
                    }
                }
        except Exception as e:
            return {
                "code": 500, 
                "data": {
                    "error": str(e),
                    "message": "重试连接失败"
                }
            }
    else:
        return {
            "code": 400, 
            "data": {
                "message": "当前MCP客户端不支持重试功能"
            }
        }

@router.post("")
async def register_mcp(cfg: dict, user_id: str = Depends(verify_token)):
    global agent
    # 1. 保存配置到 Redis
    save_mcp_config_to_redis(cfg)
    # 2. 重新注册 + 连接
    try:
        await reload_agent(user_id=user_id)
        tools = await mcp_client.get_tools()
        return {"code": 200, "data": {"tools": [t.name for t in tools], "message": "MCP配置成功!"}}
    except Exception as e:
        # 即使MCP工具加载失败，也创建一个仅使用LLM的代理
        await reload_agent(user_id=user_id)
        return {"code": 200, "data": {"tools": [], "message": f"MCP配置已更新，但连接失败: {str(e)}"}}