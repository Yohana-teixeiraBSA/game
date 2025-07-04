from app.dto.websockets.session_dto import SessionDTO
from app.redis_client import redis
import json

class RedisRepository:
    @staticmethod
    async def get_balance(player_id: str) -> int:
        key = f"balance:{player_id}"
        balance = await redis.get(key)
        return int(balance) if balance else 0
    
    @staticmethod
    async def set_balance(player_id: str, value: int):
        key = f"{player_id}"
        await redis.set(key, value)

    @staticmethod
    async def update_ranking(player_id: str, value: int):
        await redis.zadd("players_balance", {player_id: value})
    
    @staticmethod
    async def get_session(player_id: str) -> SessionDTO | None :
        key = f"{player_id}"
        session_data = await redis.get(key)
        print("entrou no session_data",session_data)
        if session_data:
            try:
                session_dict = json.loads(session_data)
                return SessionDTO(**session_dict)
            except Exception as e:
                print(e)
                return None
        return None

    @staticmethod
    async def set_session(player_id: str, session:SessionDTO | None):
        key = f"{player_id}"
        await redis.set(key, json.dumps(session.model_dump()))

    @staticmethod
    async def get_is_logged(player_id: str) -> SessionDTO | None :
        key = f"{player_id}"
        session_data = await redis.get(key)
        print("entrou no session_data",session_data)
        if session_data:
            try:
                session_dict = json.loads(session_data)
                return SessionDTO(is_logged = session_dict.get("is_logged", False))
            except Exception as e:
                print("Houve um erro ao tentar desserializar a sessão:",e)
                return None
        return None

    @staticmethod
    async def set_is_logged(player_id: str, session:SessionDTO | None):
        key = f"{player_id}"
        value = json.dumps({"is_logged": session.is_logged})
        await redis.set(key, value)
    
    @staticmethod
    async def delete_session(player_id: str):
        await redis.delete(f"{player_id}")