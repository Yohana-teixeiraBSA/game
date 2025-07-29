
from pydantic import BaseModel


class SelectIndexDTO(BaseModel):
    index: int