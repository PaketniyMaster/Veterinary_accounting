from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.crud import appointment as crud_appt
from backend.schemas import appointment as schema_appt
from datetime import date # Добавьте импорт
from fastapi import HTTPException

router = APIRouter(prefix="/appointments", tags=["Записи на прием"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schema_appt.AppointmentResponse)
def create_appointment(appt: schema_appt.AppointmentCreate, db: Session = Depends(get_db)):
    return crud_appt.create_appointment(db=db, appt=appt)

@router.get("/", response_model=list[schema_appt.AppointmentResponse])
def read_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_appt.get_appointments(db, skip=skip, limit=limit)

@router.get("/date/{target_date}", response_model=list[schema_appt.AppointmentResponse])
def read_appointments_by_date(target_date: date, db: Session = Depends(get_db)):
    """Эндпоинт для получения расписания на конкретную дату (формат YYYY-MM-DD)"""
    return crud_appt.get_appointments_by_date(db, target_date=target_date)

@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Эндпоинт для отмены (удаления) записи"""
    success = crud_appt.delete_appointment(db=db, appointment_id=appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"message": "Запись успешно отменена"}

@router.get("/{appointment_id}", response_model=schema_appt.AppointmentResponse)
def read_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Эндпоинт для получения конкретной карточки приема"""
    db_appt = crud_appt.get_appointment(db, appointment_id=appointment_id)
    if not db_appt:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    
    # Добавляем имя питомца перед отправкой ответа
    db_appt.pet_name = db_appt.pet.name if db_appt.pet else "Неизвестно"
    return db_appt

# Эндпоинт PUT (Обновление) вы, возможно, уже добавили ранее. Если нет, он выглядит так:
@router.put("/{appointment_id}", response_model=schema_appt.AppointmentResponse)
def update_appointment(appointment_id: int, appt_data: schema_appt.AppointmentCreate, db: Session = Depends(get_db)):
    updated_appt = crud_appt.update_appointment(db=db, appointment_id=appointment_id, appt=appt_data)
    if not updated_appt:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    updated_appt.pet_name = updated_appt.pet.name if updated_appt.pet else "Неизвестно"
    return updated_appt