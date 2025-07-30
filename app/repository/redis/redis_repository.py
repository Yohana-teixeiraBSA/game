from app.dto.websockets.session_dto import SessionDTO
from app.test_error import setup_logger
from app.redis_client import redis
import json

logger = setup_logger("Redis Repository")

class RedisRepository:
    def __init__ (self, redis_client):
        self.redis = redis_client

    async def get_balance(self, session: SessionDTO) -> int:
        key = f"balance:{session.player_id}"
        balance = await self.redis.get(key)
        return int(balance) if balance else 0
    
    async def set_balance(self, session: SessionDTO, value: int):
        key = f"balance:{session.player_id}"
        await self.redis.set(key, value)

    async def update_ranking(self, session: SessionDTO, value: int):
        await self.redis.zadd("players_balance", {session.player_id: value})

    async def get_is_logged(self, session: SessionDTO) -> SessionDTO | None :
        key = f"{session.player_id}"
        session_data = await self.redis.get(key)
        print("entrou no session_data",session_data)

        if session_data:
            try:
                session_dict = json.loads(session_data)
                return SessionDTO(is_logged = session_dict.get("is_logged", False))
            except Exception as e:
                print("Houve um erro ao tentar desserializar a sessão:",e)
                return None
        return None


    async def set_is_logged( self, session:SessionDTO | None):
        key = f"{session.player_id}"
        value = json.dumps({"is_logged": session.is_logged})
        await self.redis.set(key, value)

    async def delete_session(self, session: SessionDTO):
        await self.redis.delete(f"{session.player_id}")

        
    

    
    
