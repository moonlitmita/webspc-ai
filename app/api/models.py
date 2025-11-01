from fastapi import APIRouter, Depends, HTTPException
from app.services.auth import verify_token
from app.services.model_config import model_service, load_model_configs_from_redis, save_model_configs_to_redis
from app.core.logger_config import get_logger
from app.services.model_config import MODEL_CONFIGS
from app.models.schemas import ModelRequest

logger = get_logger(__name__)

router = APIRouter(prefix="/ai/models", tags=["models"])

@router.get("/providers")
def list_providers(user_id: str = Depends(verify_token)):
    """返回全部 provider 列表"""
    return {
        "code": 200,
        "data": [
            {"key": k, "label": v["label"]}
            for k, v in MODEL_CONFIGS.items()
        ]
    }

@router.get("/available")
def list_models_by_provider(provider: str, user_id: str = Depends(verify_token)):
    """返回某 provider 下的模型列表"""
    if provider not in MODEL_CONFIGS:
        raise HTTPException(404, "provider not found")
    models = MODEL_CONFIGS[provider]["models"].values()
    return {"code": 200, "data": list(models)}

@router.post("/switch")
def switch_model(req: ModelRequest, user_id: str = Depends(verify_token)):
    """切换模型：需要同时提供 provider + model_id"""
    cfg = MODEL_CONFIGS.get(req.provider, {}).get("models", {}).get(req.model_id)
    print(f"switchCFG: {cfg}")
    print(f"user_id is : {user_id}")
    if not cfg:
        raise HTTPException(400, "Invalid provider or model")
    # 真正切换逻辑
    success = model_service.set_model(user_id, req.provider, req.model_id)   # 下面给出改造
    if not success:
        raise HTTPException(status_code=400, detail=f"Invalid API provider: {req.provider} and model id {req.model_id}")

    return {"code": 200, "data": {"success": True, "message": f"Switched to {req.model_id}"}}

# 获取当前模型
@router.get("/current")
def get_current_model(user_id: str = Depends(verify_token)):
    """获取当前使用的模型"""
    config = model_service.get_current_model_config(user_id)   # +user_id
    return {"code": 200, "data": {"current_model": config, "message": "模型获取成功！"}}

# 获取全部模型配置
@router.get("/config")
def get_model_configs(user_id: str = Depends(verify_token)):
    """获取全部模型配置"""
    configs = load_model_configs_from_redis()
    return {
        "code": 200,
        "data": {
            "model_configs": configs,
            "message": "模型配置获取成功！"
        }
    }

# 更新模型配置
@router.post("/config")
async def update_model_configs(configs: dict, user_id: str = Depends(verify_token)):
    """更新模型配置"""
    try:
        # 保存配置到 Redis
        save_model_configs_to_redis(configs)
        
        # 更新全局模型配置
        from app.services.model_config import update_global_model_configs_from_redis
        success = update_global_model_configs_from_redis()
        if not success:
            raise HTTPException(status_code=500, detail="无法更新全局模型配置")
        
        # 清除所有用户的 LLM 缓存，使新配置生效
        model_service.clear_all_llm_cache()
        
        return {
            "code": 200,
            "data": {
                "message": "模型配置更新成功！"
            }
        }
    except Exception as e:
        logger.error(f"更新模型配置时出错: {e}")
        raise HTTPException(status_code=500, detail=f"更新模型配置失败: {str(e)}")

