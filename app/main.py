from colorama import init
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.dto.mongo.transaction_dto import TransactionDTO
from app.dto.mongo.transaction_refund import TransactionREFUND
from app.dto.mongo.transaction_type_dto import TransactionTypeDTO
from app.dto.websockets.bet__dto import BetDTO
from app.dto.websockets.game_session_status import GameSessionStatus
from app.dto.websockets.select_index_dto import SelectIndexDTO
from app.events.handle_bet import HandleBet
from app.events.handle_cashout import HandleCashout
from app.events.handle_select_index import HandleSelectIndex
from app.repository.mongo.mongo_transaction_repository import MongoTransactionRepository
from app.test_error import setup_logger
from app.redis_client import redis
from app.game_logic import  get_session, mask_grid, set_session
from app.dto.websockets.error_dto import ErrorDTO
from app.dto.websockets.player_dto import PlayerDTO
from app.service.mongo.transaction_service import TransactionService
from app.service.websocket.websocket_service import WebSocketService
from app.service.mongo.player_service import PlayerService

app = FastAPI()

logger = setup_logger("Main")

# WebSocket endpoint para receber apostas e enviar resultados
# ws://localhost:8000/ws/slot/{player_id}
@app.websocket("/ws/slot/{player_id}")
async def slot_websocket(websocket: WebSocket, player_id: str):
    await websocket.accept()
    
    running = True
    existing_session = await get_session(player_id)

    if existing_session and existing_session.is_logged:
        await websocket.send_json(ErrorDTO(error="Já existe uma sessão ativa para esse jogador.").model_dump())
        await websocket.close()
        return
    
    try:
        while running:
            data = await websocket.receive_json()
            action = data.get("action")
            print(action)
            bet_amount = data.get("bet_amount")
            ws_service = WebSocketService(websocket, redis)
            mongo_transaction_repository = MongoTransactionRepository()

            if not action:
                await ws_service.send_error(ErrorDTO(error="Ação não especificada."))
                continue
            
            if action == "bet":
                    player = PlayerDTO(player_id=player_id, balance=1000) 
                    player = await PlayerService.get_or_create_player( player = player)
                    mongo_balance = player.balance
                    vbet = BetDTO(**data)

                    #logger.error("Mongo Balance", mongo_balance)
                    mongo_balance = await HandleBet.handle_bet(
                        player_id, player.balance, vbet, mongo_balance
                    )

                    # Após o handle_bet, recupere a sessão atualizada (com bet_id)
                    session = await get_session(player_id)
                    print(f"Session após aposta: {session}")

                    if existing_session:
                       masked_grid = mask_grid(session)
                       grid_2d = [masked_grid[i:i+5] for i in range(0, 25, 5)]
                    else:
                        # grid padrão caso não exista sessão
                        grid_2d = [["x"] * 5 for _ in range(5)]

                    # Envia dados iniciais
                    await ws_service.send_grid(grid_2d)
                    print(f"Jogador {player_id} fez uma aposta de {bet_amount}. Saldo atual: {mongo_balance}")
                    await ws_service.send_player(PlayerDTO(player_id=player_id, type="saldo", balance=mongo_balance))

            elif action == "select_index":
                    
                    index_dto = SelectIndexDTO(**data)
                    result =await HandleSelectIndex.handle_select_index(
                        player_id,
                        index_dto.index,
                        websocket
                    )
                    await get_session(player_id=player_id)
                    if result == "closed":
                        running = False
                        break

            elif action == "cashout":
                    await get_session(player_id=player_id)
                    result = await HandleCashout.handle_cashout(
                        player_id,
                        websocket,
                        session,
                        mongo_balance=mongo_balance
                    )
                    if result == "closed":
                        running = False
                        break
            else:
                await ws_service.send_error(ErrorDTO(error= f"Ação desconhecida: {action}"))

    except WebSocketDisconnect:
        print(f"Jogador {player_id} desconectado.")
        # traceback error

        session =await get_session(player_id=player_id)
        if session:
            if session.status == GameSessionStatus.PLAYING and all(revealed == 'x' for revealed in session.revealed):
                refund_amount = session.bet_amount
                print(f"Jogador {player_id} solicitou um reembolso de {refund_amount}.")
                player = PlayerDTO(player_id=player_id, balance=0)  
                player_service = (await PlayerService.get_or_create_player(player))
                mongo_balance = player_service.balance
                player_balance = mongo_balance
                transaction = TransactionREFUND(
                    player_id=player_id,
                    balance= player_balance,
                    new_balance=mongo_balance + refund_amount,
                    win=None,
                    refund= refund_amount,
                    type=TransactionTypeDTO.REFUND,
                    bet_id=session.bet_id    
                )
                refund_id = await TransactionService.create_transaction(transaction)
                update_transaction = TransactionDTO(
                    bet_id=session.bet_id,
                    refund_id=refund_id
                )
                await mongo_transaction_repository.update_transaction_with_refund_id(update_transaction)
                print("Transação de aposta salva:", transaction.model_dump())
                player_update_balance = PlayerDTO(player_id= player_id, balance=mongo_balance + refund_amount)
                await PlayerService.update_balance(player_update_balance)
                session.is_logged = False
                await set_session(session)

        