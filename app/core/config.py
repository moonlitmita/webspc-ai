#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "dev"
    frontend_url: str = "http://localhost:5173"
    redis_session_host: str = "localhost"
    redis_session_port: int = 6380
    redis_model_host: str = "localhost"
    redis_model_port: int = 6381
    redis_mcp_host: str = "localhost"
    redis_mcp_port: int = 6382
    redis_celery_host: str = "localhost"
    redis_celery_port: int = 6383
    localmodel_api_key: str = "default"
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