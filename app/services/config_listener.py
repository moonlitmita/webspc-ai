import redis
import threading
from app.core.logger_config import get_logger
from app.services.mcp import load_mcp_config_from_redis, filter_server_configs_for_client
from app.services.redis_tools import (
    REDIS_MCP_HOST,
    REDIS_MCP_PORT
)

# 创建一个新的 Redis 连接用于监听 MCP 配置变更（需要独立的连接用于 pubsub）
# Uses the MCP-specific Redis server with db=0
r = redis.Redis(
    host=REDIS_MCP_HOST,
    port=REDIS_MCP_PORT,
    db=0,  # MCP Redis instance uses db=0
    decode_responses=True
)

def start_config_listener():
    """
    启动配置变更监听器
    """
    # 获取专用日志记录器
    logger = get_logger(__name__)
    
    def listen():
        while True:
            try:
                pubsub = r.pubsub()
                pubsub.subscribe('mcp_config_channel')
                
                for message in pubsub.listen():
                    try:
                        if message['type'] == 'message':
                            # 配置已更新，重新加载
                            # print("检测到MCP配置更新，正在重新加载...")

                            # 重新加载配置
                            from app.services.mcp import RobustMultiServerMCPClient
                            new_config = load_mcp_config_from_redis()
                            filtered_server_configs = filter_server_configs_for_client(new_config["mcpServers"])

                            # 重新创建 MCP 客户端
                            new_mcp_client = RobustMultiServerMCPClient(filtered_server_configs)

                            # 更新全局 mcp_client 实例
                            import app.services.mcp as mcp_module
                            mcp_module.mcp_client = new_mcp_client
                            mcp_module.mcp_config = new_config
                            mcp_module.filtered_server_configs = filtered_server_configs
                    except Exception as e:
                        # 记录配置更新过程中的错误，但不中断监听循环
                        logger.error(f"MCP配置更新失败: {str(e)}")
                        continue
            except redis.ConnectionError as e:
                logger.error(f"Redis连接断开，正在尝试重连: {str(e)}")
                # 重连前等待一段时间
                import time
                time.sleep(5)
            except Exception as e:
                logger.error(f"MCP配置监听器发生未知错误: {str(e)}")
                # 出现未知错误时等待一段时间再重试
                import time
                time.sleep(10)

    # 在一个独立线程中运行监听器
    listener_thread = threading.Thread(target=listen, daemon=True)
    listener_thread.start()
    # print("MCP配置变更监听器已启动")