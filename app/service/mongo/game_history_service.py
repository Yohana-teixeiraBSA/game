from app.dto.websockets.game_history_dto import GameHistoryDTO
from app.repository.mongo.mongo_game_history_repository import MongoGameHistoryRepository

class GameHistoryService:

    def __init__(self, repository=None):
        self.repository = repository or MongoGameHistoryRepository()

    async def create_game_history(self, game_history: GameHistoryDTO):
        return await self.repository.create_game_history(game_history)    

    async def get_game_history_by_player(self, player_id: str):
        return await self.repository.get_game_history_by_player(player_id)

    