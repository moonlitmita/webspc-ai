#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from fastapi import APIRouter, Depends, Query
from app.services.auth import verify_token
from app.services.redis_tools import get_active_sessions, remove_active_session, add_active_session
from app.services.history import get_redis_session_history
from app.services.redis_tools import session_redis_client
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.core.logger_config import get_logger

router = APIRouter(prefix="/ai/session", tags=["session"])
logger = get_logger(__name__)

@router.get("/end_session")
def end_session(
    conversation_id: str = Query("", description="要结束的会话ID,空串则直接找唯一活跃会话"),
    user_id: str = Depends(verify_token)
):

    """
    结束当前用户的活跃会话。
    如果前端没传 conversation_id，后端自动找当前唯一活跃会话。
    """
    try:
        actual_conversation_id = conversation_id
        if conversation_id == "default" or not conversation_id:
            user_active = get_active_sessions(user_id)
            if user_active:
                # 如果有多个活跃会话且未指定具体会话ID，返回错误提示
                if len(user_active) > 1:
                    return {
                        "code": 400,
                        "data": {
                            "message": f"用户有多个活跃会话，请指定要结束的具体会话ID: {user_active}",
                            "conversation_id": None
                        }
                    }
                else:
                    # 只有一个活跃会话，结束它
                    actual_conversation_id = user_active[0]
                    remove_active_session(user_id, actual_conversation_id)
            else:
                # 🔥 没有活跃会话 → 自动创建默认会话
                actual_conversation_id = "default"

        else:
            # ---- 清理活跃集合 ----
            remove_active_session(user_id, actual_conversation_id)

        # ---- 触发落盘（get_session_history 会自动 save） ----
        history = get_redis_session_history(user_id, actual_conversation_id)

        return {
            "code": 200,
            "data": {
                "message": "会话已结束并保存到Redis",
                "conversation_id": actual_conversation_id
            }
        }
    except Exception as e:
        logger.error(f"结束会话失败: {e}")
        return {
            "code": 500,
            "data": {
                "message": f"结束会话失败: {str(e)}"
            }
        }
    
@router.get("/history")
def get_session_history(user_id: str = Depends(verify_token)):
    """获取用户的历史会话记录（排除活跃会话）"""
    try:
        # 获取Redis中所有匹配用户ID的会话键
        pattern = f"session:{user_id}:*"
        session_keys = session_redis_client.keys(pattern)
        
        # 获取活跃会话ID列表（只保留conversation_id部分）
        user_active_conversations = get_active_sessions(user_id)
        
        history_sessions = []
        
        # 遍历所有会话键
        for key in session_keys:
            # 提取conversation_id（最后一个冒号后的内容）
            conversation_id = key.split(":")[-1]
            
            # 跳过活跃会话
            if conversation_id in user_active_conversations:
                continue
            
            # 获取会话历史
            history = get_redis_session_history(user_id, conversation_id)
            
            # 如果会话中有消息，则添加到历史记录中
            if history.messages:
                # 获取第一条消息作为会话标题
                first_message = history.messages[0].content if history.messages else "空会话" 
                # 获取最后一条消息的时间作为会话时间
                # 注意：由于RedisChatMessageHistory没有直接存储时间戳，
                # 我们只能近似使用当前时间或者从消息内容中推断
                history_sessions.append({
                    "conversation_id": conversation_id,
                    "title": first_message[:17] + "..." if len(first_message) > 17 else first_message,
                    "message_count": len(history.messages)
                })
        return {
            "code": 200,
            "data": {
                "history_sessions": history_sessions,
                "message": "历史会话获取成功"
            }
        }
    except Exception as e:
        logger.error(f"获取历史会话失败: {e}")
        return {
            "code": 500,
            "data": {
                "message": f"获取历史会话失败: {str(e)}"
            }
        }

def msg_to_dict(msg) -> dict:
    if isinstance(msg, HumanMessage):
        return {"role": "user", "content": msg.content}
    if isinstance(msg, AIMessage):
        return {"role": "assistant", "content": msg.content}
    if isinstance(msg, SystemMessage):
        return {"role": "system", "content": msg.content}
    # 兜底
    return {"role": "unknown", "content": str(msg.content)}

@router.get("/detail")
def get_session_detail(
    conversation_id: str = Query("", description="会话ID, 空串则按以下规则处理"),
    user_id: str = Depends(verify_token)
):
    try:
        # 确定实际要使用的会话ID
        actual_conversation_id = conversation_id

        # 如果前端传入的是"default"或空字符串，则查找用户的活跃会话
        if conversation_id == "default" or not conversation_id:
            user_active = get_active_sessions(user_id)
            if user_active:
                # 如果有多个活跃会话且未指定具体会话ID，返回错误提示
                if len(user_active) > 1:
                    return {
                        "code": 400,
                        "data": {
                            "session_detail": [],
                            "conversation_id": None,
                            "message": f"用户有多个活跃会话，请指定具体的会话ID: {user_active}"
                        }
                    }
                else:
                    actual_conversation_id = user_active[0]
                    # print(f"使用活跃会话ID: {actual_conversation_id}")
            else:
                return {
                    "code": 200,
                    "data": {
                        "session_detail": [],
                        "conversation_id": None,
                        "message": "当前没有活跃会话"
                    }
                }

        history = get_redis_session_history(user_id, actual_conversation_id)
        return {
            "code": 200,
            "data": {
                "session_detail": [msg_to_dict(m) for m in history.messages],
                "conversation_id": actual_conversation_id,
                "message": "会话详情获取成功"
            }
        }
    except Exception as e:
        logger.error(f"获取会话详情失败: {e}")
        return {
            "code": 500,
            "data": {
                "message": f"获取会话详情失败: {str(e)}"
            }
        }
    
@router.delete("/history")
def delete_session_history(
    conversation_id: str = Query(..., description="要删除的会话ID"),
    user_id: str = Depends(verify_token)
):
    """
    删除指定的历史会话
    """
    try:
        # 构造会话键
        session_key = f"session:{user_id}:{conversation_id}"
        
        # 检查会话是否存在
        if not session_redis_client.exists(session_key):
            return {
                "code": 404,
                "data": {
                    "message": "会话不存在"
                }
            }
        
        # 删除会话数据
        session_redis_client.delete(session_key)
        
        # 如果该会话在活跃会话中，也要从活跃会话中移除
        remove_active_session(user_id, conversation_id)
        
        return {
            "code": 200,
            "data": {
                "message": "会话删除成功",
                "conversation_id": conversation_id
            }
        }
    except Exception as e:
        logger.error(f"删除会话失败: {e}")
        return {
            "code": 500,
            "data": {
                "message": f"删除会话失败: {str(e)}"
            }
        }
    
@router.delete("/history/batch")
def delete_multiple_session_history(
    conversation_ids: list[str] = Query(..., description="要删除的会话ID列表"),
    user_id: str = Depends(verify_token)
):
    """
    批量删除历史会话
    """
    try:
        deleted_count = 0
        failed_deletions = []
        
        for conversation_id in conversation_ids:
            session_key = f"session:{user_id}:{conversation_id}"
            
            # 删除会话数据
            if session_redis_client.exists(session_key):
                result = session_redis_client.delete(session_key)
                if result > 0:
                    # 如果该会话在活跃会话中，也要从活跃会话中移除
                    remove_active_session(user_id, conversation_id)
                    deleted_count += 1
                else:
                    failed_deletions.append(conversation_id)
            else:
                failed_deletions.append(conversation_id)
        
        return {
            "code": 200,
            "data": {
                "message": f"批量删除完成，成功删除 {deleted_count} 个会话",
                "deleted_count": deleted_count,
                "failed_count": len(failed_deletions),
                "failed_ids": failed_deletions
            }
        }
    except Exception as e:
        logger.error(f"批量删除会话失败: {e}")
        return {
            "code": 500,
            "data": {
                "message": f"批量删除会话失败: {str(e)}"
            }
        }