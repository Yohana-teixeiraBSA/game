from enum import Enum

class TransactionTypeDTO(str,Enum):
    BET = "bet"
    WIN = "win"
    LOSS = "loss"
    REFOUND = "refound"
    
    