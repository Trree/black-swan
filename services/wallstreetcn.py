from typing import List, Dict, Any, Optional
import requests

def my_fetch(url: str) -> Any:
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def wallstreetcn_live() -> List[Dict[str, Any]]:
    api_url = "https://api-one.wallstcn.com/apiv1/content/lives?channel=global-channel&limit=30"
    res = my_fetch(api_url)
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

def wallstreetcn_news() -> List[Dict[str, Any]]:
    api_url = "https://api-one.wallstcn.com/apiv1/content/information-flow?channel=global-channel&accept=article&limit=30"
    res = my_fetch(api_url)
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

def wallstreetcn_hot() -> List[Dict[str, Any]]:
    api_url = "https://api-one.wallstcn.com/apiv1/content/articles/hot?period=all"
    res = my_fetch(api_url)
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
        "wallstreetcn": wallstreetcn_live,
        "wallstreetcn-quick": wallstreetcn_live,
        "wallstreetcn-news": wallstreetcn_news,
        "wallstreetcn-hot": wallstreetcn_hot,
    }

# Example usage:
sources = define_source()
print(sources["wallstreetcn"]())