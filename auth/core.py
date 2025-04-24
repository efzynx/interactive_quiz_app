# File: auth/core.py
import uuid
from fastapi_users import FastAPIUsers
from auth.manager import get_user_manager
# Impor backend yang Anda pilih di strategy.py
from auth.strategy import auth_backend_jwt # atau auth_backend_cookie, atau keduanya dalam list
from models.user_models import User # Impor model User

# Instance utama FastAPIUsers
# Pastikan tipe ID (uuid.UUID atau int) cocok dengan model User Anda
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend_jwt], # Masukkan backend aktif Anda di sini dalam bentuk list
)

# Dependency untuk mendapatkan user yang sedang aktif (sudah login dan terverifikasi jika perlu)
# Anda bisa membuat variasi lain (misal: current_user tanpa cek active/verified)
current_active_user = fastapi_users.current_user(active=True)
current_optional_user = fastapi_users.current_user(active=True, optional=True) # User bisa None
current_superuser = fastapi_users.current_user(active=True, superuser=True) # Hanya superuser