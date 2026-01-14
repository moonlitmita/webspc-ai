#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.services.auth import verify_token
from app.core.logger_config import get_logger
from app.tasks.alarm_analysis import analyze_alarm_and_notify_task

router = APIRouter(prefix="/ai/alarm", tags=["alarm"])
logger = get_logger(__name__)

class Outlier(BaseModel):
    x: float
    y: float
    message: str
    add_date: str  

class AlarmData(BaseModel):
    title: str
    content: str
    outliers: List[Outlier]
    project: str
    process: str
    product: str
    spcType: List[str]
    additional_info: Optional[dict] = None

@router.post("/analyze")
async def analyze_alarm(alarm_data: AlarmData, user_id: str = Depends(verify_token)):
    """
    接收告警信息，启动异步分析任务
    """
    try:
        # 启动异步任务进行告警分析和飞书通知
        task = analyze_alarm_and_notify_task.delay(
            alarm_data.model_dump(),
            user_id
        )
        
        logger.info(f"Alarm analysis task started with ID: {task.id}")
        
        return {"code": 200, "data": {"message": "告警分析任务已启动"}}
    except Exception as e:
        logger.error(f"Failed to start alarm analysis task: {e}")
        raise HTTPException(status_code=500, detail=f"启动告警分析任务失败: {str(e)}")