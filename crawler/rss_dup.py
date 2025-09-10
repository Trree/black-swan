import redis
import time

from crawler.redis_pool import get_redis_conn


class RSSDeduplicator:
    def __init__(self):
        self.redis = get_redis_conn()
        self.expire_days = 30
        self.key_name = 'rss_seen_set'
        # 设置清理频率（每处理多少条记录后清理一次）
        self.cleanup_frequency = 100
        self.counter = 0

    def is_duplicate(self, item):
        key = item.get('guid') or item.get('link')
        if not key:
            return False

        # 定期清理（每处理cleanup_frequency条记录后清理一次）
        self.counter += 1
        if self.counter >= self.cleanup_frequency:
            self.cleanup_old_data()
            self.counter = 0

        # 检查是否存在
        if self.redis.zscore(self.key_name, key) is not None:
            return True

        # 添加新数据，使用当前时间作为分数
        self.redis.zadd(self.key_name, {key: time.time()})
        return False

    def cleanup_old_data(self):
        # 计算一个月前的时间戳
        cutoff_time = time.time() - (self.expire_days * 24 * 60 * 60)
        # 删除分数(时间戳)小于cutoff_time的所有成员
        self.redis.zremrangebyscore(self.key_name, 0, cutoff_time)

if __name__ == "__main__":
    rss_items = [
        {'guid': '1', 'link': 'https://example.com/a', 'title': 'A'},
        {'guid': '2', 'link': 'https://example.com/b', 'title': 'B'},
        {'guid': '3', 'link': 'https://example.com/e', 'title': 'A'}, # 重复
        {'guid': '', 'link': 'https://example.com/c', 'title': 'C'},
        {'guid': '', 'link': 'https://example.com/c', 'title': 'C'}, # 重复
        {'title': 'No Link'}, # 没有 guid/link，不去重
    ]
    def process(items):
        print("Processing:", items)

    try:
        dedup = RSSDeduplicator()
        for it in rss_items:
            if dedup.is_duplicate(it):
                continue
            process(it)
    except* (redis.ConnectionError, redis.TimeoutError) as eg:
        print(f"Redis连接问题: {eg}")