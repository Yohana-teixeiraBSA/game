import redis.asyncio as aioredis

# Configura conexão com Redis local
redis = aioredis.from_url("redis://localhost:6380", decode_responses=True)
