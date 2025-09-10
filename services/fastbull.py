import asyncio
from typing import List, Dict, Any

from bs4 import BeautifulSoup

from crawler.async_news_fetcher import fetch_url

# 假设 NewsItem 是一个 dict，实际项目可用 dataclass 或 pydantic 等替代
NewsItem = Dict[str, Any]


# todo 查询快讯
async def fastbull_express() -> List[NewsItem]:
    base_url = "https://www.fastbull.com"
    html = await fetch_url(f"{base_url}/cn/express-news")
    soup = BeautifulSoup(html, "html.parser")
    news_list = soup.select(".news-list")
    news: List[NewsItem] = []

    for el in news_list:
        a = el.select_one(".title_name")
        if a is None:
            continue
        url = a.get("href")
        title_text = a.get_text()
        import re
        match = re.search(r"【(.+)】", title_text)
        title = match.group(1) if match else title_text
        date = el.get("data-date")
        if url and title and date:
            news.append({
                "title": title if len(title) >= 4 else title_text,
                "link": base_url + url,
                "pubDate": int(date),
            })
    return news

async def fastbull_news() -> List[NewsItem]:
    base_url = "https://www.fastbull.com"
    html = await fetch_url(f"{base_url}/cn/news")
    soup = BeautifulSoup(html, "html.parser")
    trending = soup.select(".trending_type")
    news: List[NewsItem] = []

    for el in trending:
        a = el
        url = a.get("href")
        title = a.select_one(".title")
        title_text = title.get_text() if title else ""
        # 获取 brief ltr_ar_dir 内容
        brief_p = a.find("p", class_="brief ltr_ar_dir")
        brief = brief_p.get_text(strip=True) if brief_p else None
        date_elem = a.select_one("[data-date]")
        date = date_elem.get("data-date") if date_elem else None
        if url and title_text and date:
            news.append({
                "title": title_text,
                "link": base_url + url,
                "description": brief,
                "pubDate": int(date),
            })
    return news

def get_fastbull_sources():
    return {
        "fastbull": asyncio.run(fastbull_express()),
        "fastbull-news": asyncio.run(fastbull_news()),
    }

if __name__ == "__main__":
    print(asyncio.run(fastbull_express()))