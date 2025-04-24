# File: api/v1/api.py
from fastapi import APIRouter
from api.v1.endpoints import quiz, recommendations
from api.v1.endpoints import history # <<<--- Impor router history BARU

api_router = APIRouter()

# Sertakan router dari endpoints kuis & rekomendasi
api_router.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])

# Sertakan router dari endpoint history BARU
api_router.include_router(history.router, prefix="/history", tags=["History"]) # <<<--- Tambahkan ini

# Tambahkan router lain jika ada