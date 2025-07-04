from app.mongo_client import db

collection = db["transactions"]

class MongoRepository:
    @staticmethod
    async def insert_transaction(player_id: str, balance: int):
        document = {"player_id": player_id, "balance": balance }
        result = await collection.insert_one(document)
        return str(result.inserted_id)

    async def get_transactions_player(player_id: str):
        cursor = collection.find({"player_id": player_id})
        transactions = await cursor.to_list(length=100)
        return transactions