from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.crud import medical_record as crud_record
from backend.schemas import medical_record as schema_record

router = APIRouter(prefix="/records", tags=["Медицинские карты"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schema_record.MedicalRecordResponse)
def create_record(record: schema_record.MedicalRecordCreate, db: Session = Depends(get_db)):
    return crud_record.create_record(db=db, record=record)

@router.get("/", response_model=list[schema_record.MedicalRecordResponse])
def read_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_record.get_records(db, skip=skip, limit=limit)