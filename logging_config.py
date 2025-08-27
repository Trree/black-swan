import logging
from logging.handlers import RotatingFileHandler
import os
from config import config


def setup_logging():
    """配置日志系统"""
    # 创建日志目录
    os.makedirs('logs', exist_ok=True)

    # 创建根日志记录器
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.LOG_LEVEL))

    # 文件处理器 - 滚动日志
    file_handler = RotatingFileHandler(
        filename=f'logs/{config.LOG_FILE}',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# 全局日志实例
logger = setup_logging()