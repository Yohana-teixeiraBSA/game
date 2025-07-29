from app.dto.websockets.player_dto import PlayerDTO
from app.repository.mongo.mongo_player_repository import MongoPlayerRepository

class PlayerService:

    @staticmethod
    async def get_or_create_player(player: PlayerDTO) -> PlayerDTO:
        existing_player = await MongoPlayerRepository.get_player(player.player_id)
        if not existing_player:
            await MongoPlayerRepository.create_player(player.player_id, initial_balance=1000)
            existing_player = await MongoPlayerRepository.get_player(player.player_id)
        return existing_player
    
    @staticmethod
    async def update_balance(player: PlayerDTO):
        result = await MongoPlayerRepository.update_player(player.player_id, player.balance)
        return result