from sqlalchemy.orm import Session
from backend.database import models
from backend.schemas import doctor as doctor_schemas

def get_doctors(db: Session, skip: int = 0, limit: int = 100, only_active: bool = True):
    """Возвращает список врачей. По умолчанию — только активных (не в архиве)"""
    query = db.query(models.Doctor)
    if only_active:
        query = query.filter(models.Doctor.is_active == True)
    return query.offset(skip).limit(limit).all()

def create_doctor(db: Session, doctor: doctor_schemas.DoctorCreate):
    db_doctor = models.Doctor(**doctor.model_dump())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor    

def delete_doctor(db: Session, doctor_id: int):
    """Мягкое удаление с защитой от 'потерянных' пациентов"""
    
    # 1. Проверяем, есть ли у врача незавершенные приемы
    active_appointments = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor_id,
        models.Appointment.status.in_(["Запланировано", "Ожидает", "На приеме"])
    ).first()

    if active_appointments:
        return "has_active" # Возвращаем специальный флаг ошибки

    # 2. Если активных приемов нет, спокойно архивируем
    db_doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if db_doctor:
        db_doctor.is_active = False 
        db.commit()
        return "success"
        
    return "not_found"