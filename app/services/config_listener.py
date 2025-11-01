import redis
import threading
from app.core.config import settings
from app.services.mcp import load_mcp_config_from_redis, filter_server_configs_for_client

# 创建 Redis 客户端，用于监听配置变更
r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=2, decode_responses=True)

def start_config_listener():
    """
    启动配置变更监听器
    """
    def listen():
        pubsub = r.pubsub()
        pubsub.subscribe('mcp_config_channel')

        for message in pubsub.listen():
            if message['type'] == 'message':
                # 配置已更新，重新加载
                print("检测到MCP配置更新，正在重新加载...")
                
                # 重新加载配置
                from app.services.mcp import mcp_client, RobustMultiServerMCPClient
                new_config = load_mcp_config_from_redis()
                filtered_server_configs = filter_server_configs_for_client(new_config["mcpServers"])
                
                # 重新创建 MCP 客户端
                new_mcp_client = RobustMultiServerMCPClient(filtered_server_configs)
                
                # 更新全局 mcp_client 实例
                import app.services.mcp as mcp_module
                mcp_module.mcp_client = new_mcp_client
                mcp_module.mcp_config = new_config
                mcp_module.filtered_server_configs = filtered_server_configs

    # 在一个独立线程中运行监听器
    listener_thread = threading.Thread(target=listen, daemon=True)
    listener_thread.start()
    # print("MCP配置变更监听器已启动")