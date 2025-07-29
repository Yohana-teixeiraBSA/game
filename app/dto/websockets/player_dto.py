from pydantic import BaseModel

class PlayerDTO(BaseModel):
    player_id: str | None = None
    type: str | None = None
    balance: int | None = None