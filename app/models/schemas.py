#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from pydantic import BaseModel
from typing import Any


class ChatRequest(BaseModel):
    messages: list  # 前端传来的历史 [{role:..., content: ...}]
    # 可选：不传就默认 "default"
    user_id: str = "default"
    conversation_id: str = "default"
    extraData: Any | None = None   # ← 新增，任意 JSON

class ModelRequest(BaseModel):
    provider: str 
    model_id: str