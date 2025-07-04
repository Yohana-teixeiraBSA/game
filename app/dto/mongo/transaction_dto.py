from pydantic import BaseModel

from app.dto.mongo.transaction_type_dto import TransactionTypeDTO

class TransactionDTO(BaseModel):
    player_id: str
    balance: int = 1000
    new_balance: int
    bet: int
    win: int
    refound: int | None = None
    type: TransactionTypeDTO