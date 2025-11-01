#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "prod"
    frontend_url: str = "http://localhost:5173"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_session_db: int = 0
    redis_model_db: int = 1  # Separate database for model configurations
    redis_mcp_db: int = 2
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