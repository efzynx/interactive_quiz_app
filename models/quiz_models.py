# File: models/quiz_models.py (DIMODIFIKASI - History Dihapus)

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
# Tidak perlu impor SQLAlchemy di sini lagi jika tidak ada model DB lain

# Skema Pydantic yang terkait dengan proses kuis itu sendiri
class CategoryInfo(BaseModel):
    """Skema untuk informasi kategori."""
    id: int = Field(..., description="ID Kategori dari OpenTDB")
    name: str = Field(..., description="Nama Kategori")

class QuestionOut(BaseModel):
    """Skema untuk pertanyaan yang dikirim ke frontend."""
    id: str
    category_name: str
    difficulty: str
    question: str
    options: List[str]

class AnswerIn(BaseModel):
    """Skema untuk jawaban yang diterima dari frontend."""
    question_id: str
    user_answer: str

class QuizSubmission(BaseModel):
    """Skema untuk payload submit kuis."""
    answers: List[AnswerIn]

class WeaknessAnalysis(BaseModel):
    """Skema untuk hasil analisis kelemahan."""
    category_name: str
    score_percentage: float
    correct_count: int
    total_questions: int

class QuizResult(BaseModel):
    """Skema untuk hasil kuis yang dikembalikan setelah submit."""
    total_questions: int
    correct_answers_count: int
    score_percentage: float
    analysis: List[WeaknessAnalysis]

class QuizStartResponse(BaseModel):
    """Skema untuk respons saat memulai kuis."""
    session_id: str
    questions: List[QuestionOut]

# Definisi QuizAttempt dan QuizAttemptRead sudah dipindah ke history_models.py