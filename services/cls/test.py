import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from services.cls.utils import get_search_params

ROOT_URL = "https://www.cls.cn"


def parse_date(timestamp):
    # timestamp 为毫秒数
    dt = datetime.utcfromtimestamp(timestamp / 1000)
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

def render_description(article_detail):
    # 这里简单返回正文，实际可自定义模板
    return article_detail.get("content", "")

def fetch_hot_articles(limit=50):
    api_url = f"{ROOT_URL}/v2/article/hot/list"
    headers = {
        'accept':'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    resp = requests.get(api_url, headers = headers, params=get_search_params({}))
    resp.raise_for_status()
    data = resp.json()
    items = []
    for item in data["data"][:limit]:
        items.append({
            "title": item.get("title") or item.get("brief"),
            "link": f"{ROOT_URL}/detail/{item['id']}",
            "pubDate": parse_date(item["ctime"] * 1000),
        })
    return items

def fetch_article_detail(link):
    resp = requests.get(link)
    soup = BeautifulSoup(resp.text, "html.parser")
    script = soup.select_one("script#__NEXT_DATA__")
    if not script:
        return {}
    next_data = json.loads(script.text)
    article_detail = (
        next_data.get("props", {})
        .get("initialState", {})
        .get("detail", {})
        .get("articleDetail", {})
    )
    return article_detail

def enrich_items(items):
    for item in items:
        article_detail = fetch_article_detail(item["link"])
        item["author"] = article_detail.get("author", {}).get("name", "")
        item["description"] = render_description(article_detail)
    return items

def get_cls_hot(limit=50):
    items = fetch_hot_articles(limit)
    items = enrich_items(items)
    return {
        "title": "财联社 - 热门文章排行榜",
        "link": ROOT_URL,
        "items": items,
    }

if __name__ == "__main__":
    result = get_cls_hot(10)
    print(json.dumps(result, ensure_ascii=False, indent=2))