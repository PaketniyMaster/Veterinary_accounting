from fastapi import APIRouter, Depends
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
    return crud_doctor.get_doctors(db, skip=skip, limit=limit)