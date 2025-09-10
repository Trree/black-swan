import asyncio

from crawler.async_news_fetcher import fetch_url_json


def proxy_picture(url, mode):
    # 你需要根据实际情况实现 proxy_picture 函数
    # 这里仅做占位返回
    return f"proxy_{mode}({url})"

async def fetch_toutiao_hot_events():
    url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
    res = await fetch_url_json(url)
    data = res.get("data", [])
    result = []
    for k in data:
        item = {
            "id": k.get("ClusterIdStr"),
            "title": k.get("Title"),
            "url": f"https://www.toutiao.com/trending/{k.get('ClusterIdStr')}/",
            "extra": {
                "icon": proxy_picture(k.get("LabelUri", {}).get("url"), "encodeBase64URL") if k.get("LabelUri") and k["LabelUri"].get("url") else None
            }
        }
        result.append(item)
    return {"toutiao" : result}

# Example usage
if __name__ == "__main__":
    hot_events = asyncio.run(fetch_toutiao_hot_events())
    for event in hot_events:
        print(event)