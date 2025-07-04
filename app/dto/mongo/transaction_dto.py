from pydantic import BaseModel

class TransactionDTO(BaseModel):
    player_id: str
    balance: int = 1000
