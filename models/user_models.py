# File: models/user_models.py (DIMODIFIKASI)

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import relationship, Mapped # Impor relationship, Mapped
from sqlalchemy import String, Boolean # Impor tipe data jika perlu
from typing import List, Optional
import uuid
import os
from dotenv import load_dotenv

# --- Impor Base dari file baru ---
from .base import Base
# --------------------------------

# Impor model QuizAttempt untuk relasi (gunakan try-except atau pastikan Base sudah dikenal)
# Karena Base diimpor dari file lain, impor ini seharusnya aman sekarang
try:
    # Menggunakan type hint string "QuizAttempt" di relationship lebih aman
    # Namun, impor ini mungkin tetap diperlukan jika ada logika lain
    from .history_models import QuizAttempt
except ImportError:
    # Fallback jika struktur berbeda, tapi sebaiknya gunakan type hint string saja
    # from models.history_models import QuizAttempt
    pass # Lebih baik andalkan type hint string jika memungkinkan


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://quiz_app_user:inipw@localhost:5432/quiz_db")

class User(SQLAlchemyBaseUserTableUUID, Base):
    """Model Database untuk User."""
    __tablename__ = "user"

    # Kolom dari FastAPI-Users sudah ada (id, email, hashed_password, dll.)

    # --- Relasi ke QuizAttempt ---
    quiz_attempts: Mapped[List["QuizAttempt"]] = relationship( # Gunakan string "QuizAttempt"
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin" # Direkomendasikan untuk async
    )
    # ---------------------------


# Setup Koneksi Database Async (Bisa dipindah ke file db.py terpisah jika mau)
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Fungsi Dependency untuk mendapatkan DB session
async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

# Fungsi Dependency untuk mendapatkan User Database
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

# --- Skema Pydantic User ---
from fastapi_users import schemas
from pydantic import ConfigDict

class UserRead(schemas.BaseUser[uuid.UUID]):
    model_config = ConfigDict(from_attributes=True)

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass