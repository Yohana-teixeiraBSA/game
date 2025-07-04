from pydantic import BaseModel, Field

class BetModel(BaseModel):
    bet_amount: int = Field(..., description="Valor da aposta maior que zero")
    player_balance: int = Field(..., ge=0, description="Saldo atual do jogador")


