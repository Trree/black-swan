import asyncio

from services.crawl import fetch_rss
from services.fastbull import get_fastbull_sources
from services.gelonghui import fetch_gelonghui
from services.jin10 import fetch_jin10_news
from services.mktnews import fetch_mktnews
from services.toutiao import fetch_toutiao_hot_events
from services.wallstreetcn import get_wallstree


def get_entry_description(entry):
    """安全获取条目描述内容"""
    if hasattr(entry, 'description'):
        return entry.description
    elif hasattr(entry, 'summary'):
        return entry.summary
    elif hasattr(entry, 'content'):
        return entry.content[0].value
    return ""

def query_all():
    rss = asyncio.run(fetch_rss())
    fastbull = get_fastbull_sources()
    gelonghui = fetch_gelonghui()
    jin10 = asyncio.run(fetch_jin10_news())
    mkt = asyncio.run(fetch_mktnews())
    toutiao = asyncio.run(fetch_toutiao_hot_events())
    wallstreet = get_wallstree()
    merged_dict = {**rss, **fastbull, **gelonghui, **jin10, **mkt, **toutiao, **wallstreet}
    return merged_dict

if __name__ == "__main__":
    print(query_all())