
from pydantic import BaseModel, Field

class BetDTO(BaseModel):
    bet_amount: int = Field(None, description="")
    num_mines: int = Field(None, ge=1, le=20, description=" O número de minas tem que ser entre 1 a 20.")
    
    def validate_bet(bet_amount, player_balance, num_mines):
        BetDTO(bet_amount=bet_amount, player_balance=player_balance, num_mines=num_mines)

        if bet_amount <= 0:
            raise ValueError("Aposta inválida: valor não pode ser zero ou negativo.")
        if bet_amount < 10:
            raise ValueError("Aposta mínima: 10 reais.")
        if bet_amount > player_balance:
            raise ValueError ("Aposta inválida: o valor da aposta não pode ser maior que o seu saldo!")
        if num_mines is None or not (1 <= num_mines < 21):
            raise ValueError ("Quantidade de minas inválidas. Escolha entre 1 e 20.")
        
         
        return BetDTO(bet_amount=bet_amount, num_mines=num_mines)
    