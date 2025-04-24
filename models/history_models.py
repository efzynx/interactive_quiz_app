# File: models/history_models.py (DIMODIFIKASI)

import datetime
import uuid
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from pydantic import BaseModel, Field, ConfigDict

# --- Impor Base dari file baru ---
from .base import Base
# --------------------------------

# Impor User untuk foreign key dan relasi (gunakan try-except atau pastikan Base sudah dikenal)
try:
    # Menggunakan type hint string "User" di relationship lebih aman
    from .user_models import User
except ImportError:
    # Fallback jika perlu (tapi type hint string lebih baik)
    # from models.user_models import User
    pass


# --- Model SQLAlchemy untuk Riwayat ---
class QuizAttempt(Base):
    """Model Database untuk menyimpan riwayat percobaan kuis."""
    __tablename__ = "quiz_attempt"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Foreign key ke User (pastikan User sudah dikenal atau pakai string)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_answers: Mapped[int] = mapped_column(Integer, nullable=False)
    categories_played: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    # Relasi ke User
    user: Mapped["User"] = relationship(back_populates="quiz_attempts") # Gunakan string "User"

# --- Skema Pydantic untuk Membaca Riwayat ---
class QuizAttemptRead(BaseModel):
    """Skema Pydantic untuk menampilkan data riwayat ke API client."""
    id: uuid.UUID
    score: float
    total_questions: int
    correct_answers: int
    categories_played: Optional[str] = None
    timestamp: datetime.datetime

    model_config = ConfigDict(from_attributes=True)