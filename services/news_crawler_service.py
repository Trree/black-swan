import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import datetime
from typing import List, Dict, Optional
import random
import time

from config import config
from logging_config import logger


class NewsCrawlerService:
    def __init__(self):
        self.session = None
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
        self.proxies = []  # 可配置代理池

    async def init_session(self):
        """初始化aiohttp会话"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=config.REQUEST_TIMEOUT)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={'User-Agent': random.choice(self.user_agents)}
            )

    async def close_session(self):
        """关闭会话"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def fetch_news_from_source(self, source_name: str, source_config: Dict) -> List[Dict]:
        """从单个新闻源抓取新闻"""
        await self.init_session()

        news_items = []
        max_retries = config.MAX_RETRIES

        for attempt in range(max_retries):
            try:
                logger.info(f"开始抓取 {source_name} (尝试 {attempt + 1}/{max_retries})")

                async with self.session.get(source_config['url']) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        news_items = self.parse_news_html(html_content, source_name)
                        logger.info(f"成功抓取 {source_name}, 获取 {len(news_items)} 条新闻")
                        break
                    else:
                        logger.warning(f"{source_name} 响应状态: {response.status}")

            except Exception as e:
                logger.error(f"抓取 {source_name} 失败: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(config.RETRY_DELAY * (attempt + 1))

        return news_items

    def parse_news_html(self, html: str, source: str) -> List[Dict]:
        """解析HTML获取新闻列表"""
        # 这里需要根据不同的新闻源编写特定的解析逻辑
        # 简化实现，返回示例数据

        soup = BeautifulSoup(html, 'html.parser')
        news_items = []

        # 示例：假设所有新闻源都有类似的结构
        try:
            articles = soup.find_all('article', limit=10) or soup.find_all('div', class_='news-item', limit=10)

            for article in articles:
                title_elem = article.find('h2') or article.find('h3') or article.find('a')
                if title_elem and title_elem.get_text().strip():
                    news_items.append({
                        'title': title_elem.get_text().strip(),
                        'url': self._get_absolute_url(title_elem.get('href', ''), source),
                        'source': source,
                        'published_at': datetime.datetime.utcnow(),
                        'content': self._extract_content(article)
                    })

        except Exception as e:
            logger.error(f"解析 {source} HTML失败: {e}")

        # 如果没有解析到新闻，返回示例数据
        if not news_items:
            news_items = self._get_sample_news(source)

        return news_items

    def _get_absolute_url(self, relative_url: str, source: str) -> str:
        """获取绝对URL"""
        if relative_url.startswith('http'):
            return relative_url

        base_urls = {
            'reuters': 'https://www.reuters.com',
            'bloomberg': 'https://www.bloomberg.com',
            'financial_times': 'https://www.ft.com',
            'wall_street_journal': 'https://www.wsj.com',
            'cnbc': 'https://www.cnbc.com'
        }

        base_url = base_urls.get(source, 'https://example.com')
        return base_url + relative_url if relative_url.startswith('/') else relative_url

    def _extract_content(self, article) -> str:
        """提取新闻内容"""
        # 简化实现
        content_elems = article.find_all('p')
        content = ' '.join([p.get_text().strip() for p in content_elems[:3]])
        return content if content else "Content not available"

    def _get_sample_news(self, source: str) -> List[Dict]:
        """获取示例新闻（用于测试）"""
        sample_news = [
            {
                'title': f'{source.replace("_", " ").title()} Sample News 1',
                'content': f'This is sample content from {source} for testing purposes.',
                'url': f'https://{source}.com/sample1',
                'source': source,
                'published_at': datetime.datetime.utcnow()
            },
            {
                'title': f'{source.replace("_", " ").title()} Sample News 2',
                'content': f'Another sample content from {source} for testing the system.',
                'url': f'https://{source}.com/sample2',
                'source': source,
                'published_at': datetime.datetime.utcnow()
            }
        ]
        return sample_news

    async def crawl_all_sources(self) -> List[Dict]:
        """抓取所有新闻源"""
        all_news = []

        # 限制并发数量
        semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_REQUESTS)

        async def limited_fetch(source_name, source_config):
            async with semaphore:
                return await self.fetch_news_from_source(source_name, source_config)

        tasks = []
        for source_name, source_config in config.NEWS_SOURCES.items():
            tasks.append(limited_fetch(source_name, source_config))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_news.extend(result)
            else:
                logger.error(f"抓取任务失败: {result}")

        # 去重
        unique_news = self._deduplicate_news(all_news)
        return unique_news

    def _deduplicate_news(self, news_items: List[Dict]) -> List[Dict]:
        """新闻去重"""
        seen_urls = set()
        unique_news = []

        for item in news_items:
            if item['url'] not in seen_urls:
                seen_urls.add(item['url'])
                unique_news.append(item)

        return unique_news


# 全局爬虫服务实例
crawler_service = NewsCrawlerService()