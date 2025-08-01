from app.dto.websockets.game_history_dto import GameHistoryDTO
from app.mongo_client import db

collection = db["game_history"]

class MongoGameHistoryRepository:

    def __init__(self, collection=collection):
        self.collection = collection

    async def create_game_history(self, history: GameHistoryDTO):
        document = history.model_dump()
        insert_result = await self.collection.insert_one(document)
        return insert_result

    async def get_game_history_by_player(self, player_id: str):
        cursor = self.collection.find({"player_id": player_id})
        data = await cursor.to_list(length=None)
        return [GameHistoryDTO(**item) for item in data]
