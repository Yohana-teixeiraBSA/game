from pydantic import BaseModel

class HandleSelectIndexDTO(BaseModel):
    player_id: str
    casino: str
    device: str
    currency: str
    regulation: str
    index: int