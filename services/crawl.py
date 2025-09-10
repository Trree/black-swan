import asyncio
import json

from crawler.async_news_fetcher import fetch_url


async def fetch_rss():
    with open('../rss.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    rss_feeds = config['rss']
    print(rss_feeds)

    for feed_name, rss_url in rss_feeds.items():
        try:
            result = await fetch_url(rss_url)
            print(result)
        except Exception as e:
            print(f"Error processing {rss_url}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(fetch_rss())