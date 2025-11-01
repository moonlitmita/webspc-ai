#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logger_config import setup_logging, get_logger
from app.api import chat, mcp, session, models
from app.core.lifespan import lifespan
from dotenv import load_dotenv
import os

load_dotenv()

# 设置日志配置，将日志同时输出到控制台和文件
setup_logging(log_file="application.log")

# 获取当前模块的日志记录器
logger = get_logger(__name__)

# ---------- 注册生命周期 ----------
app = FastAPI(title="WebSPC Assistant", lifespan=lifespan)

# 1. 读环境变量；开发机可以不设，默认给 localhost 5173
ENV = os.getenv("ENV", "dev")                       # dev / prod
FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173" if ENV == "dev" else "https://webspc.top"
)

# 2. 组装 origins
origins = [origin.strip() for origin in FRONTEND_URL.split(",") if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(mcp.router)
app.include_router(session.router)
app.include_router(models.router)
