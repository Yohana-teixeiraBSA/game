from app.dto.websockets.session_dto import SessionDTO
from app.test_error import setup_logger
from app.redis_client import redis
import json

logger = setup_logger("Redis Repository")

class RedisRepository:
    @staticmethod
    async def get_balance(session: SessionDTO) -> int:
        key = f"balance:{session.player_id}"
        balance = await redis.get(key)
        return int(balance) if balance else 0
    
    @staticmethod
    async def set_balance(session: SessionDTO, value: int):
        key = f"balance:{session.player_id}"
        await redis.set(key, value)

    @staticmethod
    async def update_ranking(session: SessionDTO, value: int):
        await redis.zadd("players_balance", {session.player_id: value})
        

    @staticmethod
    async def get_is_logged(session: SessionDTO) -> SessionDTO | None :
        key = f"{session.player_id}"
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
    async def set_is_logged( session:SessionDTO | None):
        key = f"{session.player_id}"
        value = json.dumps({"is_logged": session.is_logged})
        await redis.set(key, value)
    
    @staticmethod
    async def delete_session(session: SessionDTO):
        await redis.delete(f"{session.player_id}")


        
    

    
    
