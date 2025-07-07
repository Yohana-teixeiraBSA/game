from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.dto.mongo.transaction_dto import TransactionDTO
from app.dto.mongo.transaction_type_dto import TransactionTypeDTO
from app.dto.websockets.balance_dto import BalanceDTO
from app.dto.websockets.session_dto import SessionDTO
from app.redis_client import redis
from app.game_logic import start_slot_round, check_win, broadcast_result, validate_bet
from app.models import BetModel
import asyncio
from app.dto.websockets.error_dto import ErrorDTO
from app.dto.websockets.game_result_dto import GameResultDTO
from app.dto.websockets.player_dto import PlayerDTO
from app.repository.redis.player_repository import RedisRepository
from app.service.mongo.transaction_service import TransactionService
from app.service.websocket.websocket_service import WebSocketService
from app.service.mongo.player_service import PlayerService

app = FastAPI()

# WebSocket endpoint para receber apostas e enviar resultados
# ws://localhost:8000/ws/slot/{player_id}
@app.websocket("/ws/slot/{player_id}")
async def slot_websocket(websocket: WebSocket, player_id: str):
    existing_session = await RedisRepository.get_session(player_id)
    
    player = await PlayerService.get_or_create_player(player_id)
    mongo_balance = player["balance"]

    if existing_session and existing_session.is_logged:
        await websocket.accept()
        
        error_dto = ErrorDTO(
            error = "Já existe uma sessão ativa para esse jogador.",
            # session = existing_session.model_dump() -> com esse comando pego os dados contidos no existing_session e retorno um JSON;
        )
        await websocket.send_json(error_dto.model_dump())
        await websocket.close()
        return
    # Aceita uma conexão
    await websocket.accept()

    if existing_session:
        existing_session.is_logged = True
        session = existing_session
    else:
        session = SessionDTO(player_id=player_id, is_logged = True)
    
    await RedisRepository.set_session(player_id, session)
  
    running = True
    
    ws_service = WebSocketService(websocket, redis)
    print("Enviando saldo inicial para o cliente...")
    
    balance_dto = BalanceDTO(player_balance = mongo_balance)
    await ws_service.send_balance(balance_dto)
    
    player = PlayerDTO(player_id = player_id, type = "saldo", balance = mongo_balance)
    await ws_service.send_player(player)

    try:
        while running:  
                # recebe mensagens do cliente
                data = await websocket.receive_json()
                # Valida dados da aposta
                bet = BetModel(**data)
                 
                bet.player_balance = mongo_balance
                
                bet_amount = data.get("bet_amount")
                player_balance = mongo_balance

                try:
                    vbet = validate_bet(bet_amount, player_balance)
                except Exception as e:
                    error_dto = ErrorDTO(error = str(e))
                    await ws_service.send_error(error_dto)
                    continue
                
                result = start_slot_round()
                win = check_win(result)

                simulate_error = data.get("simulate_error")
                refound_value = False
                try:
                    if simulate_error:
                        raise Exception("Simulando desconexão ou erro no meio do processo.")
                    if win:
                        mongo_balance += int(vbet.bet_amount * 0.5)
                        tx_type = TransactionTypeDTO.WIN
                        win_value = mongo_balance - player_balance 
                    else:
                        mongo_balance -= vbet.bet_amount
                        tx_type = TransactionTypeDTO.LOSS
                        win_value = None

                    
                except Exception as e:
                    # Erro simulado → aplica refound
                    mongo_balance += int(vbet.bet_amount * 0.5)
                    tx_type = TransactionTypeDTO.REFOUND
                    win_value = None
                    refound_value = True
                    print(f"⚠️ Refound aplicado por erro: {str(e)}")

                saldo_final= mongo_balance

                transaction = TransactionDTO(
                    player_id=player_id,
                    balance=player_balance,
                    new_balance= saldo_final,
                    win=win_value,
                    bet=vbet.bet_amount,
                    refound= (saldo_final - player_balance if refound_value else None),
                    type=tx_type
                )
                await TransactionService.create_transaction(transaction)
                print("🧾 Transação salva:", transaction.model_dump())
                       
                await PlayerService.update_balance(player_id, saldo_final)

                await RedisRepository.set_session(player_id, session)
                # Envia resultado só para o jogador que apostou
                game_result = GameResultDTO(type = None, result = result, win = win,new_balance = saldo_final,message = "Você ganhou!" if win else "Você perdeu." )
                await ws_service.send_game_result(game_result)

                if saldo_final <= 0:
                    saldo_final = 0
                
                if saldo_final == 0:
                    game_result = GameResultDTO(type = "Fim", result = None, win = None,new_balance = saldo_final, message = "Você perdeu todo o saldo. Fim de jogo." )
                    await ws_service.send_game_end(game_result)
                    print("Fim de Jogo")

                    await broadcast_result({
                        "type": "slot_result",
                        "player_id": player_id,
                        "result": result,
                        "win": win,
                        "balance": saldo_final
                    })
                    
                    await asyncio.sleep(1)
                    running = False
                    await websocket.close()
    
    except WebSocketDisconnect:
        print(f"Jogador {player_id} desconectado ou conexão foi perdida.")
        existing_session = await RedisRepository.get_session(player_id)
        if existing_session:
            existing_session.is_logged = False
            print("Sessão existente:", existing_session.model_dump() if existing_session else "Nenhuma")
            await RedisRepository.set_session(player_id, existing_session)
            

        
