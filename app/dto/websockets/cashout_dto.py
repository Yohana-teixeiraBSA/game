from pydantic import BaseModel

class CashoutDTO(BaseModel):
    cashout: bool = True