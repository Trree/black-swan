import aiohttp

async def fetch_url(rss_url, timeout=10):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(rss_url, timeout=timeout) as response:
                if response.status == 200:
                    return await response.text() # 返回 RSS XML 内容
                else:
                    print(f"Failed to fetch {rss_url}: HTTP {response.status}")
                    return None
    except Exception as e:
        print(f"Error processing {rss_url}: {str(e)}")
        return None


async def fetch_url_json(rss_url, timeout=10):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(rss_url, timeout=timeout) as response:
                if response.status == 200:
                    return await response.json() # 返回 RSS XML 内容
                else:
                    print(f"Failed to fetch {rss_url}: HTTP {response.status}")
                    return None
    except Exception as e:
        print(f"Error processing {rss_url}: {str(e)}")
        return None