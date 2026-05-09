from pydantic import BaseModel
from typing import Optional

class MedicalRecordBase(BaseModel):
    anamnesis: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None

class MedicalRecordCreate(MedicalRecordBase):
    appointment_id: int

class MedicalRecordResponse(MedicalRecordBase):
    id: int
    appointment_id: int

    class Config:
        from_attributes = True