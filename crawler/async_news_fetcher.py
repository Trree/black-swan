import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(aiohttp.ClientError)  # 只对网络异常重试
)
async def fetch_url(rss_url, timeout=10, max_retries=3):
    async with aiohttp.ClientSession() as session:
        async with session.get(rss_url, timeout=timeout) as response:
            return await response.text() # 返回 RSS XML 内容

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(aiohttp.ClientError)  # 只对网络异常重试
)
async def fetch_url_json(rss_url, timeout=10):
    async with aiohttp.ClientSession() as session:
        async with session.get(rss_url, timeout=timeout) as response:
            return await response.json() # 返回 RSS XML 内容
