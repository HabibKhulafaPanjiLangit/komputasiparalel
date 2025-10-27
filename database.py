"""
Database Models untuk MPI Payroll System
SQLAlchemy ORM Models
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Base class untuk semua models
Base = declarative_base()


class Karyawan(Base):
    """Model untuk data karyawan"""
    __tablename__ = 'karyawan'
    
    id = Column(String(50), primary_key=True)
    nama = Column(String(100), nullable=False)
    jabatan = Column(String(50), nullable=False)
    gaji_pokok = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nama': self.nama,
            'jabatan': self.jabatan,
            'gaji_pokok': self.gaji_pokok
        }


class Absen(Base):
    """Model untuk data absensi"""
    __tablename__ = 'absen'
    
    id = Column(String(50), primary_key=True)
    hari_masuk = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hari_masuk': self.hari_masuk
        }


class Gaji(Base):
    """Model untuk data gaji (hasil perhitungan)"""
    __tablename__ = 'gaji'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    karyawan_id = Column(String(50), nullable=False)
    nama = Column(String(100), nullable=False)
    jabatan = Column(String(50), nullable=False)
    gaji_pokok = Column(Float, nullable=False)
    hari_masuk = Column(Integer, nullable=False)
    total_gaji = Column(Float, nullable=False)
    mode_hitung = Column(String(20))  # 'serial' atau 'parallel'
    waktu_hitung = Column(Float)  # waktu eksekusi dalam detik
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.karyawan_id,
            'nama': self.nama,
            'jabatan': self.jabatan,
            'gaji_pokok': self.gaji_pokok,
            'hari_masuk': self.hari_masuk,
            'total_gaji': self.total_gaji
        }


# Database connection setup
def get_database_url():
    """Get database URL from environment or use SQLite as fallback"""
    # Untuk production (Railway/Render), gunakan DATABASE_URL dari environment
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Railway/Render provide DATABASE_URL
        # Fix for psycopg2 (change postgresql:// to postgresql+psycopg2://)
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql+psycopg2://', 1)
        elif database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
        return database_url
    else:
        # Local development, gunakan SQLite
        return 'sqlite:///payroll.db'


def init_db():
    """Initialize database and create all tables"""
    database_url = get_database_url()
    engine = create_engine(database_url, echo=False)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session factory
    Session = sessionmaker(bind=engine)
    
    return engine, Session


def get_session():
    """Get database session"""
    _, Session = init_db()
    return Session()


# Auto initialize on import
try:
    engine, SessionFactory = init_db()
    print(f"[DB] Database initialized: {get_database_url()}")
except Exception as e:
    print(f"[DB] Error initializing database: {e}")
    engine = None
    SessionFactory = None
