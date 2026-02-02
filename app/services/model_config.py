#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

import os
from typing import Dict, List, Tuple
from langchain_openai import ChatOpenAI
from app.core.logger_config import get_logger
from app.services.redis_tools import model_redis_client  # This client should connect to Redis with AOF+RDB persistence enabled
from app.core.config_model import model_configs
from app.core.http_client_config import create_sync_http_client
import json

logger = get_logger(__name__)

MODEL_CONFIGS = model_configs

# Model configuration persistence functions
def load_model_configs_from_redis() -> dict:
    """
    从 Redis 加载模型配置
    """
    try:
        data = model_redis_client.get('model_configs')
        if data:
            return json.loads(data)
        else:
            # 如果 Redis 中没有配置，返回默认配置
            return MODEL_CONFIGS
    except Exception as e:
        logger.error(f"从 Redis 加载模型配置时出错: {e}")
        # 出错时返回默认配置
        return MODEL_CONFIGS

def check_model_configs_in_redis() -> bool:
    """
    检查 Redis 中是否存在模型配置
    """
    try:
        return model_redis_client.exists('model_configs') == 1
    except Exception as e:
        logger.error(f"检查 Redis 中模型配置时出错: {e}")
        return False

def save_model_configs_to_redis(configs: dict):
    """
    将模型配置保存到 Redis
    """
    try:
        model_redis_client.set('model_configs', json.dumps(configs, indent=2))
        logger.info("模型配置已保存到 Redis")
    except Exception as e:
        logger.error(f"保存模型配置到 Redis 时出错: {e}")
        raise e

def update_global_model_configs_from_redis():
    """
    从 Redis 重新加载模型配置到全局变量
    """
    global MODEL_CONFIGS
    try:
        data = model_redis_client.get('model_configs')
        if data:
            new_configs = json.loads(data)
            MODEL_CONFIGS = new_configs
            logger.info("全局模型配置已从 Redis 更新")
            return True
        else:
            logger.warning("Redis 中未找到模型配置，保持默认配置")
            return False
    except Exception as e:
        logger.error(f"从 Redis 更新全局模型配置时出错: {e}")
        return False

class ModelConfigService:
    # ---------- 用户级 ----------
    # user_id -> ChatOpenAI 实例 (in-memory cache for performance)
    _user_llm: Dict[str, ChatOpenAI] = {}

    # 系统兜底
    _default_provider = "siliconflow"
    _default_model_id = "qwen2.5-7b-instruct"

    # Redis key template
    _USER_MODEL_KEY_TPL = "user_model:{user_id}"

    # ---------- 内部工具 ----------
    def _get_cfg(self, provider: str, model_id: str) -> Dict:
        # 从 Redis 获取最新配置，如果不存在则使用全局默认配置
        from app.services.model_config import MODEL_CONFIGS
        cfg = load_model_configs_from_redis().get(provider, {}).get("models", {}).get(model_id)
        if not cfg:
            cfg = MODEL_CONFIGS.get(provider, {}).get("models", {}).get(model_id)
            if not cfg:
                raise ValueError(f"Invalid provider={provider} or model_id={model_id}")
        # 返回包含provider信息的配置
        return {**cfg, "provider": provider}

    def _build_llm(self, cfg: Dict) -> ChatOpenAI:
        api_key = os.getenv(cfg["api_key_env"])
        if not api_key:
            raise ValueError(f"Env {cfg['api_key_env']} not set")

        # 使用HTTP客户端配置来创建LLM实例
        base_url = cfg["base_url"].strip()

        # 创建自定义HTTP客户端以处理HTTP/2兼容性问题
        http_client = create_sync_http_client(base_url, api_key)

        return ChatOpenAI(
            base_url=base_url,
            api_key=api_key,
            model=cfg["name"],
            http_client=http_client
        )

    # ---------- 对外 API ----------
    def get_user_current(self, user_id: str) -> Tuple[str, str]:
        """返回 (provider, model_id) - 从Redis获取"""
        key = self._USER_MODEL_KEY_TPL.format(user_id=user_id)
        stored = model_redis_client.get(key)
        if stored:
            try:
                provider, model_id = stored.split(':', 1)
                # 延长TTL
                model_redis_client.expire(key, 3600 * 24)  # 24小时
                return (provider, model_id)
            except ValueError:
                # 如果格式不正确，使用默认值并更新Redis
                self.set_model(user_id, self._default_provider, self._default_model_id)
                return (self._default_provider, self._default_model_id)
        else:
            # 如果Redis中没有，返回默认值，并在Redis中设置
            self.set_model(user_id, self._default_provider, self._default_model_id)
            return (self._default_provider, self._default_model_id)

    def get_current_model_config(self, user_id: str) -> Dict:
        """给 /current 接口用的完整配置（含 id）"""
        provider, model_id = self.get_user_current(user_id)
        cfg = self._get_cfg(provider, model_id)
        return {"id": model_id, "provider": provider, **cfg}

    def get_llm(self, user_id: str) -> ChatOpenAI:
        """用户级 LLM 实例（懒加载）"""
        if user_id not in self._user_llm:
            provider, model_id = self.get_user_current(user_id)
            cfg = self._get_cfg(provider, model_id)
            self._user_llm[user_id] = self._build_llm(cfg)
        return self._user_llm[user_id]

    def set_model(self, user_id: str, provider: str, model_id: str) -> bool:
        """切换用户级模型，并存储到Redis"""
        try:
            cfg = self._get_cfg(provider, model_id)
        except ValueError:
            return False

        # 1. 保存到Redis
        key = self._USER_MODEL_KEY_TPL.format(user_id=user_id)
        model_redis_client.setex(key, 3600 * 24, f"{provider}:{model_id}")  # 保存24小时

        # 2. 重建 LLM 实例（即时生效）
        self._user_llm[user_id] = self._build_llm(cfg)
        return True

    # 清除用户 LLM 缓存
    def clear_user_llm_cache(self, user_id: str):
        """清除用户的 LLM 缓存，强制重新创建"""
        if user_id in self._user_llm:
            del self._user_llm[user_id]

    def clear_all_llm_cache(self):
        """清除所有用户的 LLM 缓存"""
        self._user_llm.clear()

    # ---------- 辅助 ----------
    def list_providers(self) -> List[Dict[str, str]]:
        configs = load_model_configs_from_redis()
        return [{"key": k, "label": v["label"]} for k, v in configs.items()]

    def list_models_by_provider(self, provider: str) -> List[Dict]:
        configs = load_model_configs_from_redis()
        if provider not in configs:
            return []
        return list(configs[provider]["models"].values())

# Global instance
model_service = ModelConfigService()