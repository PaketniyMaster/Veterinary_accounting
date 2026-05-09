from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.crud import pet as crud_pet
from backend.schemas import pet as schema_pet

# Создаем объект роутера (все эндпоинты будут начинаться с /pets)
router = APIRouter(prefix="/pets", tags=["Питомцы"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schema_pet.PetResponse)
def create_pet(pet: schema_pet.PetCreate, db: Session = Depends(get_db)):
    return crud_pet.create_pet(db=db, pet=pet)

@router.get("/", response_model=list[schema_pet.PetResponse])
def read_pets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_pet.get_pets(db, skip=skip, limit=limit)

@router.get("/client/{client_id}", response_model=list[schema_pet.PetResponse])
def read_pets_by_client(client_id: int, db: Session = Depends(get_db)):
    """Эндпоинт для получения списка питомцев по ID владельца"""
    return crud_pet.get_pets_by_client(db, client_id=client_id)

from fastapi import HTTPException

@router.delete("/{pet_id}")
def delete_pet(pet_id: int, db: Session = Depends(get_db)):
    success = crud_pet.delete_pet(db=db, pet_id=pet_id)
    if not success:
        raise HTTPException(status_code=404, detail="Питомец не найден")
    return {"message": "Питомец удален"}