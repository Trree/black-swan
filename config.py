import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config:
    # OpenAI配置
    OPENAI_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    OPENAI_MODEL = os.getenv('MODEL')
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-zh-v1.5")
    OPENAI_MAX_TOKENS = 1000
    OPENAI_TEMPERATURE = 0.1

    # 数据库配置
    DATABASE_URL = "sqlite:///news.db"

    # 调度配置
    CRAWL_INTERVAL_MINUTES = 30  # 主要抓取间隔
    QUICK_CHECK_INTERVAL_MINUTES = 5  # 快速检查间隔
    WORKING_HOURS = {
        'start': '06:00',  # 早上6点开始
        'end': '22:00'  # 晚上10点结束
    }

    # 爬虫配置
    USER_AGENT = "BlackSwanMonitor/1.0 (+http://example.com/bot)"
    REQUEST_TIMEOUT = 30
    MAX_CONCURRENT_REQUESTS = 5

    # 分类阈值
    BLACK_SWAN_THRESHOLD = 0.7

    # 新闻源配置
    NEWS_SOURCES = {
        'reuters': {
            'url': 'https://www.reuters.com/news/archive',
            'type': 'general',
            'priority': 1
        },
        'bloomberg': {
            'url': 'https://mktnews.net/',
            'type': 'financial',
            'priority': 1
        },
        'financial_times': {
            'url': 'https://www.ft.com/',
            'type': 'financial',
            'priority': 1
        },
        'wall_street_journal': {
            'url': 'https://www.wsj.com/news/markets',
            'type': 'financial',
            'priority': 1
        },
        'cnbc': {
            'url': 'https://www.cnbc.com/world/?region=world',
            'type': 'financial',
            'priority': 2
        }
    }

    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FILE = "news_monitor.log"

    # 重试配置
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # 秒


config = Config()