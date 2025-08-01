from app.dto.websockets.player_dto import PlayerDTO
from app.mongo_client import db

collection = db["players"]

class MongoPlayerRepository:

    def __init__(self, collection=collection):
        self.collection = collection

    async def get_player(self, player: PlayerDTO) -> PlayerDTO | None:
        data = await self.collection.find_one({"player_id": player.player_id})
        if data:
            return PlayerDTO(**data)
        return None

    async def create_player(self, player: PlayerDTO):
        document = {"player_id": player.player_id, "balance": player.balance}
        await self.collection.insert_one(document)

    async def update_player(self, player: PlayerDTO):
        update_result = await self.collection.update_one(
            {"player_id": player.player_id},
            {"$set":{"balance": player.balance}}
        )
        return update_result
    