from turtle import update
from fastapi import WebSocket
from app.dto.mongo.transaction_bet import TransactionBET
from app.dto.mongo.transaction_type_dto import TransactionTypeDTO
from app.dto.websockets.bet__dto import BetDTO
from app.dto.websockets.error_dto import ErrorDTO
from app.dto.websockets.game_session_status import GameSessionStatus
from app.dto.websockets.player_dto import PlayerDTO
from app.dto.websockets.session_dto import SessionDTO
from app.game_logic import get_session, set_session, start_grid_game
from app.service.mongo.player_service import PlayerService
from app.service.mongo.transaction_service import TransactionService
from app.service.websocket.websocket_service import WebSocketService
from app.test_error import setup_logger

logger = setup_logger("handle-bet")

class HandleBet:
    async def handle_bet(player_id, player_balance, vbet: BetDTO, mongo_balance, websocket: WebSocket):
        
        '''
        logger.error("Mongo Balance", mongo_balance)
        ws_service = WebSocketService(websocket, redis)  

        if session and session.status != GameSessionStatus.PLAYING:
            await ws_service.send_error(ErrorDTO(error="Você já tem uma partida ativa."))
            return
        '''
        session = SessionDTO(player_id=player_id)
        await get_session(session=session)
        grid = await start_grid_game(
            PlayerDTO(player_id=player_id, type="Saldo", balance=mongo_balance),
            num_mines=vbet.num_mines
        )
        session = SessionDTO(
            player_id=player_id,
            is_logged=True,
            grid=grid,
            num_mines= vbet.num_mines,
            bet_amount= vbet.bet_amount,
            revealed=["x"] * 25,
            status= GameSessionStatus.PLAYING
        )
        await set_session(session=session)

        if vbet.num_mines is None or not (1 <= vbet.num_mines < 21):
                await WebSocketService.send_error(ErrorDTO(error="Quantidade de minas inválidas. Escolha entre 1 e 20."))
        mongo_balance -= vbet.bet_amount
        
        transaction = TransactionBET(
            player_id=player_id,
            balance=player_balance,
            new_balance=mongo_balance,
            bet=vbet.bet_amount,
            type=TransactionTypeDTO.BET
        )
        
        bet_id =await TransactionService.create_transaction(transaction)
        session.bet_id = bet_id
        await set_session(session=session)
        player_balance = PlayerDTO(player_id=player_id, balance=mongo_balance)
        await PlayerService.update_balance(player=player_balance)
        return mongo_balance
        