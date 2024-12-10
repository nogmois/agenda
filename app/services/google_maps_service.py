from fastapi import HTTPException, Depends, Query
import requests
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from config.database import get_db
from app.repository.models import Appointment, ShowByDistanceRequest, ShowDistanceRequest
import os
from dotenv import load_dotenv
from datetime import datetime


# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")



async def get_shows_within_distance(
    request: ShowDistanceRequest,  # Dados do corpo da requisição
    db: Session = Depends(get_db)  # Para conectar ao banco de dados
):
    # Converter a data do show fornecida
    show_date = datetime.strptime(request.show_date, "%Y-%m-%d")

    print(f"Received city: {request.show_city}")

    # Definir o intervalo de 90 dias antes e depois da data do show
    start_date = show_date - timedelta(days=90)
    end_date = show_date + timedelta(days=90)

    # Buscar shows do mesmo artista dentro do intervalo de 90 dias
    appointments = db.query(Appointment).filter(
        Appointment.artist_id == request.artist_id,
        Appointment.approved_at != None,
        Appointment.show_date.between(start_date, end_date)
    ).all()

    if not appointments:
        raise HTTPException(status_code=200, detail="No shows found within the 90-day period")

    # Verificar a proximidade das cidades usando a API do Google Maps
    nearby_shows = []
    for appointment in appointments:
        destination = f"{appointment.show_city},{appointment.show_state}"
        origin = f"{request.show_city},{request.show_state}"

        # Faz a requisição à API do Google Maps para calcular a distância
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": origin,
            "destinations": destination,
            "key": GOOGLE_MAPS_API_KEY
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to connect to Google Maps API")

        data = response.json()

        # Verificar se a distância é menor que 90 km
        element = data["rows"][0]["elements"][0]
        if element["status"] == "OK":
            distance = element["distance"]["value"]  # Distância em metros
            if distance < 90000:  # 90 km
                nearby_shows.append({
                    "show_city": appointment.show_city,
                    "show_state": appointment.show_state,
                    "show_date": appointment.show_date,
                    "artist_id": appointment.artist_id,
                    "distance_km": distance / 1000  # Converte para km
                })

    if not nearby_shows:
        return {"detail": "Nenhum show próximo em um raio de 90 km e 90 dias"}

    return {
        "nearby_shows": nearby_shows
    }



async def get_shows_by_distance(
    request: ShowByDistanceRequest,  # Dados do corpo da requisição
    db: Session = Depends(get_db)
):
    # Converter as datas
    start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(request.end_date, "%Y-%m-%d")

    # Buscar shows dentro do intervalo de datas para o artista
    appointments = db.query(Appointment).filter(
        Appointment.artist_id == request.artist_id, 
        Appointment.approved_at != None,
        Appointment.show_date.between(start_date, end_date)
    ).all()

    if not appointments:
        raise HTTPException(status_code=200, detail="Nenhum show encontrado nas datas fornecidas")
    
    nearby_shows = []
    for appointment in appointments:
        destination = f"{appointment.show_city}, {appointment.show_state}"
        origin = f"{request.city}, {request.state}"

        # Requisição à API do Google Maps
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": origin,
            "destinations": destination,
            "key": GOOGLE_MAPS_API_KEY
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Falha ao conectar-se à API do Google Maps")
        
        data = response.json()

        # Acessar o primeiro elemento da resposta
        element = data["rows"][0]["elements"][0]
        if element["status"] == "OK":
            distance = element["distance"]["value"]  # Distância em metros
            if distance >= request.km_limit * 1000:  # km para metros
                nearby_shows.append({
                    "show_city": appointment.show_city,
                    "show_state": appointment.show_state,
                    "show_date": appointment.show_date,
                    "artist_id": appointment.artist_id,
                    "distance_km": distance / 1000  # Convertendo para km
                })

    if not nearby_shows:
        return {"detail": "Nenhum show encontrado dentro do limite de km"}
    
    return {
        "nearby_shows": nearby_shows
    }
