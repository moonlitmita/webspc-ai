#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.services.auth import verify_token
from app.services.redis_tools import get_active_sessions, add_active_session
import uuid
from app.services.history import get_redis_session_history
from langchain_core.messages import HumanMessage, AIMessage
from app.core.lifespan import get_agent
from app.models.schemas import ChatRequest
from app.core.logger_config import get_logger
import json, time

# 获取当前模块的日志记录器
logger = get_logger(__name__)

router = APIRouter(prefix="/ai/chat", tags=["chat"])

async def event_stream(
    messages: list,
    user_id: str,
    conversation_id: str
):
    try:
        ai_parts = []
        agent = get_agent()
        async for chunk in agent.astream({"messages": messages}):
            if "agent" not in chunk:
                continue
            msgs = chunk["agent"]["messages"]
            if not msgs:
                continue
            last_msg = msgs[-1]
            if not isinstance(last_msg, AIMessage):
                continue

            # 1. 工具调用信息
            if last_msg.tool_calls:
                tool = last_msg.tool_calls[0]

                # 验证工具参数格式
                validated_args = {}
                for key, value in tool['args'].items():
                    if isinstance(value, str):
                        validated_args[key] = value
                    else:
                        validated_args[key] = str(value)

                tool_info = (
                    f"\n\n📋 调用工具：{tool['name']}\n"
                    f"```json\n{json.dumps(validated_args, indent=2, ensure_ascii=False)}\n```\n"
                )
                for ch in tool_info:
                    delta = ch.lstrip("\n\r") # 去掉左侧换行
                    yield f"data: {json.dumps({'delta': ch})}\n\n"
                    time.sleep(0.02)

            # 2. 正常回答内容（含工具结果）
            content = last_msg.content or ""
            if not content.strip():
                continue
            ai_parts.append(content)
            for ch in content:
                delta = ch.lstrip("\n\r")   # 去掉左侧换行
                yield f"data: {json.dumps({'delta': delta})}\n\n"
                time.sleep(0.02)
        # ---- 流结束：把完整 AI 回复写回 Redis ----
        if ai_parts:                       # 有内容才存
            complete_ai = "".join(ai_parts)
            if complete_ai.strip():
                history = get_redis_session_history(user_id, conversation_id)
                # 确保AI消息内容是字符串类型
                clean_complete_ai = str(complete_ai) if complete_ai is not None else ""
                history.add_ai_message(clean_complete_ai)   # 这会触发 _save_to_redis()
        yield "data: [DONE]\n\n"
    except GeneratorExit:
        logger.info("SSE 客户端断开连接, user=%s", user_id)   # 或 logger.debug
        logger.info("SSE 客户端断开连接, user=%s")
    except Exception as e:
        logger.error(f"事件流处理错误: {e}")
        yield f"data: {json.dumps({'error': '处理请求时发生错误'})}\n\n"
        yield "data: [DONE]\n\n"


import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """计算文本的 token 数"""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")  # 默认编码
    return len(encoding.encode(text))

# ---------------- 流式接口 ----------------
@router.post("/stream")
def chat_stream(req: ChatRequest, user_id: str = Depends(verify_token)):
    conversation_id = req.conversation_id
    if not conversation_id or conversation_id == "default":
        # 创建新的会话
        conversation_id = str(uuid.uuid4())
        add_active_session(user_id, conversation_id)
    else:
        # 如果提供了具体的conversation_id，添加到活跃会话中
        add_active_session(user_id, conversation_id)

    print(f"extraData: {req.extraData}")

    # 把前端历史写进记忆（只写一次，后续由 RunnableWithMessageHistory 自动维护）
    history = get_redis_session_history(user_id, conversation_id)
    # 不再清空历史记录，而是保留现有历史
    # 遍历消息列表(除了最后一条消息)
    for m in req.messages[:-1]:
        if m["role"] == "user":
            history.add_user_message(m["content"])
        elif m["role"] == "assistant":
            # Only add non-empty assistant messages
            if m["content"] and m["content"].strip():
                history.add_ai_message(m["content"])

    # 构建最终消息列表
    history_list = list(history.messages)

    # 处理最后一条消息
    if req.messages:
        content = req.messages[-1].get("content", "")
        if req.extraData:
            content += f"\n\n<!--DATA:{json.dumps(req.extraData, ensure_ascii=False)}-->"
        history_list.append(HumanMessage(content=content))
    
    # 计算实际会传给 LLM 的 token 数
    total_tokens = sum(count_tokens(str(m.content)) for m in history_list)
    
    # token超限提醒
    if total_tokens > 30000:
        raise HTTPException(
            status_code=413,
            detail=f"上下文过长: {total_tokens} tokens，请开启新对话或缩短输入"
        )
    
    return StreamingResponse(
        event_stream(history_list, user_id, conversation_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )