# -*- coding: utf-8 -*-
from flask_redis import Redis
from rediscluster import RedisCluster
from .config import DefaultConfig

# Redis cache
redis_cache = Redis()
# Redis user info, will initialized in app
redis_cluster = RedisCluster(startup_nodes=DefaultConfig.REDIS_USERS_STARTUP_NODES,
                             decode_responses=True)
