# File: api/v1/endpoints/quiz.py (DIPERBAIKI - Menghapus komentar /* */ yang salah)

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import List, Optional
import uuid

# Impor model, skema, service
from models.quiz_models import QuestionOut, QuizSubmission, QuizResult, QuizStartResponse, CategoryInfo
from services import quiz_service
from utils.opentdb_api import OPENTDB_CATEGORIES

# Impor dependensi Auth & DB
from sqlalchemy.ext.asyncio import AsyncSession
# Pastikan path impor benar untuk get_async_session
try:
    from models.user_models import User, get_async_session
except ImportError:
    # Fallback jika get_async_session dipindah ke file lain (misal: db.session)
    # Sesuaikan path ini jika perlu
    from db.session import get_async_session
    from models.user_models import User

from auth.core import fastapi_users # Impor instance fastapi_users

# Dependency shortcut untuk user aktif
current_active_user = fastapi_users.current_user(active=True)

router = APIRouter()

# Endpoint GET Categories
@router.get("/categories", response_model=List[CategoryInfo], summary="Dapatkan Daftar Kategori Kuis")
async def get_available_categories(): # Hapus komentar salah dari sini
    """Mengembalikan daftar semua kategori yang tersedia beserta ID-nya."""
    category_list = [ CategoryInfo(id=cat_id, name=cat_name) for cat_id, cat_name in OPENTDB_CATEGORIES.items() ]
    if not category_list:
        raise HTTPException(status_code=404, detail="Daftar kategori tidak ditemukan.")
    return category_list

# Endpoint GET Start Quiz (Diproteksi)
@router.get("/start", response_model=QuizStartResponse, summary="Memulai Kuis Baru (Memerlukan Login)")
async def start_quiz(
    user: User = Depends(current_active_user),
    amount: int = Query(10, ge=1, le=50),
    category_ids: Optional[List[int]] = Query(None, alias="category_id"),
    difficulty: Optional[str] = Query(None)
): # Hapus komentar salah dari sini
    """Memulai kuis baru untuk user yang sedang login."""
    print(f"[User: {user.email}] Starting a new quiz.")
    quiz_session_id = str(uuid.uuid4())
    questions_for_user: List[QuestionOut] = await quiz_service.get_new_quiz(
        quiz_session_id=quiz_session_id, amount=amount, category_ids=category_ids, difficulty=difficulty
    )
    if not questions_for_user:
        raise HTTPException(status_code=503, detail="Gagal mengambil pertanyaan.")
    return QuizStartResponse(session_id=quiz_session_id, questions=questions_for_user)

# Endpoint GET Start Guest Quiz (Tidak diproteksi)
@router.get("/start-guest", response_model=QuizStartResponse, summary="Memulai Kuis Baru sebagai Tamu")
async def start_guest_quiz(
    amount: int = Query(10, ge=1, le=50),
    category_ids: Optional[List[int]] = Query(None, alias="category_id"),
    difficulty: Optional[str] = Query(None)
): # Hapus komentar salah dari sini
    """Memulai kuis baru untuk tamu (tidak memerlukan login)."""
    print("[Guest] Starting a new guest quiz.")
    quiz_session_id = str(uuid.uuid4())
    questions_for_guest: List[QuestionOut] = await quiz_service.get_new_quiz(
        quiz_session_id=quiz_session_id, amount=amount, category_ids=category_ids, difficulty=difficulty
    )
    if not questions_for_guest:
        raise HTTPException(status_code=503, detail="Gagal mengambil pertanyaan.")
    return QuizStartResponse(session_id=quiz_session_id, questions=questions_for_guest)

# Endpoint POST Submit Quiz (Diproteksi)
@router.post("/{quiz_session_id}/submit", response_model=QuizResult, summary="Submit Jawaban Kuis (Memerlukan Login & Menyimpan Hasil)")
async def submit_quiz(
    quiz_session_id: str,
    submission: QuizSubmission = Body(...),
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
): # Hapus komentar salah dari sini
    """Menerima jawaban, menilai, menyimpan hasil ke DB, dan mengembalikan skor."""
    print(f"[User: {user.email}] Submitting quiz session {quiz_session_id}")
    result = await quiz_service.submit_quiz_answers(
        quiz_session_id=quiz_session_id, user_answers=submission.answers, db=db, user=user
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Quiz session ID tidak valid atau sudah selesai.")
    return result

# Endpoint POST Calculate Guest Result (Tidak diproteksi)
@router.post("/{quiz_session_id}/calculate-guest-result",
             response_model=QuizResult,
             summary="Hitung Hasil Kuis Tamu (Tanpa Login & Tanpa Menyimpan)")
async def calculate_guest_result(
    quiz_session_id: str,
    submission: QuizSubmission = Body(...)
): # Hapus komentar salah dari sini
    """Menerima jawaban tamu, menilai berdasarkan data sesi sementara, dan mengembalikan hasil."""
    print(f"[Guest] Calculating result for session {quiz_session_id}")
    result = await quiz_service.calculate_guest_quiz_result(
        quiz_session_id=quiz_session_id,
        guest_answers=submission.answers
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Sesi kuis tamu tidak valid atau sudah selesai.")
    return result