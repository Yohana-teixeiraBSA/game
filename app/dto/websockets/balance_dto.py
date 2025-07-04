from pydantic import BaseModel

class BalanceDTO(BaseModel):
    player_balance: int