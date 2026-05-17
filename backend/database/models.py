from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from backend.database.connection import Base
class Client(Base):
    """Модель таблицы Клиентов (Владельцев)"""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(100))

    # Связь "Один ко многим"
    pets = relationship("Pet", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.full_name}')>"

class Pet(Base):
    """Модель таблицы Питомцев"""
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    species = Column(String(50), nullable=False)
    breed = Column(String(100))
    birth_date = Column(Date)

    # Обратная связь с владельцем
    owner = relationship("Client", back_populates="pets")
    # Связь с приемами
    appointments = relationship("Appointment", back_populates="pet", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Pet(id={self.id}, name='{self.name}', species='{self.species}')>"

class Doctor(Base):
    """Модель справочника Врачей"""
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    specialization = Column(String(100))
    
    # --- НОВАЯ КОЛОНКА ДЛЯ АРХИВАЦИИ ---
    is_active = Column(Boolean, default=True)

    # Связь с приемами
    appointments = relationship("Appointment", back_populates="doctor")

    def __repr__(self):
        return f"<Doctor(id={self.id}, name='{self.full_name}', active={self.is_active})>"

class Appointment(Base):
    """Модель Расписания / Записей на прием"""
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    date_time = Column(DateTime, nullable=False)
    status = Column(String(50), default="Запланирован")
    # --- НОВЫЕ МЕДИЦИНСКИЕ ПОЛЯ ---
    anamnesis = Column(Text, nullable=True) # Text позволяет хранить длинный текст
    diagnosis = Column(String, nullable=True)
    treatment = Column(Text, nullable=True)
    # Связи
    pet = relationship("Pet", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    # Связь "Один к одному" с медицинской картой (uselist=False)
    record = relationship("MedicalRecord", back_populates="appointment", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Appointment(id={self.id}, datetime='{self.date_time}')>"

class MedicalRecord(Base):
    """Модель Электронной медицинской карты"""
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    # unique=True гарантирует, что на один прием может быть только одна медкарта
    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="CASCADE"), unique=True, nullable=False)
    anamnesis = Column(Text)
    diagnosis = Column(Text)
    treatment = Column(Text)

    # Обратная связь
    appointment = relationship("Appointment", back_populates="record")

    def __repr__(self):
        return f"<MedicalRecord(id={self.id}, diagnosis='{self.diagnosis}')>"