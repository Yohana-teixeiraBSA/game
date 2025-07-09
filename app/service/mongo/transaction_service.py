from app.dto.mongo.transaction_dto import TransactionDTO
from app.repository.mongo.transaction_repository import MongoRepository

class TransactionService:

    @staticmethod
    async def create_transaction(data: TransactionDTO):
        return await MongoRepository.insert_transaction(data.player_id, data.balance, data.new_balance, data.bet, data.win, data.refund)

    @staticmethod
    async def get_player_transactions(player_id: str):
        return await MongoRepository.get_transactions_player(player_id)