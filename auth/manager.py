# File: auth/manager.py
import uuid
import os
from typing import Optional

from fastapi import Depends, Request, Response # Import Response
from fastapi_users import BaseUserManager, UUIDIDMixin, exceptions, models, schemas # <<< --- TAMBAHKAN 'schemas' DI SINI ---
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.exceptions import UserAlreadyExists # Import exception

from models.user_models import User, get_user_db # Impor model dan dependency DB
from dotenv import load_dotenv # Untuk membaca .env

load_dotenv() # Muat variabel dari .env

SECRET = os.getenv("SECRET_KEY", "fallback_secret_key_harap_diganti") # Ambil dari .env
if SECRET == "fallback_secret_key_harap_diganti":
    print("PERINGATAN: SECRET_KEY tidak diatur di .env, gunakan fallback yang tidak aman!")

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]): # Sesuaikan UUIDIDMixin/IntegerIDMixin
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} ({user.email}) has registered.")
        # TODO: Kirim email selamat datang (opsional)

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")
        # TODO: Kirim email reset password ke user.email dengan token

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
        # TODO: Kirim email verifikasi ke user.email dengan token

    # Override create untuk logging/penanganan error lebih baik (opsional)
    async def create(
        self,
        user_create: schemas.UC, # type: ignore - FastAPI Users internal type
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP: # type: ignore - FastAPI Users internal type
        try:
            # Cek apakah email sudah ada (FastAPI-Users juga melakukannya, tapi ini untuk log)
            existing_user = await self.user_db.get_by_email(user_create.email)
            if existing_user:
                print(f"Attempt to register with existing email: {user_create.email}")
                raise UserAlreadyExists()

            created_user = await super().create(user_create, safe, request)
            print(f"User successfully created with ID: {created_user.id}")
            return created_user
        except UserAlreadyExists:
            # Tangkap error spesifik jika perlu penanganan khusus
            raise UserAlreadyExists() # Re-raise agar router default menanganinya
        except Exception as e:
            # Log error tak terduga
            print(f"Unexpected error during user creation: {e}")
            # Anda bisa melempar HTTPException di sini jika mau
            raise

# Dependency untuk mendapatkan User Manager
async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)