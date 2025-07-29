
from pydantic import BaseModel

from app.dto.mongo.transaction_type_dto import TransactionTypeDTO


class TransactionREFUND(BaseModel):
    player_id: str
    balance: int = 1000
    new_balance: int
    refund: int
    bet_id: str | None = None
    type: TransactionTypeDTO