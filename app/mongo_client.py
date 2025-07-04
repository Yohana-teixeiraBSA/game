from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://admin:password@localhost:27017/")
db = client["slot_game"]
