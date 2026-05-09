from sqlalchemy.orm import Session
from backend.database import models
from backend.schemas import client as client_schemas

# Функция для получения списка всех клиентов
def get_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Client).offset(skip).limit(limit).all()

# Функция для создания нового клиента
def create_client(db: Session, client: client_schemas.ClientCreate):
    # Превращаем Pydantic-схему в модель SQLAlchemy
    db_client = models.Client(
        full_name=client.full_name,
        phone=client.phone,
        email=client.email
    )
    db.add(db_client) # Добавляем в сессию
    db.commit()       # Сохраняем в БД
    db.refresh(db_client) # Обновляем объект, чтобы получить сгенерированный ID
    return db_client


def delete_client(db: Session, client_id: int):
    # Ищем клиента по ID
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if db_client:
        db.delete(db_client) # Удаляем
        db.commit()          # Сохраняем изменения
        return True
    return False