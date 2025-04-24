# File: models/base.py (BARU)

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Kelas dasar deklaratif untuk model SQLAlchemy."""
    pass

# Anda bisa menambahkan metadata default atau naming convention di sini jika perlu
# from sqlalchemy import MetaData
# metadata = MetaData(naming_convention={...})
# class Base(DeclarativeBase):
#     metadata = metadata