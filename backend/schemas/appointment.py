from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentBase(BaseModel):
    pet_id: int
    doctor_id: int
    date_time: datetime
    status: str = "Запланировано"
    
    # --- ДОБАВЛЕННЫЕ МЕДИЦИНСКИЕ ПОЛЯ ---
    anamnesis: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pet_id: int
    doctor_id: int

class AppointmentResponse(AppointmentBase):
    id: int
    pet_id: int
    doctor_id: int
    pet_name: str # Добавляем это поле

    class Config:
        from_attributes = True