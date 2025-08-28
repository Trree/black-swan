import requests

def get_hot_stocks():
    session = requests.Session()
    # 访问主页获取 cookies，模拟浏览器
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "https://xueqiu.com/hq",
        "X-Requested-With": "XMLHttpRequest",
    }
    homepage = session.get("https://xueqiu.com/hq", headers=headers)
    # 获取 cookies
    cookies = session.cookies.get_dict()
    cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
    # 请求数据接口
    url = "https://stock.xueqiu.com/v5/stock/hot_stock/list.json?size=30&_type=10&type=10"
    headers["Cookie"] = cookie_str
    res = session.get(url, headers=headers)
    print(res.status_code, res.text)
    data = res.json()
    # 后续解析同前
    items = data["data"]["items"]
    results = []
    for k in items:
        if not k.get("ad"):
            results.append({
                "id": k["code"],
                "url": f"https://xueqiu.com/s/{k['code']}",
                "title": k["name"],
                "extra": {
                    "info": f"{k['percent']}% {k['exchange']}",
                }
            })
    return results

# 提供与原 defineSource 类似的接口
def xueqiu_source():
    return {
        "xueqiu": get_hot_stocks,
        "xueqiu-hotstock": get_hot_stocks,
    }

