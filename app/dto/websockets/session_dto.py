from pydantic import BaseModel

class SessionDTO(BaseModel):
    player_id: str 
    is_logged: bool = False
    