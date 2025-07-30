from pydantic import BaseModel

from app.dto.mongo.transaction_type_dto import TransactionTypeDTO

class TransactionDTO(BaseModel):
    player_id: str | None = None
    balance: int = 1000
    new_balance: int | None = None
    bet: int | None = None
    win: int | None = None
    refund: int | None = None
    type: TransactionTypeDTO | None = None
    bet_id: str | None = None
    win_id: str | None = None
    refund_id: str | None = None

    