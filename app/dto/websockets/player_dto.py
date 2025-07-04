from pydantic import BaseModel

class PlayerDTO(BaseModel):
    player_id: str
    type: str
    balance: int