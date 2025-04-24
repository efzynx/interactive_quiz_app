from fastapi import APIRouter, HTTPException, Depends
from typing import List

from models.recommendation_models import Recommendation
from models.quiz_models import QuizResult, WeaknessAnalysis # Impor model hasil
from services import recommendation_service
from api.v1.endpoints.quiz import submit_quiz # Impor endpoint submit untuk dependency

router = APIRouter()

# Contoh: Endpoint rekomendasi yang bergantung pada hasil submit terakhir
# Ini desain yang mungkin, cara lain adalah punya endpoint terpisah
# yang menerima analisis kelemahan secara langsung.

# Note: Menggunakan Depends pada endpoint lain seperti ini tidak ideal untuk state.
# Lebih baik: Submit mengembalikan hasil -> Frontend panggil endpoint rekomendasi TERPISAH
# dengan mengirimkan data analisis kelemahan dari hasil submit.

# Endpoint Terpisah (Disarankan):
@router.post("/", response_model=List[Recommendation], summary="Dapatkan Rekomendasi Bacaan")
async def get_recommendations_based_on_analysis(
    analysis_data: List[WeaknessAnalysis] # Terima data analisis dari frontend
):
    """
    Menerima data analisis kelemahan (dari hasil kuis) dan memberikan rekomendasi.
    """
    if not analysis_data:
        raise HTTPException(status_code=400, detail="Data analisis kelemahan diperlukan.")

    recommendations = await recommendation_service.generate_recommendations(analysis_data)
    return recommendations