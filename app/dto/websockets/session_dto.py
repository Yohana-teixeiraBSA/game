from pydantic import BaseModel
from app.dto.websockets.game_session_enum import GameSessionEnum

class SessionDTO(BaseModel):
    casino: str
    player_id: str 
    currency: str | None = None
    is_logged: bool = False
    device: str | None = None
    grid: list | None = None
    revealed: list | None = None
    num_mines: int | None = None
    bet_amount: int | None = None
    status: GameSessionEnum | None = None
    accumulated_win: int = 0 
    bet_id: str | None = None
    win_id: str | None = None
    regulation: str | None = None