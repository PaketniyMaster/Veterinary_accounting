from pydantic import BaseModel
from typing import Optional
from datetime import date

# Базовая схема питомца
class PetBase(BaseModel):
    name: str
    species: str
    breed: Optional[str] = None
    birth_date: Optional[date] = None

# Схема для создания (требует ID клиента)
class PetCreate(PetBase):
    client_id: int

# Схема для ответа (добавляется ID самого питомца)
class PetResponse(PetBase):
    id: int
    client_id: int

    class Config:
        from_attributes = True