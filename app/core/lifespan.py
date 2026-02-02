#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from contextlib import asynccontextmanager
from fastapi import FastAPI
from langgraph.prebuilt import create_react_agent
from app.core.logger_config import get_logger
from app.services.mcp import mcp_client
from dotenv import load_dotenv

# Import the model service
from app.services.model_config import model_service, save_model_configs_to_redis, MODEL_CONFIGS, check_model_configs_in_redis

# Import the config listener
from app.services.config_listener import start_config_listener

# Import tool wrapper
# from app.core.tool_wrapper import ValidatingToolWrapper

load_dotenv()
logger = get_logger(__name__)

# 内部持有真实对象
_agent = None

# ③ 创建 LangGraph ReAct 代理
# Removed the hardcoded LLM initialization
def get_current_llm(user_id: str):
    return model_service.get_llm(user_id)

# ---------------- FastAPI 生命周期：自动托管 MCP ----------------
from contextlib import asynccontextmanager
systemPrompt = (
    "你是一名六西格玛黑带,精通六西格玛,尤其是SPC控制图"
    "控制图的八条判异准则如下"
    "准则1: 点超控制限"
    "准则2: 连续9点落在中心线同一侧"
    "准则3: 连续6点递增或递减"
    "准则4: 连续14点中相邻点升降交错"
    "准则5: 连续3点中有2点落在中心线同一侧的B区之外"
    "准则6: 连续5点中有4点落在中心线同一侧的C区之外"
    "准则7: 连续15点落在C区之内"
    "准则8: 连续8点落在中心线两侧,但无1点在C区之内"
    "请根据会话历史回答用户的问题"
    "如果MCP server 返回的数据里有链接地址，一定要返回该地址。"
    "当调用工具后，请根据工具返回的结果简洁地告知用户操作结果，"
    "如果操作失败，请简要说明失败原因，不要输出工具返回的详细错误信息。"
)

# 热重载供重试MCP tools连接和保存MCP配置时使用
async def reload_agent(tools=None, user_id: str = "default_user"):
    """运行期热重载 agent（可被路由多次调用）"""
    global _agent
    if tools is None:   # 重新拉取最新工具
        # raw_tools = await mcp_client.get_tools()
        tools = await mcp_client.get_tools()
        # 使用工具包装器包装所有工具，确保参数验证(暂时不启用，如后续遇到mcp工具调用时出现参数问题再启用)。
        # tools = [ValidatingToolWrapper(tool) for tool in raw_tools]
    # Use the dynamic LLM
    llm = get_current_llm(user_id)
    _agent = create_react_agent(llm, tools, prompt=systemPrompt)
    logger.info(f"Agent reloaded with {len(tools)} tools")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动：连接 MCP Server + 创建代理 + 启动配置监听器
    global _agent
    try:
        # 初始化模型配置：确保 Redis 中有默认模型配置
        if not check_model_configs_in_redis():
            # 如果 Redis 中没有模型配置，则保存默认配置
            save_model_configs_to_redis(MODEL_CONFIGS)
            logger.info("默认模型配置已保存到 Redis")
        else:
            logger.info("使用 Redis 中的模型配置")
        
        tools = await mcp_client.get_tools()   # ← 内部已连接
        # print(f"[Lifespan] MCP 工具已加载：{[t.name for t in tools]}")
        await reload_agent(tools, user_id="system_default")   # 使用系统默认用户初始化代理
        logger.info(f"MCP tools loaded: {[t.name for t in tools]}")
        
        # 启动配置监听器
        start_config_listener()
    except Exception as e:
        logger.error(f"MCP load failed: {e}")
        # print(f"[Lifespan] MCP 工具加载失败：{e}")
        # 即使MCP工具加载失败，也创建一个仅使用LLM的代理
        await reload_agent([], user_id="system_default")   # 纯LLM兜底，使用系统默认用户
    yield  # 应用运行期间卡住这里
    # 关闭：无需手动断开（MultiServerMCPClient 内部已处理）

# 工厂函数 —— 供路由函数调用
def get_agent():
    if _agent is None:
        # 如果 lifespan 还没跑完，抛 500 让 FastAPI 自动返回 500 Internal Server Error
        raise RuntimeError("Agent 尚未初始化完成")
    return _agent

