from datetime import datetime
from pydantic import BaseModel

class GameHistoryDTO(BaseModel):
    casino: str
    player_id: str 
    currency: str 
    bet_amount: int | None = None
    balance: int | None = None
    new_balance: int | None = None
    win: int | None = None
    win_id : str | None = None
    num_mines: int | None = None
    revealed: list[str] | None = None
    timestamp: datetime | None = None
