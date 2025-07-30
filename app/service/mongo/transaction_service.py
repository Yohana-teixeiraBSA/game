from app.dto.mongo.transaction_dto import TransactionDTO
from app.dto.websockets.player_dto import PlayerDTO
from app.repository.mongo.mongo_transaction_repository import MongoTransactionRepository

class TransactionService:

    @staticmethod
    async def create_transaction(transaction_dto: TransactionDTO):
        mongo_repo = MongoTransactionRepository()
        return await mongo_repo.insert_transaction(transaction_dto)

    @staticmethod
    async def get_player_transactions(player: PlayerDTO):
        mongo_repo = MongoTransactionRepository()
        return await mongo_repo.get_transactions_player(player.player_id)

