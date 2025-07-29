import redis
from app.dto.mongo.transaction_win import TransactionWIN
from app.dto.mongo.transaction_type_dto import TransactionTypeDTO
from app.dto.websockets.error_dto import ErrorDTO
from app.dto.websockets.game_result_dto import GameResultDTO
from app.dto.websockets.game_session_status import GameSessionStatus
from app.dto.websockets.player_dto import PlayerDTO
from app.dto.websockets.session_dto import SessionDTO
from app.game_logic import get_session, set_session
from app.repository.mongo.mongo_transaction_repository import MongoTransactionRepository
from app.service.mongo.player_service import PlayerService
from app.service.mongo.transaction_service import TransactionService
from app.service.websocket.websocket_service import WebSocketService

class HandleCashout:
   
    async def handle_cashout(player_id:str, websocket, session: SessionDTO, mongo_balance):
        ws_service = WebSocketService(websocket, redis)

        session = await get_session(player_id)
        if session.status != GameSessionStatus.PLAYING:
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
            new_balance= mongo_balance + session.bet_amount + session.accumulated_win,
            message="Você solicitou cashout."
            
        )
        session.status = GameSessionStatus.FINISHED
        await ws_service.send_game_end(game_result)
        print(f"Jogador {player_id} fez cashout com saldo de {mongo_balance}")
        cashout_win =session.bet_amount + session.accumulated_win
        
        transaction = TransactionWIN(
            player_id=player_id,
            balance=mongo_balance,
            new_balance=mongo_balance + cashout_win,
            win=cashout_win,
            type=TransactionTypeDTO.WIN,
            bet_id=session.bet_id   
        )
        win_id = await TransactionService.create_transaction(transaction)
        await MongoTransactionRepository.update_transaction_with_win_id(session.bet_id, win_id)
        player_update_balance = PlayerDTO(player_id=player_id, balance=mongo_balance + cashout_win)
        await PlayerService.update_balance(player=player_update_balance)
        await set_session(player_id, session)
        
       
    