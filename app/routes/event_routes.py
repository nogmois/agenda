from fastapi import APIRouter
from app.services.google_maps_service import get_shows_within_distance, get_shows_by_distance

router = APIRouter(tags=['Events'], prefix='/shows')

# Definindo a rota para verificar a distância e retornar shows
router.add_api_route("/check-distance/", get_shows_within_distance, methods=["POST"]),
router.add_api_route("/check-city-by-km/", get_shows_by_distance, methods=["POST"])

