import requests

def get_hot_stock():
    # 获取 cookie
    hq_resp = requests.get("https://xueqiu.com/hq")
    cookies = hq_resp.cookies.get_dict()
    # 组装 cookie 字符串
    cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])
    url = "https://stock.xueqiu.com/v5/stock/hot_stock/list.json?size=30&_type=10&type=10"
    headers = {
        "cookie": cookie_header,
        "User-Agent": "Mozilla/5.0",
    }
    res = requests.get(url, headers=headers)
    data = res.json()
    items = data.get("data", {}).get("items", [])
    # 过滤掉广告(ad为1)
    filtered = [k for k in items if not k.get("ad")]
    # 构造返回结果
    result = []
    for k in filtered:
        result.append({
            "id": k.get("code"),
            "url": f"https://xueqiu.com/s/{k.get('code')}",
            "title": k.get("name"),
            "extra": {
                "info": f"{k.get('percent')}% {k.get('exchange')}"
            }
        })
    return result

# 提供与原 defineSource 类似的接口
def xueqiu_source():
    return {
        "xueqiu": get_hot_stock,
        "xueqiu-hotstock": get_hot_stock,
    }