from pydantic import BaseModel

from app.dto.websockets.game_session_status import GameSessionStatus

class SessionDTO(BaseModel):
    player_id: str 
    is_logged: bool = False
    grid: list | None = None
    revealed: list | None = None
    num_mines: int | None = None
    bet_amount: int | None = None
    status: GameSessionStatus | None = None
    accumulated_win: int = 0 
    bet_id: str | None = None
    win_id: str | None = None
