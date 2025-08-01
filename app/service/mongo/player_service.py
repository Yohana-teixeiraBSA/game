from app.dto.websockets.player_dto import PlayerDTO
from app.repository.mongo.mongo_player_repository import MongoPlayerRepository

class PlayerService:

    def __init__(self, repository=None):
        self.repository = repository or MongoPlayerRepository()

    async def get_or_create_player(self, player: PlayerDTO) -> PlayerDTO:
        existing_player = await self.repository.get_player(player)
        if not existing_player:
            await self.repository.create_player(player)
            existing_player = await self.repository.get_player(player)
        return existing_player

    async def update_balance(self, player: PlayerDTO):
        result = await self.repository.update_player(player)
        return result