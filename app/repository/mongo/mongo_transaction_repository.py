

from bson import ObjectId
from app.dto.mongo.transaction_dto import TransactionDTO
from app.mongo_client import db

collection = db["transactions"]

class MongoTransactionRepository:
    
    @staticmethod
    async def insert_transaction(transaction: TransactionDTO):
        document = transaction.model_dump()
        result = await collection.insert_one(document)
        object_id = result.inserted_id
        print(f"object_id: {object_id}")
        print(result)
        return str(object_id)

    @staticmethod
    async def get_transactions_player(player_id: str):
        cursor = collection.find({"player_id": player_id})
        transactions = await cursor.to_list(length=100)
        return transactions
    
    @staticmethod
    async def update_transaction_with_win_id(bet_id: str, win_id: str): 
        update_win = await collection.update_one(
            {"_id": ObjectId(bet_id)},
            {"$set": {"win_id": win_id}}
        )
        return update_win
    
    @staticmethod
    async def update_transaction_with_refund_id(bet_id: str, refund_id: str): 
        update_refund = await collection.update_one(
            {"_id": ObjectId(bet_id)},
            {"$set": {"refund_id": refund_id}}
        )
        return update_refund