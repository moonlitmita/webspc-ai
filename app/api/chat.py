#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.services.auth import verify_token
from app.services.redis_tools import get_active_sessions, add_active_session
import uuid
from app.services.history import get_redis_session_history
from langchain.schema import HumanMessage,AIMessage
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
                tool_info = (
                    f"\n\n📋 调用工具：{tool['name']}\n"
                    f"```json\n{json.dumps(tool['args'], indent=2)}\n```\n"
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
                history.add_ai_message(complete_ai)   # 这会触发 _save_to_redis()
        yield "data: [DONE]\n\n"
    except GeneratorExit:
        logger.info("SSE 客户端断开连接, user=%s", user_id)   # 或 logger.debug
        logger.info("SSE 客户端断开连接, user=%s")

# ---------------- 流式接口 ----------------
@router.post("/stream")
def chat_stream(req: ChatRequest, user_id: str = Depends(verify_token)):
    print('userid', user_id)
    # 如果未提供conversation_id或为默认值，则继续使用当前活跃会话
    # 否则创建新的会话
    conversation_id = req.conversation_id
    is_new_conversation = False
    if not conversation_id or conversation_id == "default":
        # 查找用户当前的活跃会话
        user_active_conversations = get_active_sessions(user_id)
        if user_active_conversations:
            # 使用现有的活跃会话
            conversation_id = user_active_conversations[0]
        else:
            # 创建新的会话
            conversation_id = str(uuid.uuid4())
            add_active_session(user_id, conversation_id)
            is_new_conversation = True
    else:
        # 如果提供了具体的conversation_id，添加到活跃会话中
        add_active_session(user_id, conversation_id)
    
    # 把前端历史写进记忆（只写一次，后续由 RunnableWithMessageHistory 自动维护）
    history = get_redis_session_history(user_id, conversation_id)
    history.clear()  # 避免重复追加，可选
    for m in req.messages:
        if m["role"] == "user":
            history.add_user_message(m["content"])
        elif m["role"] == "assistant":
            # Only add non-empty assistant messages
            if m["content"] and m["content"].strip():
                history.add_ai_message(m["content"])

    # 最后一条是用户最新输入
    last_raw = req.messages[-1]["content"] if req.messages else ""
    # 2. 如果有 extraData，拼到内容后面
    if req.extraData is not None:
        last_raw += f"\n\n<!--DATA:{json.dumps(req.extraData, ensure_ascii=False)}-->"
    history_list = list(history.messages)
    history_list.append(HumanMessage(content=last_raw))
    messages = history_list
  
    return StreamingResponse(
        event_stream(messages, user_id, conversation_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )