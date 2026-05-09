from pydantic import BaseModel
from typing import Optional

# Базовая схема (общие поля)
class ClientBase(BaseModel):
    full_name: str
    phone: str
    email: Optional[str] = None

# Схема для создания (входящие данные)
class ClientCreate(ClientBase):
    pass # Пока ничего не добавляем, хватает базовых полей

# Схема для ответа (исходящие данные)
class ClientResponse(ClientBase):
    id: int # При возврате мы уже знаем ID из базы данных

    class Config:
        from_attributes = True # Позволяет Pydantic читать данные из моделей SQLAlchemy