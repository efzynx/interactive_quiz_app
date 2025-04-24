# File: api/v1/endpoints/history.py (DIMODIFIKASI - Impor Diubah)

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
import uuid # Impor uuid

# --- Impor model/skema dari file baru ---
from models.history_models import QuizAttemptRead
# ------------------------------------
from models.user_models import User, get_async_session
from services import quiz_service
from auth.core import fastapi_users

# Dependency shortcut untuk user aktif
current_active_user = fastapi_users.current_user(active=True)

router = APIRouter()

@router.get("", # Path relatif terhadap prefix di api.py -> /history
            response_model=List[QuizAttemptRead], # Gunakan skema dari history_models
            summary="Dapatkan Riwayat Kuis Pengguna",
            description="Mengambil daftar riwayat percobaan kuis untuk pengguna yang sedang login.")
async def get_quiz_history(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Endpoint untuk mengambil riwayat kuis user."""
    print(f"Fetching quiz history for user {user.email} (ID: {user.id})")
    # Pastikan tipe user.id (UUID atau int) cocok dengan parameter di service
    history = await quiz_service.get_user_quiz_history(user_id=user.id, db=db)
    # Tidak perlu cek None lagi jika service selalu return list
    # if history is None:
    #     raise HTTPException(status_code=500, detail="Gagal mengambil riwayat kuis.")
    return history