#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

import logging
from logging.config import dictConfig

def setup_logging(log_level=logging.INFO, log_file=None):
    """
    设置统一的日志配置
    
    Args:
        log_level: 日志级别，默认为 INFO
        log_file: 日志文件路径，如果为 None 则只输出到控制台
    """
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            }
        },
        "root": {"level": "INFO", "handlers": ["console"]},
    }
    
    # 如果指定了日志文件，则添加文件处理器
    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": log_file,
            "mode": "a",
            "encoding": "utf-8",
        }
        config["root"]["handlers"].append("file")
    
    dictConfig(config)

def get_logger(name):
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    return logging.getLogger(name)
