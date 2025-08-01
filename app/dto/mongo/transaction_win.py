from datetime import datetime
from pydantic import BaseModel
from app.dto.mongo.transaction_type_dto import TransactionTypeDTO

class TransactionWIN(BaseModel):
    timestamp: datetime 
    casino: str
    player_id: str
    currency: str
    balance: int = 1000
    new_balance: int
    win: int
    bet_id: str | None = None
    type: TransactionTypeDTO
