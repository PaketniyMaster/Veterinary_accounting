from fastapi import APIRouter, Depends, HTTPException # <--- Добавили HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.crud import doctor as crud_doctor
from backend.schemas import doctor as schema_doctor

router = APIRouter(prefix="/doctors", tags=["Врачи"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schema_doctor.DoctorResponse)
def create_doctor(doctor: schema_doctor.DoctorCreate, db: Session = Depends(get_db)):
    return crud_doctor.create_doctor(db=db, doctor=doctor)

@router.get("/", response_model=list[schema_doctor.DoctorResponse])
def read_doctors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Возвращаем только активных врачей для фронтенда
    return crud_doctor.get_doctors(db, skip=skip, limit=limit, only_active=True)

@router.delete("/{doctor_id}")
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Удаление (архивация) врача с проверкой"""
    result = crud_doctor.delete_doctor(db=db, doctor_id=doctor_id)
    
    if result == "has_active":
        # Код 400 (Bad Request) - логическая ошибка
        raise HTTPException(status_code=400, detail="Невозможно удалить: у врача есть активные записи на прием. Перенесите или отмените их.")
    elif result == "not_found":
        raise HTTPException(status_code=404, detail="Врач не найден")
        
    return {"message": "Врач успешно переведен в архив"}