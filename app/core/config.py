#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str
    frontend_url: str
    redis_session_host: str
    redis_session_port: int
    redis_model_host: str
    redis_model_port: int
    redis_mcp_host: str
    redis_mcp_port: int
    redis_celery_host: str
    redis_celery_port: int
    localmodel_api_key: str
    siliconflow_api_key: str
    modelscope_api_key: str
    dashscope_api_key: str
    zhipuai_api_key: str
    moonshot_api_key: str
    doubao_api_key: str
    deepseek_api_key: str
    jwt_secret: str = "webspc_123"

    class Config:
        env_file = ".env"

settings = Settings()