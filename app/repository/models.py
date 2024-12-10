from sqlalchemy import Column, Integer, String, DateTime
from config.database import Base
from pydantic import BaseModel

class Appointment(Base):
    __tablename__ = 'appointment'

    id = Column(Integer, primary_key=True, index=True)
    show_city = Column(String(100))
    show_state = Column(String(100))
    show_date = Column(DateTime)
    artist_id = Column(Integer)
    contractors_name = Column(String(255))  # Adicione o campo contractors_name aqui
    approved_at = Column(DateTime, nullable=True)


# Criar um modelo Pydantic para o corpo da requisição
class ShowDistanceRequest(BaseModel):
    show_city: str
    show_state: str
    artist_id: int
    show_date: str

# Criar um modelo Pydantic para o corpo da requisição
class ShowByDistanceRequest(BaseModel):
    start_date: str
    end_date: str
    city: str
    state: str
    km_limit: int
    artist_id: int