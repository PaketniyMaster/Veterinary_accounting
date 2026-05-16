from sqlalchemy.orm import Session
from backend.database import models
from backend.schemas import doctor as doctor_schemas

def get_doctors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Doctor).offset(skip).limit(limit).all()

def create_doctor(db: Session, doctor: doctor_schemas.DoctorCreate):
    db_doctor = models.Doctor(**doctor.model_dump())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor    

def delete_doctor(db: Session, doctor_id: int):
    # Ищем врача по id
    db_doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    
    if db_doctor:
        db.delete(db_doctor) # Удаляем объект
        db.commit()          # Сохраняем изменения в базе
        return True
    return False