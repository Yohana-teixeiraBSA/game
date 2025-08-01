from fastapi import APIRouter
from app.service.mongo.game_history_service import GameHistoryService

router = APIRouter()

service = GameHistoryService()

@router.get("/game_history/{player_id}")
async def get_game_history( player_id: str):
    history = await service.get_game_history_by_player(player_id)
    return {"game_history": history}

