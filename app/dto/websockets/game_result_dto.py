from pydantic import BaseModel

class GameResultDTO(BaseModel):
    type: str | None = None 
    result: list[str] | None = None 
    win: bool | None = None
    new_balance: int
    message: str