# File: services/quiz_service.py (LENGKAP & DIPERBAIKI INDENTASINYA)

from typing import List, Dict, Tuple, Optional
import uuid

# Impor komponen DB dan Model
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc # Tambah desc untuk sorting

# Impor model User & History
# Pastikan path ini benar sesuai struktur folder Anda
try:
    from models.user_models import User
    from models.history_models import QuizAttempt
except ImportError:
    print("WARNING: Gagal impor User/QuizAttempt dari models. Periksa path.")
    # Definisikan tipe dummy jika perlu agar tidak error saat load, tapi ini tidak ideal
    User = type("User", (), {})
    QuizAttempt = type("QuizAttempt", (), {})


# Impor model/skema KUIS
from models.quiz_models import QuizResult, AnswerIn, QuestionOut, WeaknessAnalysis
# Impor utilitas lain
from utils.opentdb_api import fetch_questions, OPENTDB_CATEGORIES

# Penyimpanan sementara (cache sederhana) untuk jawaban & detail soal per sesi
temp_correct_answers_storage: Dict[str, Dict[str, str]] = {}
temp_quiz_questions_storage: Dict[str, Dict[str, Dict]] = {}

def clear_quiz_session(quiz_session_id: str):
    """Membersihkan data sesi kuis dari penyimpanan sementara."""
    popped_answers = temp_correct_answers_storage.pop(quiz_session_id, None)
    popped_details = temp_quiz_questions_storage.pop(quiz_session_id, None)
    if popped_answers or popped_details:
        print(f"Cleared temp data for session {quiz_session_id}")

# Fungsi get_new_quiz dengan indentasi diperbaiki
async def get_new_quiz(
    quiz_session_id: str,
    amount: int = 10,
    category_ids: Optional[List[int]] = None,
    difficulty: Optional[str] = None
) -> List[QuestionOut]:
    """Membuat kuis baru, menyimpan jawaban benar, mengembalikan soal."""
    print(f"Service: get_new_quiz called for session {quiz_session_id} with category_ids: {category_ids}")
    fetched_questions: List[Dict] = []
    target_category_id: Optional[int] = None

    # Tentukan cara memanggil fetch_questions berdasarkan filter
    if not category_ids:
        # 1. Tidak ada filter
        print(f"Fetching {amount} questions from all categories.")
        fetched_questions = fetch_questions(amount=amount, difficulty=difficulty)
    elif len(category_ids) == 1:
        # 2. Filter 1 kategori
        target_category_id = category_ids[0]
        print(f"Fetching {amount} questions from single category ID: {target_category_id}")
        fetched_questions = fetch_questions(amount=amount, category_id=target_category_id, difficulty=difficulty)
    else:
        # 3. Filter >1 kategori
        fetch_multiplier = 5
        amount_to_fetch = max(amount * fetch_multiplier, 50)
        print(f"Fetching {amount_to_fetch} questions from all categories to filter for IDs {category_ids}")
        all_fetched = fetch_questions(amount=amount_to_fetch, difficulty=difficulty)

        # --- BAGIAN FILTERING DENGAN INDENTASI BENAR ---
        if all_fetched:
            # Baris-baris ini di-indent 4 spasi dari 'if all_fetched:'
            selected_category_names = {
                OPENTDB_CATEGORIES.get(cid) for cid in category_ids if cid in OPENTDB_CATEGORIES
            }
            selected_category_names.discard(None) # Hapus None jika ID tidak valid

            print(f"Filtering based on selected category names: {selected_category_names}")

            # Filter berdasarkan 'category_name'
            filtered_questions = [
                q for q in all_fetched
                if q.get('category_name') in selected_category_names # Bandingkan NAMA
            ]
            # Ambil sejumlah 'amount' atau sebanyak yang tersedia setelah filter
            fetched_questions = filtered_questions[:amount]
            print(f"Filtered down to {len(fetched_questions)} questions for categories: {selected_category_names}")
        else:
            # Baris ini sejajar dengan 'if all_fetched:'
            print("Failed to fetch questions for filtering.")
            fetched_questions = [] # Ini di-indent di bawah 'else:'
        # --- AKHIR BAGIAN FILTERING ---

    # Pastikan baris ini indentasinya kembali sejajar dengan if/elif/else utama
    if not fetched_questions:
        print(f"No questions fetched or filtered for session {quiz_session_id}")
        return [] # Kembalikan list kosong jika tidak ada soal

    # Pemrosesan dan penyimpanan sementara (Sama seperti versi terakhir)
    quiz_questions_for_user: List[QuestionOut] = []
    correct_answers_map: Dict[str, str] = {}
    questions_details_map: Dict[str, Dict] = {}
    used_ids_in_session = set()
    final_processed_questions = []
    for i, q in enumerate(fetched_questions):
        base_id = q.get('id', f"q_fallback_{i}")
        unique_id = f"{base_id}_{quiz_session_id[:4]}"
        collision_count = 0
        while unique_id in used_ids_in_session:
            collision_count += 1
            unique_id = f"{base_id}_{quiz_session_id[:4]}_{collision_count}"
        used_ids_in_session.add(unique_id)
        q['id'] = unique_id
        final_processed_questions.append(q)

    for q in final_processed_questions:
        question_id = q['id']
        quiz_questions_for_user.append(
            QuestionOut(
                id=question_id,
                category_name=q['category_name'],
                difficulty=q['difficulty'],
                question=q['question'],
                options=q['options']
            )
        )
        correct_answers_map[question_id] = q['correct_answer']
        questions_details_map[question_id] = q

    temp_correct_answers_storage[quiz_session_id] = correct_answers_map
    temp_quiz_questions_storage[quiz_session_id] = questions_details_map
    print(f"Stored {len(correct_answers_map)} correct answers for session {quiz_session_id}")
    return quiz_questions_for_user


# Fungsi submit_quiz_answers (UNTUK USER LOGIN - Tidak Berubah)
async def submit_quiz_answers(
    quiz_session_id: str,
    user_answers: List[AnswerIn],
    db: AsyncSession,
    user: User
) -> Optional[QuizResult]:
    """Menilai jawaban kuis user login, menganalisis, DAN MENYIMPAN hasilnya ke database."""
    correct_answers_map = temp_correct_answers_storage.get(quiz_session_id)
    questions_details_map = temp_quiz_questions_storage.get(quiz_session_id)

    if not correct_answers_map or not questions_details_map:
        print(f"Error: Quiz session {quiz_session_id} data not found.")
        clear_quiz_session(quiz_session_id)
        return None

    total_questions_in_session = len(correct_answers_map)
    if total_questions_in_session == 0:
         print(f"Warning: No questions found for session {quiz_session_id}.")
         clear_quiz_session(quiz_session_id)
         return QuizResult(total_questions=0, correct_answers_count=0, score_percentage=0.0, analysis=[])

    correct_count = 0
    results_by_category: Dict[str, Dict] = {}
    session_categories = set()

    for question_id, question_detail in questions_details_map.items():
        category_name = question_detail.get('category_name', 'Unknown')
        session_categories.add(category_name)
        if category_name not in results_by_category:
            results_by_category[category_name] = {"correct": 0, "total": 0}
        results_by_category[category_name]["total"] += 1
        user_ans_obj = next((ans for ans in user_answers if ans.question_id == question_id), None)
        if user_ans_obj:
            correct_ans = correct_answers_map.get(question_id)
            if correct_ans is not None and user_ans_obj.user_answer == correct_ans:
                correct_count += 1
                results_by_category[category_name]["correct"] += 1

    overall_score_percentage = round((correct_count / total_questions_in_session) * 100, 2) if total_questions_in_session > 0 else 0.0
    analysis_list: List[WeaknessAnalysis] = []
    for category_name, counts in results_by_category.items():
        cat_total = counts["total"]; cat_correct = counts["correct"]
        cat_score_percentage = round((cat_correct / cat_total) * 100, 2) if cat_total > 0 else 0.0
        analysis_list.append( WeaknessAnalysis( category_name=category_name, score_percentage=cat_score_percentage, correct_count=cat_correct, total_questions=cat_total ) )

    quiz_result_obj = QuizResult(
        total_questions=total_questions_in_session,
        correct_answers_count=correct_count,
        score_percentage=overall_score_percentage,
        analysis=analysis_list
    )

    # Simpan hasil ke Database
    try:
        categories_played_str = ", ".join(sorted(list(session_categories))) if session_categories else None
        # Pastikan QuizAttempt diimpor dari models.history_models
        new_attempt = QuizAttempt(
            user_id=user.id,
            score=overall_score_percentage,
            total_questions=total_questions_in_session,
            correct_answers=correct_count,
            categories_played=categories_played_str
        )
        db.add(new_attempt)
        await db.commit()
        print(f"Quiz attempt saved for user {user.id}")
    except Exception as e:
        await db.rollback()
        print(f"ERROR saving quiz attempt for user {user.id}: {e}")
        # Pertimbangkan logging error yang lebih baik di production

    clear_quiz_session(quiz_session_id)
    return quiz_result_obj


# Fungsi calculate_guest_quiz_result (UNTUK TAMU - Tidak Berubah)
async def calculate_guest_quiz_result(
    quiz_session_id: str,
    guest_answers: List[AnswerIn]
) -> Optional[QuizResult]:
    """Menilai jawaban kuis tamu TANPA menyimpan ke database."""
    print(f"Calculating result for GUEST session {quiz_session_id}")
    correct_answers_map = temp_correct_answers_storage.get(quiz_session_id)
    questions_details_map = temp_quiz_questions_storage.get(quiz_session_id)

    if not correct_answers_map or not questions_details_map:
        print(f"Error: GUEST Quiz session {quiz_session_id} data not found or expired.")
        clear_quiz_session(quiz_session_id); return None

    total_questions_in_session = len(correct_answers_map)
    if total_questions_in_session == 0:
         print(f"Warning: No questions found for GUEST session {quiz_session_id}.")
         clear_quiz_session(quiz_session_id); return QuizResult(total_questions=0, correct_answers_count=0, score_percentage=0.0, analysis=[])

    # Logika perhitungan skor (sama seperti di submit_quiz_answers)
    correct_count = 0
    results_by_category: Dict[str, Dict] = {}
    for question_id, question_detail in questions_details_map.items():
        category_name = question_detail.get('category_name', 'Unknown')
        if category_name not in results_by_category: results_by_category[category_name] = {"correct": 0, "total": 0}
        results_by_category[category_name]["total"] += 1
        user_ans_obj = next((ans for ans in guest_answers if ans.question_id == question_id), None)
        if user_ans_obj:
            correct_ans = correct_answers_map.get(question_id)
            if correct_ans is not None and user_ans_obj.user_answer == correct_ans:
                correct_count += 1
                results_by_category[category_name]["correct"] += 1

    overall_score_percentage = round((correct_count / total_questions_in_session) * 100, 2) if total_questions_in_session > 0 else 0.0
    analysis_list: List[WeaknessAnalysis] = []
    for category_name, counts in results_by_category.items():
        cat_total = counts["total"]; cat_correct = counts["correct"]
        cat_score_percentage = round((cat_correct / cat_total) * 100, 2) if cat_total > 0 else 0.0
        analysis_list.append( WeaknessAnalysis( category_name=category_name, score_percentage=cat_score_percentage, correct_count=cat_correct, total_questions=cat_total ) )

    quiz_result_obj = QuizResult(
        total_questions=total_questions_in_session,
        correct_answers_count=correct_count,
        score_percentage=overall_score_percentage,
        analysis=analysis_list
    )

    clear_quiz_session(quiz_session_id) # Hapus data sesi tamu
    print(f"Guest quiz result calculated for session {quiz_session_id}. Temp data cleared.")
    return quiz_result_obj


# Fungsi get_user_quiz_history (Tidak Berubah)
async def get_user_quiz_history(user_id: uuid.UUID | int, db: AsyncSession) -> List[QuizAttempt]:
    """Mengambil riwayat percobaan kuis untuk user tertentu dari database."""
    try:
        # Urutkan berdasarkan timestamp terbaru di atas
        stmt = select(QuizAttempt).where(QuizAttempt.user_id == user_id).order_by(desc(QuizAttempt.timestamp))
        result = await db.execute(stmt)
        attempts = result.scalars().all()
        return list(attempts)
    except Exception as e:
        print(f"Error fetching quiz history for user {user_id}: {e}")
        return [] # Kembalikan list kosong jika error