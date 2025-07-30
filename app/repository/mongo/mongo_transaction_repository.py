

from bson import ObjectId
from app.dto.mongo.transaction_dto import TransactionDTO
from app.dto.websockets.player_dto import PlayerDTO
from app.mongo_client import db

collection = db["transactions"]

class MongoTransactionRepository:

    def __init__(self, collection = collection):

        self.collection = collection

    async def insert_transaction(self, transaction: TransactionDTO):
        document = transaction.model_dump()
        result = await self.collection.insert_one(document)
        object_id = result.inserted_id
        print(f"object_id: {object_id}")
        print(result)
        return str(object_id)

    async def get_transactions_player(self, player: PlayerDTO):
        cursor = self.collection.find({"player_id": player.player_id})
        transactions = await cursor.to_list(length=100)
        return transactions
    
    async def update_transaction_with_win_id(self, transaction: TransactionDTO): 
        update_win = await self.collection.update_one(
            {"_id": ObjectId(transaction.bet_id)},
            {"$set": {"win_id": transaction.win_id}}
        )
        return update_win

    async def update_transaction_with_refund_id(self, transaction: TransactionDTO): 
        update_refund = await self.collection.update_one(
            {"_id": ObjectId(transaction.bet_id)},
            {"$set": {"refund_id": transaction.refund_id}}
        )
        return update_refund