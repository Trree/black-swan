import requests

def proxy_picture(url, mode):
    # 你需要根据实际情况实现 proxy_picture 函数
    # 这里仅做占位返回
    return f"proxy_{mode}({url})"

def fetch_toutiao_hot_events():
    url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
    response = requests.get(url)
    res = response.json()
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
    return result

# Example usage
if __name__ == "__main__":
    hot_events = fetch_toutiao_hot_events()
    for event in hot_events:
        print(event)