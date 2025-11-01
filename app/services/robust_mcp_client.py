#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from langchain_mcp_adapters.client import MultiServerMCPClient
from typing import List, Dict, Any
import asyncio
from app.core.logger_config import get_logger

# 获取当前模块的日志记录器
logger = get_logger(__name__)

class RobustMultiServerMCPClient:
    """
    一个增强版的MultiServerMCPClient，能够在部分服务器连接失败时继续工作
    """
    
    def __init__(self, server_configs: Dict[str, Dict[str, Any]]):
        self.server_configs = server_configs
        self.clients = {}
        self.failed_servers = set()
        
        # 为每个服务器配置创建一个独立的MultiServerMCPClient
        # 同时处理 'disabled' 参数，过滤掉它再传给 MultiServerMCPClient
        for server_name, config in server_configs.items():
            # 检查服务器是否被禁用
            server_disabled = config.get('disabled', False)
            # 过滤掉 'disabled' 参数，因为它不是 MultiServerMCPClient 的有效参数
            filtered_config = {k: v for k, v in config.items() if k != 'disabled'}
            
            if not server_disabled:
                # 只为未禁用的服务器创建客户端
                try:
                    self.clients[server_name] = MultiServerMCPClient({server_name: filtered_config})
                    logger.info(f"已为服务器 {server_name} 创建客户端")
                except Exception as e:
                    logger.error(f"无法为服务器 {server_name} 创建客户端: {e}")
                    self.failed_servers.add(server_name)
            else:
                logger.info(f"服务器 {server_name} 已禁用，跳过客户端创建")
    
    async def get_tools(self) -> List[Any]:
        """
        获取所有可用服务器的工具，即使部分服务器连接失败也不会导致整个操作失败
        """
        all_tools = []
        
        # 并行尝试连接所有服务器
        tasks = {
            server_name: self._get_server_tools(server_name, client)
            for server_name, client in self.clients.items()
        }
        
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        # 处理结果
        for server_name, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"连接MCP服务器 {server_name} 失败: {result}")
                self.failed_servers.add(server_name)
            else:
                all_tools.extend(result)
                # 如果服务器重新连接成功，从失败列表中移除
                self.failed_servers.discard(server_name)
        
        # 添加被禁用的服务器到失败列表中，这样前端可以知道它们的状态
        for server_name, config in self.server_configs.items():
            if config.get('disabled', False):
                self.failed_servers.add(server_name)
        
        logger.info(f"成功从 {len(all_tools)} 个工具中加载了 {len(all_tools)} 个工具")
        logger.info(f"以下服务器连接失败或被禁用: {list(self.failed_servers)}")
        
        return all_tools
    
    async def _get_server_tools(self, server_name: str, client: MultiServerMCPClient) -> List[Any]:
        """
        获取单个服务器的工具
        """
        try:
            tools = await client.get_tools()
            logger.info(f"成功连接到MCP服务器 {server_name}，获取到 {len(tools)} 个工具")
            return tools
        except Exception as e:
            logger.error(f"连接MCP服务器 {server_name} 失败: {e}")
            raise e
    
    def get_failed_servers(self) -> set:
        """
        获取连接失败的服务器列表
        """
        return self.failed_servers.copy()
    
    async def retry_failed_servers(self) -> List[Any]:
        """
        重试连接之前失败的服务器
        """
        # 过滤掉被禁用的服务器，只重试实际连接失败的服务器
        actual_failed_servers = {server_name for server_name in self.failed_servers 
                                if not self.server_configs.get(server_name, {}).get('disabled', False)}
        
        if not actual_failed_servers:
            return []
        
        logger.info(f"尝试重新连接 {len(actual_failed_servers)} 个失败的服务器: {list(actual_failed_servers)}")
        
        # 只重试实际失败的服务器
        retry_tasks = {
            server_name: self._get_server_tools(server_name, self.clients[server_name])
            for server_name in actual_failed_servers
        }
        
        results = await asyncio.gather(*retry_tasks.values(), return_exceptions=True)
        
        # 收集成功重连的服务器工具
        newly_connected_tools = []
        for server_name, result in zip(retry_tasks.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"重新连接MCP服务器 {server_name} 失败: {result}")
            else:
                newly_connected_tools.extend(result)
                logger.info(f"成功重新连接到MCP服务器 {server_name}")
                self.failed_servers.discard(server_name)
        
        return newly_connected_tools
