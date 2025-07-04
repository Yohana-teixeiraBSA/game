from app.mongo_client import db

collection = db["transactions"]

class MongoRepository:
    @staticmethod
    async def insert_transaction(player_id: str, balance: int, new_balance: int, bet: int, win: int, refound: int):
        document = {"player_id": player_id, "balance": balance, "new_balance": new_balance, "bet":bet, "refound": refound}
        result = await collection.insert_one(document)
        return str(result.inserted_id)

    async def get_transactions_player(player_id: str):
        cursor = collection.find({"player_id": player_id})
        transactions = await cursor.to_list(length=100)
        return transactions