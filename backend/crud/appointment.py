from sqlalchemy.orm import Session
from backend.database import models
from backend.schemas import appointment as appt_schemas
from datetime import date, datetime
def get_appointments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Appointment).offset(skip).limit(limit).all()

def create_appointment(db: Session, appt: appt_schemas.AppointmentCreate):
    # Создаем объект записи из пришедших данных
    db_appt = models.Appointment(**appt.model_dump())
    
    db.add(db_appt)
    db.commit()
    db.refresh(db_appt) # Обновляем объект, чтобы получить его ID из базы
    
    # --- НУЖНО ДОБАВИТЬ ЭТУ СТРОКУ ---
    # Наполняем поле pet_name перед отправкой ответа
    db_appt.pet_name = db_appt.pet.name if db_appt.pet else "Неизвестно"
    # --------------------------------
    
    return db_appt

def get_appointments_by_date(db: Session, target_date: date):
    """Возвращает все записи на прием в пределах одного выбранного дня с именем питомца"""
    # Создаем границы дня: от 00:00:00 до 23:59:59
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())
    
    # 1. Получаем список всех записей из базы данных
    appointments = db.query(models.Appointment).filter(
        models.Appointment.date_time >= start_of_day,
        models.Appointment.date_time <= end_of_day
    ).all()

    # 2. Проходим циклом по каждой записи и "приклеиваем" к ней имя питомца.
    # Благодаря связям (relationship), которые мы создали в моделях,
    # SQLAlchemy сама найдет нужного питомца по ID.
    for appt in appointments:
        # Обращаемся к связанному объекту pet и его полю name
        appt.pet_name = appt.pet.name if appt.pet else "Неизвестно"
    
    return appointments

def delete_appointment(db: Session, appointment_id: int):
    """Удаляет запись на прием по её ID"""
    db_appt = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if db_appt:
        db.delete(db_appt)
        db.commit()
        return True
    return False

def update_appointment(db: Session, appointment_id: int, appt: appt_schemas.AppointmentCreate):
    """Обновляет медицинские данные (анамнез, диагноз, лечение) и статус приема"""
    
    # Ищем нужную запись в базе по ID
    db_appt = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    
    if db_appt:
        # Перезаписываем старые данные новыми из формы
        db_appt.status = appt.status
        db_appt.anamnesis = appt.anamnesis
        db_appt.diagnosis = appt.diagnosis
        db_appt.treatment = appt.treatment
        
        # Сохраняем изменения в базу
        db.commit()
        db.refresh(db_appt)
        
    return db_appt

def get_appointment(db: Session, appointment_id: int):
    """Возвращает информацию о конкретном приеме по ID"""
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()