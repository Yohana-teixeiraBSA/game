from pydantic import BaseModel

from app.dto.mongo.transaction_type_dto import TransactionTypeDTO

class TransactionBET(BaseModel):
    player_id: str
    balance: int = 1000
    new_balance: int
    bet: int
    win_id: str | None = None
    refund_id: str | None = None
    type: TransactionTypeDTO