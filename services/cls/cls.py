import asyncio
import time

import aiohttp

from services.cls.utils import get_search_params, get_cls_header


class Item:
    def __init__(self, id, brief, shareurl, ctime, is_ad=0, title=None):
        self.id = id
        self.title = title
        self.brief = brief
        self.shareurl = shareurl
        self.ctime = ctime
        self.is_ad = is_ad

async def my_fetch(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers= get_cls_header()) as response:
            return await response.json()

async def depth():
    api_url = "https://www.cls.cn/v3/depth/home/assembled/1000"
    params = dict(await get_search_params({}))
    res = await my_fetch(api_url, params)
    items = res["data"]["depth_list"]
    sorted_items = sorted(items, key=lambda k: k["ctime"], reverse=True)
    return [
        {
            "id": k["id"],
            "title": k.get("title") or k["brief"],
            "mobileUrl": k["shareurl"],
            "pubDate": k["ctime"] * 1000,
            "url": f'https://www.cls.cn/detail/{k["id"]}',
        }
        for k in sorted_items
    ]

async def hot():
    api_url = "https://www.cls.cn/v2/article/hot/list"
    params = dict(await get_search_params())
    res = await my_fetch(api_url, params)
    items = res["data"]
    return [
        {
            "id": k["id"],
            "title": k.get("title") or k["brief"],
            "mobileUrl": k["shareurl"],
            "url": f'https://www.cls.cn/detail/{k["id"]}',
        }
        for k in items
    ]

async def telegraph():
    api_url = "https://www.cls.cn/nodeapi/updateTelegraphList"
    last_time = int(time.time())
    params = get_search_params({})
    res = await my_fetch(api_url, params)
    items = [k for k in res["data"]["roll_data"] if not k.get("is_ad")]
    print(items)
    return [
        {
            "id": k["id"],
            "title": k.get("title") or k["brief"],
            "mobileUrl": k["shareurl"],
            "pubDate": k["ctime"] * 1000,
            "url": f'https://www.cls.cn/detail/{k["id"]}',
        }
        for k in items
    ]

def define_source():
    return {
        "cls": telegraph,
        "cls-telegraph": telegraph,
        "cls-depth": depth,
        "cls-hot": hot,
    }



asyncio.run((telegraph()))