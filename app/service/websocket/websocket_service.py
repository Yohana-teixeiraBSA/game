from fastapi import WebSocket
from app.dto.websockets.balance_dto import BalanceDTO
from app.dto.websockets.error_dto import ErrorDTO
from app.dto.websockets.game_result_dto import GameResultDTO
from app.dto.websockets.player_dto import PlayerDTO
import redis.asyncio as redis

class WebSocketService():
    def __init__(self, websocket: WebSocket, redis_client):
        self.__websocket = websocket
        self.__redis = redis

    async def send_error(self, error:ErrorDTO):
        await self.__websocket.send_json(error.model_dump())

    async def send_game_result(self, game_result: GameResultDTO):
        await self.__websocket.send_json(game_result.model_dump())

    async def send_game_end(self, game_result: GameResultDTO):
        await self.__websocket.send_json(game_result.model_dump())
    
    async def send_player(self, player: PlayerDTO ):
        await self.__websocket.send_json(player.model_dump())

    async def send_balance(self, balance: BalanceDTO):
        await self.__websocket.send_json(balance.model_dump())
       