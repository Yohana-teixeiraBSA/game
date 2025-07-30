from app.dto.websockets.player_dto import PlayerDTO
from app.repository.mongo.mongo_player_repository import MongoPlayerRepository

class PlayerService:

    @staticmethod
    async def get_or_create_player(player: PlayerDTO) -> PlayerDTO:
        mongo_repo = MongoPlayerRepository()
        existing_player = await mongo_repo.get_player(player)
        if not existing_player:
            await mongo_repo.create_player(player)
            existing_player = await mongo_repo.get_player(player)
        return existing_player
    
    @staticmethod
    async def update_balance(player: PlayerDTO):
        mongo_repo = MongoPlayerRepository()
        result = await mongo_repo.update_player(player)
        return result