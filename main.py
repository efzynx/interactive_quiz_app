# File: main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# Impor router API Kuis
from api.v1.api import api_router as api_router_v1

# Impor komponen FastAPI-Users
from auth.core import fastapi_users
from auth.strategy import auth_backend_jwt # Impor backend auth yang Anda pilih
from models.user_models import User, UserRead, UserCreate, UserUpdate, uuid # Impor model & skema

# (Opsional) Impor dotenv jika ingin memuat .env di sini juga
# from dotenv import load_dotenv
# load_dotenv()

# Inisialisasi Aplikasi FastAPI
app = FastAPI(
    title="Interactive Quiz API with Auth",
    description="API untuk Kuis Pengetahuan Umum Interaktif dengan fitur Otentikasi Pengguna.",
    version="0.2.0" # Naikkan versi karena ada fitur baru
)

# --- Konfigurasi CORS ---
# PENTING: Sesuaikan origins dengan alamat frontend Anda!
origins = [
    "http://localhost:5500",          # Ganti 5500 dengan port frontend Anda
    "http://127.0.0.1:5500",
    # "http://localhost:3000",   # Contoh jika pakai React/Vue dev server
    # "https://domain-frontend-anda.com" # Untuk production
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # Penting jika pakai cookie atau auth header
    allow_methods=["*"],
    allow_headers=["*"],    # Izinkan semua header (termasuk Authorization)
)
# -----------------------

# --- Sertakan Router FastAPI-Users ---
# Endpoint untuk Login & Logout (tergantung backend auth yang dipilih)
app.include_router(
    fastapi_users.get_auth_router(auth_backend_jwt), # Gunakan backend JWT
    prefix="/api/v1/auth", # Prefix path
    tags=["Auth"],         # Grup di dokumentasi API
)

# Endpoint untuk Registrasi User Baru
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate), # Tentukan skema read & create
    prefix="/api/v1/auth",
    tags=["Auth"],
)

# Endpoint untuk Reset Password
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/api/v1/auth",
    tags=["Auth"],
)

# Endpoint untuk Verifikasi Email (jika diaktifkan di UserManager)
app.include_router(
    fastapi_users.get_verify_router(UserRead), # Tentukan skema read
    prefix="/api/v1/auth",
    tags=["Auth"],
)

# Endpoint untuk Manajemen User (GET /me, PATCH /me, GET /{id})
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate), # Tentukan skema read & update
    prefix="/api/v1/users",
    tags=["Users"],
)
# -----------------------------------

# --- Sertakan Router API Kuis Anda ---
app.include_router(api_router_v1, prefix="/api/v1")
# -----------------------------------

# --- Contoh Root Endpoint ---
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Interactive Quiz API! Docs at /docs"}

# --- Contoh Endpoint Terproteksi ---
# Hanya bisa diakses oleh user yang sudah login dan aktif
@app.get("/api/v1/protected-route", tags=["Example"])
async def protected_route(user: User = Depends(fastapi_users.current_user(active=True))):
    """Contoh endpoint yang memerlukan otentikasi."""
    return {"message": f"Hello {user.email}! You are accessing a protected route."}
# ---------------------------------

# Jika perlu event startup/shutdown (misal cek koneksi DB awal)
# @app.on_event("startup")
# async def on_startup():
#     print("Aplikasi FastAPI dimulai...")
#     # Cek koneksi DB atau init resource lain

# @app.on_event("shutdown")
# async def on_shutdown():
#     print("Aplikasi FastAPI berhenti...")