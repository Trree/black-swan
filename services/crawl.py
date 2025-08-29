import asyncio
import json

from crawler.async_news_fetcher import fetch_url


async def fetch_rss():
    with open('../rss.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(config)
    if 'rss' in config and isinstance(config['rss'], list):
        for rss_url in config['rss']:
            try:
                result = await fetch_url(rss_url)
                print(result)
            except Exception as e:
                print(f"Error processing {rss_url}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(fetch_rss())