from pydantic import BaseModel
from typing import Optional

class DoctorBase(BaseModel):
    full_name: str
    specialization: Optional[str] = None

class DoctorCreate(DoctorBase):
    pass

class DoctorResponse(DoctorBase):
    id: int
    is_active: bool # <--- Добавили поле статуса

    class Config:
        from_attributes = True