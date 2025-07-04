from app.repository.mongo.mongo_player_repository import MongoPlayerRepository

class PlayerService:

    @staticmethod
    async def get_or_create_player(player_id: str):
        player = await MongoPlayerRepository.get_player(player_id)
        if not player:
            await MongoPlayerRepository.create_player(player_id, initial_balance = 1000)
            player = await MongoPlayerRepository.get_player(player_id)
        return player
    
    @staticmethod
    async def update_balance(player_id: str, new_balance: int):
        await MongoPlayerRepository.update_player(player_id, new_balance)