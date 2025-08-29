import asyncio
from typing import List, Dict, Any, Optional
import requests
from watchfiles import awatch

from crawler.async_news_fetcher import fetch_url_json



async def wall_streetcn_live() -> List[Dict[str, Any]]:
    api_url = "https://api-one.wallstcn.com/apiv1/content/lives?channel=global-channel&limit=30"
    res = await fetch_url_json(api_url)
    items = res.get('data', {}).get('items', [])
    return [
        {
            "id": k["id"],
            "title": k.get("title") or k.get("content_text"),
            "extra": {
                "date": k["display_time"] * 1000,
            },
            "url": k["uri"],
        }
        for k in items
    ]

async def wallstreetcn_news() -> List[Dict[str, Any]]:
    api_url = "https://api-one.wallstcn.com/apiv1/content/information-flow?channel=global-channel&accept=article&limit=30"
    res = await fetch_url_json(api_url)
    items = res.get('data', {}).get('items', [])
    result = []
    for k in items:
        resource_type = k.get("resource_type")
        resource = k.get("resource", {})
        if resource_type not in ["theme", "ad"] and resource.get("type") != "live" and resource.get("uri"):
            result.append({
                "id": resource["id"],
                "title": resource.get("title") or resource.get("content_short"),
                "extra": {
                    "date": resource["display_time"] * 1000,
                },
                "url": resource["uri"],
            })
    return result

async def wallstreetcn_hot() -> List[Dict[str, Any]]:
    api_url = "https://api-one.wallstcn.com/apiv1/content/articles/hot?period=all"
    res = await fetch_url_json(api_url)
    day_items = res.get('data', {}).get('day_items', [])
    return [
        {
            "id": h["id"],
            "title": h.get("title", ""),
            "url": h["uri"],
        }
        for h in day_items
    ]

def define_source():
    return {
        "wallstreetcn": asyncio.run(wall_streetcn_live()),
        "wallstreetcn-quick": asyncio.run(wall_streetcn_live()),
        "wallstreetcn-news": asyncio.run(wallstreetcn_news()),
        "wallstreetcn-hot": asyncio.run(wallstreetcn_hot()),
    }

# Example usage:
sources = define_source()
if __name__ == "__main__":
    print(define_source())
