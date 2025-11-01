#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import json
import redis

class RedisChatMessageHistory(ChatMessageHistory):
    def __init__(self, user_id: str, conversation_id: str, redis_client: redis.Redis = None):
        super().__init__()
        # 使用私有属性存储user_id、conversation_id和redis_client
        self._user_id = user_id
        self._conversation_id = conversation_id
        # Use the passed redis_client if provided, otherwise use the imported session_redis_client
        self._redis_client = redis_client if redis_client is not None else session_redis_client
        self._session_key = f"session:{user_id}:{conversation_id}"
        self._load_from_redis()

    def _load_from_redis(self):
        """从Redis加载会话历史"""
        raw = self._redis_client.get(self._session_key)
        if not raw:
            return
        # 兼容 bytes / str
        if isinstance(raw, bytes):
            raw = raw.decode('utf-8')
        try:
            messages = json.loads(raw)
        except json.JSONDecodeError:
            return
        for msg in messages:
            t, c = msg["type"], msg["content"]
            if t == "human":
                self.add_user_message(c)
            elif t == "ai":
                self.add_ai_message(c)
            elif t == "system":
                self.add_message(SystemMessage(content=c))
        
    def _save_to_redis(self):
        """将会话历史保存到Redis"""
        body = json.dumps(
            [
                {"type": "human", "content": m.content}
                if isinstance(m, HumanMessage)
                else {"type": "ai", "content": m.content}
                if isinstance(m, AIMessage)
                else {"type": "system", "content": m.content}
                for m in self.messages
            ],
            ensure_ascii=False,
        )
        self._redis_client.setex(self._session_key, 3600, body)

    def add_user_message(self, message: str) -> None:
        super().add_user_message(message)
        self._save_to_redis()

    def add_ai_message(self, message: str) -> None:
        # Only add non-empty messages
        if message and message.strip():
            super().add_ai_message(message)
            self._save_to_redis()

    def add_message(self, message) -> None:
        super().add_message(message)
        self._save_to_redis()

    def clear(self) -> None:
        super().clear()
        self._redis_client.delete(self._session_key)

# 全局存储，用于缓存RedisChatMessageHistory实例
session_store: dict[tuple[str, str], RedisChatMessageHistory] = {}

def get_redis_session_history(user_id: str, conversation_id: str) -> RedisChatMessageHistory:
    """获取会话历史，使用Redis进行持久化存储"""
    key = (user_id, conversation_id)
    if key not in session_store:
        session_store[key] = RedisChatMessageHistory(user_id, conversation_id)
    return session_store[key]