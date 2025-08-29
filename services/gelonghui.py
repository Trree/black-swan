import asyncio

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

from crawler.async_news_fetcher import fetch_url


def parse_relative_date(relatieve_time: str, timezone: str) -> int:
    # 这里你需要根据 relatieve_time 和 timezone 实现时间解析逻辑
    # 目前返回 0 作为占位符
    return 0

def fetch_news() -> List[Dict[str, Any]]:
    base_url = "https://www.gelonghui.com"
    response = requests.get("https://www.gelonghui.com/news/")
    response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    news_items = []

    for el in soup.select(".article-content"):
        a = el.select_one(".detail-right > a")
        if a:
            url = a.get("href")
            title = a.find("h2").get_text() if a.find("h2") else ""
            info = el.select_one(".time > span:nth-child(1)")
            info_text = info.get_text() if info else ""
            relatieve_time_elem = el.select_one(".time > span:nth-child(3)")
            relatieve_time = relatieve_time_elem.get_text() if relatieve_time_elem else ""

            if url and title and relatieve_time:
                news_items.append({
                    "url": base_url + url,
                    "title": title,
                    "id": url,
                    "extra": {
                        "date": parse_relative_date(relatieve_time, "Asia/Shanghai"),
                        "info": info_text,
                    },
                })
    return news_items

# 示例用法
if __name__ == "__main__":
    news = fetch_news()
    for item in news:
        print(item)