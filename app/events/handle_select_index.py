import redis
from datetime import datetime
from fastapi import WebSocket
from app.dto.mongo.transaction_dto import TransactionDTO
from app.dto.mongo.transaction_type_dto import TransactionTypeDTO
from app.dto.mongo.transaction_win import TransactionWIN
from app.dto.websockets.error_dto import ErrorDTO
from app.dto.websockets.game_history_dto import GameHistoryDTO
from app.dto.websockets.game_result_dto import GameResultDTO
from app.dto.websockets.game_session_enum import GameSessionEnum
from app.dto.websockets.handle_select_index_dto import HandleSelectIndexDTO
from app.dto.websockets.player_dto import PlayerDTO
from app.game_logic import check_win, generate_current_grid_view, get_session, set_session
from app.repository.mongo.mongo_transaction_repository import MongoTransactionRepository
from app.service.mongo.game_history_service import GameHistoryService
from app.service.mongo.player_service import PlayerService
from app.service.mongo.transaction_service import TransactionService
from app.service.websocket.websocket_service import WebSocketService

class HandleSelectIndex:

    async def handle_select_index(request: HandleSelectIndexDTO, websocket: WebSocket):

        ws_service = WebSocketService(websocket, redis)
        mongo_transaction_repository = MongoTransactionRepository()
        game_history_service = GameHistoryService()
        player_service = PlayerService()
        transaction_service = TransactionService()

        player = PlayerDTO(player_id=request.player_id, balance=0)
        mongo_balance = (await player_service.get_or_create_player(player=player))

        session = await get_session(request.player_id)
        print(f"Session dentro do meu Select_index: {session}")
        if session.status != GameSessionEnum.PLAYING:
            await ws_service.send_error(ErrorDTO(error="Partida não está ativa. Faça uma nova aposta."))
            return
        
        if session is None or session.grid is None:
            await ws_service.send_error(ErrorDTO(error="Sessão ou grid não encontrados."))
            return

        grid = session.grid
        session.is_logged = True 

        if request.index is None or not (0 <= request.index < 25):
            await ws_service.send_error(ErrorDTO(error="Índice inválido. Escolha entre 0 e 24."))
            return

        if session.revealed[request.index] != "x":
            await ws_service.send_error(ErrorDTO(error=f"A casa já foi revelada na posição {request.index}: {session.revealed[request.index]}"))
            return

        symbol = grid[request.index]
        session.revealed[request.index] = symbol

        win = check_win(symbol)
        win_value = 0

        player_dto = await player_service.get_or_create_player(player=player)
        mongo_balance = player_dto.balance
        player_balance = mongo_balance
        
        if symbol == "💣":
            tx_type = TransactionTypeDTO.WIN
            # valor total a perder: apenas ganhos acumulados, pois aposta já foi debitada
            loss_value = session.accumulated_win
            mongo_balance = mongo_balance - loss_value
            win_value = 0  # perdeu tudo
            message = "Você acertou uma mina! Perdeu todo o ganho acumulado e sua aposta."
            session.status = GameSessionEnum.FINISHED
            session.accumulated_win = 0  # reseta o acumulado
            transaction = TransactionWIN(
                player_id=request.player_id,
                balance=player_balance,
                new_balance=mongo_balance,
                win=win_value,
                bet_id=session.bet_id,
                type=tx_type,
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
                balance=player_balance,
                new_balance=mongo_balance,
                win=win_value,
                num_mines=session.num_mines,
                revealed=session.revealed,
                timestamp=datetime.now(),
                win_id=win_id,
                casino=request.casino,
                currency=request.currency
            )
            result  = await game_history_service.create_game_history(history_dto)
            mongo_id = str(result.inserted_id)
            history_dto._id = mongo_id
            

            player_update_balance = PlayerDTO(player_id=request.player_id, balance=mongo_balance)
            await player_service.update_balance(player=player_update_balance)

            session.casino=request.casino
            session.player_id=request.player_id
            session.device=request.device
            session.currency=request.currency
            session.regulation=request.regulation
            session.is_logged = False
            await set_session(session)

            await ws_service.send_game_end(GameResultDTO(
                type="Fim",
                result=symbol,
                win=0,
                new_balance=mongo_balance,
                message="Jogo finalizado."
            )) 
            updated_grid = await generate_current_grid_view(request.player_id)
            await ws_service.send_grid(updated_grid) 
            await websocket.close()  
            return "closed" 
        else:
            tx_type = TransactionTypeDTO.WIN
            win_this_round = int(session.bet_amount * 0.1)
            session.accumulated_win += win_this_round  # acumula o ganho
            mongo_balance += win_this_round  # adiciona ao saldo
            win_value = session.accumulated_win  # mostra o total ganho até aqui
            message = f"Você ganhou! Total acumulado: {win_value}"
            session.status = GameSessionEnum.PLAYING
        
            await set_session(session)
            print(f"Session  dentro do meu Select_index após atualização: {session}")
        await ws_service.send_game_result(GameResultDTO(
            type=tx_type,
            result=symbol,
            win=win,
            new_balance=mongo_balance,
            message=message
        ))
        updated_grid = await generate_current_grid_view(request.player_id)
        await ws_service.send_grid(updated_grid)   
        return session
            
