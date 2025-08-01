from app.dto.mongo.transaction_dto import TransactionDTO
from app.dto.websockets.player_dto import PlayerDTO
from app.repository.mongo.mongo_transaction_repository import MongoTransactionRepository

class TransactionService:

    def __init__(self, repository=None):
        self.repository = repository or MongoTransactionRepository()

    async def create_transaction(self, transaction_dto: TransactionDTO):
        return await self.repository.insert_transaction(transaction_dto)

    async def get_player_transactions(self, player: PlayerDTO):
        return await self.repository.get_transactions_player(player)

