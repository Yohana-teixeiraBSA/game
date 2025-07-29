from pydantic import BaseModel

from app.dto.mongo.transaction_type_dto import TransactionTypeDTO

class TransactionWIN(BaseModel):
    player_id: str
    balance: int = 1000
    new_balance: int
    win: int
    bet_id: str | None = None
    type: TransactionTypeDTO