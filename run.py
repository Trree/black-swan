#!/usr/bin/env python3
"""
新闻监控系统启动脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import NewsMonitorApp
from logging_config import logger

def main():
    """主函数"""
    try:
        app = NewsMonitorApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("系统被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()