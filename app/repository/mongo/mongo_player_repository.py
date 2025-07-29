from app.mongo_client import db

collection = db["players"]

class MongoPlayerRepository:

    @staticmethod
    async def get_player(player_id: str):
        return await collection.find_one({"player_id": player_id})
    
    @staticmethod
    async def create_player(player_id: str, initial_balance: int = 0):
        document = {"player_id": player_id, "balance": initial_balance}
        await collection.insert_one(document)

    @staticmethod
    async def update_player(player_id: str, new_balance: int):
        update_result = await collection.update_one(
            {"player_id": player_id},
            {"$set":{"balance": new_balance}}
        )
        return update_result