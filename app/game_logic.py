import random
from app.redis_client import redis
from app.models import BetModel

SYMBOLS = ["🍒", "7️⃣", "⭐", "🔔", "🍋"]

def validate_bet(bet_amount, player_balance):
    bet_model = BetModel(bet_amount=bet_amount, player_balance=player_balance)

    if bet_amount <= 0:
        raise ValueError("Aposta inválida: valor não pode ser zero ou negativo.")
    if bet_amount < 5:
        raise ValueError("Aposta mínima: 5 reais.")
    if bet_amount > player_balance:
        raise ValueError ("Aposta inválida: o valor da aposta não pode ser maior que o seu saldo!")
    
    return  bet_model

def start_slot_round():
    return [random.choice(SYMBOLS) for _ in range(3)]

def check_win(result):
    return len(set(result)) == 1

async def broadcast_result(result, channel="slot_channel"):
    message = str(result)
    print(f"Broadcasting to Redis | Channel: {channel} | Message: {message}")
    await redis.publish(channel, message)