from sqlalchemy.orm import Session
from backend.database import models
from backend.schemas import medical_record as record_schemas

def get_records(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MedicalRecord).offset(skip).limit(limit).all()

def create_record(db: Session, record: record_schemas.MedicalRecordCreate):
    db_record = models.MedicalRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record