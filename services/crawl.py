import asyncio
import json
import feedparser

from crawler.async_news_fetcher import fetch_url

async def fetch_rss():
    with open('../rss.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    rss_feeds = config['rss']
    print(rss_feeds)

    for feed_name, rss_url in rss_feeds.items():
        try:
            result = await fetch_url(rss_url)
            feed = feedparser.parse(result)
            return {feed_name: feed.entries}
        except Exception as e:
            print(f"Error processing {rss_url}: {str(e)}")

if __name__ == "__main__":
    print(asyncio.run(fetch_rss()))