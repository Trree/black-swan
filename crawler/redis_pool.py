# redis_pool.py
import redis

# 全局 Redis 连接池
redis_pool = redis.ConnectionPool(
    host='100.107.167.15',
    port=6379,
    db=0,
    decode_responses=True,
    max_connections=100  # 最大连接数
)

def get_redis_conn():
    """从连接池获取 Redis 连接"""
    return redis.Redis(connection_pool=redis_pool)