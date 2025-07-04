from pydantic import BaseModel

class ErrorDTO(BaseModel):
    error: str
