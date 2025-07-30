import redis
from fastapi import WebSocket
from app.dto.mongo.transaction_dto import TransactionDTO
from app.dto.mongo.transaction_type_dto import TransactionTypeDTO
from app.dto.mongo.transaction_win import TransactionWIN
from app.dto.websockets.error_dto import ErrorDTO
from app.dto.websockets.game_result_dto import GameResultDTO
from app.dto.websockets.game_session_status import GameSessionStatus
from app.dto.websockets.player_dto import PlayerDTO
from app.game_logic import check_win, generate_current_grid_view, get_session, set_session
from app.repository.mongo.mongo_transaction_repository import MongoTransactionRepository
from app.service.mongo.player_service import PlayerService
from app.service.mongo.transaction_service import TransactionService
from app.service.websocket.websocket_service import WebSocketService

class HandleSelectIndex:

    @staticmethod
    async def handle_select_index(player_id: str, index: int, websocket: WebSocket):
        
        ws_service = WebSocketService(websocket, redis)
        mongo_transaction_repository = MongoTransactionRepository()
        player = PlayerDTO(player_id=player_id, balance=0)
        mongo_balance = (await PlayerService.get_or_create_player(player=player))

        session = await get_session(player_id=player_id)
        
        if session.status != GameSessionStatus.PLAYING:
            await ws_service.send_error(ErrorDTO(error="Partida não está ativa. Faça uma nova aposta."))
            return
        
        if session is None or session.grid is None:
            await ws_service.send_error(ErrorDTO(error="Sessão ou grid não encontrados."))
            return

        grid = session.grid
        session.is_logged = True 

        if index is None or not (0 <= index < 25):
            await ws_service.send_error(ErrorDTO(error="Índice inválido. Escolha entre 0 e 24."))
            return

        if session.revealed[index] != "x":
            await ws_service.send_error(ErrorDTO(error=f"A casa já foi revelada na posição {index}: {session.revealed[index]}"))
            return

        symbol = grid[index]
        session.revealed[index] = symbol
        
        win = check_win(symbol)
        win_value = 0
        
        player_dto = await PlayerService.get_or_create_player(player=player)
        mongo_balance = player_dto.balance
        player_balance = mongo_balance
        
        if symbol == "💣":
            tx_type = TransactionTypeDTO.WIN
            # valor total a perder: apenas ganhos acumulados, pois aposta já foi debitada
            loss_value = session.accumulated_win
            mongo_balance = mongo_balance - loss_value
            win_value = 0  # perdeu tudo
            message = "Você acertou uma mina! Perdeu todo o ganho acumulado e sua aposta."
            session.status = GameSessionStatus.FINISHED
            session.accumulated_win = 0  # reseta o acumulado
            transaction = TransactionWIN(
                player_id=player_id,
                balance=player_balance,
                new_balance=mongo_balance,
                win=win_value,
                bet_id=session.bet_id,
                type=tx_type
            )
            win_id = await TransactionService.create_transaction(transaction)
            update_transaction = TransactionDTO(
                bet_id=session.bet_id,
                win_id=win_id
            )
            await mongo_transaction_repository.update_transaction_with_win_id(update_transaction)
            player_update_balance = PlayerDTO(player_id=player_id, balance=mongo_balance)
            await PlayerService.update_balance(player=player_update_balance)
            session.is_logged = False
            await set_session(session) 

            await ws_service.send_game_end(GameResultDTO(
                type="Fim",
                result=symbol,
                win=0,
                new_balance=mongo_balance,
                message="Jogo finalizado."
            )) 
            updated_grid = await generate_current_grid_view(player_id)
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
            session.status = GameSessionStatus.PLAYING
        
            await set_session(session)
            print(f"Session  dentro do meu Select_index após atualização: {session}")
        await ws_service.send_game_result(GameResultDTO(
            type=tx_type,
            result=symbol,
            win=win,
            new_balance=mongo_balance,
            message=message
        ))
        updated_grid = await generate_current_grid_view(player_id)
        await ws_service.send_grid(updated_grid)   
        return session
            
