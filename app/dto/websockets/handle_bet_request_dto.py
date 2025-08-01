from pydantic import BaseModel
from app.dto.websockets.bet__dto import BetDTO

class HandleBetRequestDTO(BaseModel):
    player_id: str
    casino: str
    device: str
    currency: str
    player_balance: int
    regulation: str
    vbet: BetDTO
    mongo_balance: int
