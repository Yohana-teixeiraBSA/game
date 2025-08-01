from pydantic import BaseModel
from app.dto.websockets.session_dto import SessionDTO

class HandleCashoutResquestDTO(BaseModel):
    player_id:str
    casino: str
    device: str
    currency: str
    regulation: str
    session: SessionDTO
    mongo_balance: int