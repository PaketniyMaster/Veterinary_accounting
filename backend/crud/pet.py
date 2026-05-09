from sqlalchemy.orm import Session
from backend.database import models
from backend.schemas import pet as pet_schemas

# Получить список всех питомцев
def get_pets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Pet).offset(skip).limit(limit).all()

# Добавить нового питомца
def create_pet(db: Session, pet: pet_schemas.PetCreate):
    # pet.model_dump() превращает данные в словарь {name: 'Бобик', species: 'Собака'...}
    db_pet = models.Pet(**pet.model_dump())
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet

def get_pets_by_client(db: Session, client_id: int):
    """Возвращает всех питомцев, привязанных к конкретному клиенту"""
    return db.query(models.Pet).filter(models.Pet.client_id == client_id).all()

def delete_pet(db: Session, pet_id: int):
    db_pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if db_pet:
        db.delete(db_pet)
        db.commit()
        return True
    return False

    