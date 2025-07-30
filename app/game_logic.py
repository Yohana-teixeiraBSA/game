import json
import random
from app.dto.websockets.game_session_status import GameSessionStatus
from app.dto.websockets.session_dto import SessionDTO
from app.redis_client import redis

SYMBOL_MINE = "💣"
SYMBOL_DIAMOND =  "💎"
GRID_SIZE = 25

async def start_grid_game(session: SessionDTO, num_mines: int) -> list[str]:
    if  num_mines < 1 or num_mines > 20:
        raise ValueError("Quantidade de minas deve estar entre 1 e 20.")

    grid = [SYMBOL_MINE] * num_mines + [SYMBOL_DIAMOND] * (GRID_SIZE - num_mines)
    random.shuffle(grid)

    session = SessionDTO(
        player_id=session.player_id,
        grid=grid,
        status=GameSessionStatus.PLAYING
    )

    await set_session(session = session)

    return grid


async def reveal_position(player_id:str, index:int) -> SessionDTO | None:
    session = await get_session(player_id)

    if not session:
        raise ValueError("Nenhuma grade ativa encontrada. Inicie uma rodada primeiro.")

    grid = session.grid
    symbol = grid[index]
    
    return symbol

def check_win(symbol: str) -> bool:
    return symbol == "💎"

def mask_grid(session: SessionDTO) -> list[str]:
    revealed_indexes = session.revealed
    grid = session.grid
    return [
        symbol if i in revealed_indexes else "x"
        for i, symbol in enumerate(grid)
    ]

@staticmethod
async def get_session(player_id: str) -> SessionDTO | None :
    key = f"{player_id}"
    session_data = await redis.get(key)
    if session_data:
        try:
            session_dict = json.loads(session_data)
            print("session_dict:", session_dict)
            if "status" not in session_dict:
                session_dict["status"] = GameSessionStatus.LOBBY
                print("⚠️ Inserido fallback status=LOBBY")
            return SessionDTO(**session_dict)
        except Exception as e:
            print("Erro ao carregar sessão:", e)
            return None
    return None

@staticmethod
async def set_session(session: SessionDTO | None):
    key = f"{session.player_id}"
    print("Sessão salva:", session)
    await redis.set(key, json.dumps(session.model_dump()))


async def generate_current_grid_view(player_id: str) -> list[list[str]]:
    session =  await get_session(player_id)
    if not session:
        return [["x"] * 5 for _ in range(5)]
    current_view = session.revealed
    grid_2d = [current_view[i:i+5] for i in range(0, 25, 5)]
    return grid_2d

async def broadcast_result(result, channel="slot_channel"):
    message = str(result)
    print(f"Broadcasting to Redis | Channel: {channel} | Message: {message}")
    await redis.publish(channel, message)