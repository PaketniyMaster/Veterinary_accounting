from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from backend.database.connection import SessionLocal
from backend.crud import client as crud_client
from backend.schemas import client as schema_client
from fastapi import HTTPException # Добавьте HTTPException в импорты из fastapi в самом начале файла!
# 1. ИМПОРТИРУЕМ НАШ НОВЫЙ РОУТЕР
from backend.routers import pets 

from backend.routers import pets
from backend.routers import doctors       
from backend.routers import appointments  
from backend.routers import medical_records 
app = FastAPI(title="Vet Clinic API", description="API для ветеринарной клиники")

app.include_router(pets.router)
app.include_router(doctors.router)        
app.include_router(appointments.router)   
app.include_router(medical_records.router) 


# Зависимость БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Эндпоинты клиентов (пока оставляем здесь) ---
@app.post("/clients/", response_model=schema_client.ClientResponse)
def create_client(client: schema_client.ClientCreate, db: Session = Depends(get_db)):
    return crud_client.create_client(db=db, client=client)

@app.get("/clients/", response_model=list[schema_client.ClientResponse])
def read_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_client.get_clients(db, skip=skip, limit=limit)

@app.delete("/clients/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    success = crud_client.delete_client(db=db, client_id=client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return {"message": "Клиент успешно удален"}