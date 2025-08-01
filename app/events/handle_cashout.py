from datetime import datetime
from fastapi import WebSocket
from app.redis_client import redis
from app.dto.mongo.transaction_dto import TransactionDTO
from app.dto.mongo.transaction_win import TransactionWIN
from app.dto.mongo.transaction_type_dto import TransactionTypeDTO
from app.dto.websockets.error_dto import ErrorDTO
from app.dto.websockets.game_history_dto import GameHistoryDTO
from app.dto.websockets.game_result_dto import GameResultDTO
from app.dto.websockets.game_session_enum import GameSessionEnum
from app.dto.websockets.handle_cashout_request_dto import HandleCashoutResquestDTO
from app.dto.websockets.player_dto import PlayerDTO
from app.game_logic import get_session, set_session
from app.repository.mongo.mongo_transaction_repository import MongoTransactionRepository
from app.service.mongo.game_history_service import GameHistoryService
from app.service.mongo.player_service import PlayerService
from app.service.mongo.transaction_service import TransactionService
from app.service.websocket.websocket_service import WebSocketService

class HandleCashout:

    async def handle_cashout(request:HandleCashoutResquestDTO, websocket: WebSocket):
        ws_service = WebSocketService(websocket, redis)
        mongo_transaction_repository = MongoTransactionRepository()
        transaction_service = TransactionService()
        player_service = PlayerService()
        game_history_service = GameHistoryService()

        session = await get_session(request.player_id)
        if session.status != GameSessionEnum.PLAYING:
            await ws_service.send_error(ErrorDTO(error="Partida não está ativa. Faça uma nova aposta."))
            return
        
        if all(revealed == 'x' for revealed in session.revealed):
            print(f"session.revealed: {session.revealed}")
            await ws_service.send_error(ErrorDTO(error="Você precisa acertar pelo menos uma jogada antes de solicitar cashout."))
            return
        game_result = GameResultDTO(
            type = TransactionTypeDTO.WIN,
            result = f"Você ganhou {session.bet_amount + session.accumulated_win}.",
            win= 0,
            new_balance= request.mongo_balance + session.bet_amount + session.accumulated_win,
            message="Você solicitou cashout."
            
        )
        session.status = GameSessionEnum.FINISHED
        await ws_service.send_game_end(game_result)
        print(f"Jogador {request.player_id} fez cashout com saldo de {request.mongo_balance}")
        cashout_win =session.bet_amount + session.accumulated_win
        
        transaction = TransactionWIN(
            player_id=request.player_id,
            balance=request.mongo_balance,
            new_balance=request.mongo_balance + cashout_win,
            win=cashout_win,
            type=TransactionTypeDTO.WIN,
            bet_id=session.bet_id,
            timestamp=datetime.now(),
            casino=request.casino,
            currency=request.currency
        )
        win_id = await transaction_service.create_transaction(transaction)
        update_transaction = TransactionDTO(
            player_id=request.player_id,
            bet_id=session.bet_id,
            win_id=win_id,
            timestamp=datetime.now(),
            casino=request.casino,
            currency=request.currency
        )
        await mongo_transaction_repository.update_transaction_with_win_id(update_transaction)
        history_dto = GameHistoryDTO(
                player_id=request.player_id,
                bet_amount=session.bet_amount,
                balance=request.mongo_balance,
                new_balance=request.mongo_balance + cashout_win,
                win=cashout_win,
                num_mines=session.num_mines,
                revealed=session.revealed,
                timestamp=datetime.now(),
                casino=request.casino,
                currency=request.currency,
                win_id=win_id
            )
        result  = await game_history_service.create_game_history(history_dto)
        mongo_id = str(result.inserted_id)
        history_dto._id = mongo_id
        player_update_balance = PlayerDTO(player_id=request.player_id, balance=request.mongo_balance + cashout_win)
        await player_service.update_balance(player=player_update_balance)
        session.is_logged = False
        session.casino = request.casino
        session.device = request.device
        session.regulation = request.regulation
        await set_session(session)
        await websocket.close()
        return "closed"
        
       
    