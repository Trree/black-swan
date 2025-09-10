import asyncio
import re
import time
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

import requests

from crawler.async_news_fetcher import fetch_url


def parse_relative_date(time_str: str, tz: str = "Asia/Shanghai") -> datetime:
    # 假设 time_str 是形如 "18:24:05" 或 "08-27 18:24:05"（金十快讯格式）
    now = datetime.now(timezone(timedelta(hours=8)))  # 亚洲上海时区
    if re.match(r'^\d{2}:\d{2}:\d{2}$', time_str):
        # 只有时间，今天
        dt = datetime(now.year, now.month, now.day, *map(int, time_str.split(":")), tzinfo=now.tzinfo)
    elif re.match(r'^\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', time_str):
        # 月-日 时:分:秒
        m, d, h, mi, s = map(int, re.findall(r'\d+', time_str))
        dt = datetime(now.year, m, d, h, mi, s, tzinfo=now.tzinfo)
    else:
        try:
            dt = datetime.fromisoformat(time_str)
        except Exception:
            dt = now
    return dt

async def fetch_jin10_news() :
    timestamp = int(time.time() * 1000)
    url = f"https://www.jin10.com/flash_newest.js?t={timestamp}"
    resp = await fetch_url(url)
    raw_data = resp

    # 移除开头的变量声明和末尾的分号
    json_str = re.sub(r'^var\s+newest\s*=\s*', '', raw_data)
    json_str = re.sub(r';*$', '', json_str).strip()

    data = []
    try:
        data = requests.utils.json.loads(json_str)
    except Exception:
        import json
        data = json.loads(json_str)

    result = []
    for k in data:
        k_data = k.get('data', {})
        title_or_content = k_data.get('title') or k_data.get('content')
        if not title_or_content or 5 in (k.get('channel') or []):
            continue
        text = re.sub(r'</?b>', '', title_or_content)
        m = re.match(r'^【([^】]*)】(.*)$', text)
        if m:
            title, desc = m.group(1), m.group(2)
        else:
            title, desc = text, None
        item = {
            "id": k.get("id"),
            "title": title,
            "pubDate": int(parse_relative_date(k.get("time", ""), "Asia/Shanghai").timestamp() * 1000),
            "url": f"https://flash.jin10.com/detail/{k.get('id')}",
            "extra": {
                "hover": desc,
                "info": "✰" if k.get("important") else None,
            }
        }
        result.append(item)
    return {"jin10" : result}

if __name__ == "__main__":
    news_items = asyncio.run(fetch_jin10_news())
    print(news_items)