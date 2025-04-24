# File: auth/strategy.py
import os
from fastapi_users.authentication import (
    CookieTransport,
    JWTStrategy,
    AuthenticationBackend,
    BearerTransport # Import BearerTransport untuk header Authorization
)
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("SECRET_KEY", "fallback_secret_key_harap_diganti")
if SECRET == "fallback_secret_key_harap_diganti":
    print("PERINGATAN: SECRET_KEY tidak diatur di .env, gunakan fallback yang tidak aman!")

# --- STRATEGI OTENTIKASI ---

# 1. Cookie Transport (jika ingin auth berbasis cookie)
# cookie_transport = CookieTransport(cookie_name="quizappauth", cookie_max_age=3600*24*7) # Contoh: cookie 1 minggu

# 2. Bearer Transport (untuk token di header Authorization: Bearer <token>)
bearer_transport = BearerTransport(tokenUrl="/api/v1/auth/login") # Path ke endpoint login JWT

# 3. JWT Strategy (Logika pembuatan & validasi token)
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600 * 24) # Contoh: token valid 1 hari

# --- AUTHENTICATION BACKEND ---
# Pilih backend yang akan digunakan (bisa satu atau lebih)

# Contoh jika pakai Cookie
# auth_backend_cookie = AuthenticationBackend(
#     name="jwt_cookie",
#     transport=cookie_transport,
#     get_strategy=get_jwt_strategy,
# )

# Contoh jika pakai Bearer Token (umum untuk API + SPA Frontend)
auth_backend_jwt = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport, # Gunakan Bearer transport
    get_strategy=get_jwt_strategy,
)

# Anda bisa mengekspor list berisi semua backend aktif jika perlu
# active_auth_backends = [auth_backend_jwt]