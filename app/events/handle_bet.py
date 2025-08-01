from datetime import datetime
from app.dto.mongo.transaction_bet import TransactionBET
from app.dto.mongo.transaction_type_dto import TransactionTypeDTO
from app.dto.websockets.error_dto import ErrorDTO
from app.dto.websockets.game_session_enum import GameSessionEnum
from app.dto.websockets.handle_bet_request_dto import HandleBetRequestDTO
from app.dto.websockets.player_dto import PlayerDTO
from app.dto.websockets.session_dto import SessionDTO
from app.game_logic import get_session, set_session, start_grid_game
from app.service.mongo.player_service import PlayerService
from app.service.mongo.transaction_service import TransactionService
from app.service.websocket.websocket_service import WebSocketService
from app.test_error import setup_logger

logger = setup_logger("handle-bet")

class HandleBet:
    #criar dto para receber os dados da aposta
    async def handle_bet(request:HandleBetRequestDTO):
        transaction_service = TransactionService()
        player_service = PlayerService()
        '''
        logger.error("Mongo Balance", mongo_balance)
        ws_service = WebSocketService(websocket, redis)  

        if session and session.status != GameSessionStatus.PLAYING:
            await ws_service.send_error(ErrorDTO(error="Você já tem uma partida ativa."))
            return
        '''

        await get_session(request.player_id)
        print(request.mongo_balance)
        grid = await start_grid_game(
            PlayerDTO(player_id=request.player_id, casino=request.casino, device=request.device, currency=request.currency, type="Saldo", balance=request.mongo_balance),
            num_mines=request.vbet.num_mines
        )
        session = SessionDTO(
            casino=request.casino,
            player_id=request.player_id,
            device=request.device,
            currency=request.currency,
            regulation=request.regulation,
            is_logged=True,
            grid=grid,
            num_mines= request.vbet.num_mines,
            bet_amount= request.vbet.bet_amount,
            revealed=["x"] * 25,
            status= GameSessionEnum.PLAYING

        )
        if request.vbet.num_mines is None or not (1 <= request.vbet.num_mines < 21):
                await WebSocketService.send_error(ErrorDTO(error="Quantidade de minas inválidas. Escolha entre 1 e 20."))
        request.mongo_balance -= request.vbet.bet_amount

        transaction = TransactionBET(
            player_id=request.player_id,
            balance=request.player_balance,
            new_balance=request.mongo_balance,
            bet=request.vbet.bet_amount,
            type=TransactionTypeDTO.BET,
            timestamp=datetime.now(),
            casino=request.casino,
            currency=request.currency
        )
        
        bet_id =await transaction_service.create_transaction(transaction)
        session.bet_id = bet_id
        await set_session(session=session)
        print(f"Session handle bet: {session}")
        player_balance = PlayerDTO(player_id=request.player_id, balance=request.mongo_balance)
        await player_service.update_balance(player=player_balance)
        return request.mongo_balance
