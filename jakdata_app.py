"""
JAKDATA - Aplikasi Pendataan Warga DKI Jakarta
Sistem Monitoring Kinerja Tim Koordinator Lapangan
Versi 2.0 - PostgreSQL + Enkripsi Data
"""

import streamlit as st
import pandas as pd
import hashlib
import re
from datetime import datetime
import io
import psycopg2
from psycopg2.extras import RealDictCursor
from cryptography.fernet import Fernet
import os

# ============================================================
# KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="JAKDATA - Pendataan Warga DKI Jakarta",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS KUSTOM - TEMA BIRU/PUTIH PROFESIONAL
# ============================================================
st.markdown("""
<style>
/* Import Font */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Main background */
.stApp {
    background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 50%, #f5f7ff 100%);
}

/* Header utama */
.main-header {
    background: linear-gradient(135deg, #0d47a1 0%, #1565c0 40%, #1976d2 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(13,71,161,0.3);
    color: white;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.main-header::after {
    content: '';
    position: absolute;
    bottom: -30%;
    right: 10%;
    width: 250px;
    height: 250px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.main-header h1 {
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.5px;
}
.main-header p {
    margin: 0.3rem 0 0 0;
    opacity: 0.85;
    font-size: 0.95rem;
    font-weight: 400;
}

/* Metric cards */
.metric-card {
    background: white;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 2px 16px rgba(13,71,161,0.08);
    border: 1px solid rgba(13,71,161,0.06);
    border-left: 4px solid #1976d2;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 24px rgba(13,71,161,0.14);
}
.metric-card .metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    color: #0d47a1;
    line-height: 1;
}
.metric-card .metric-label {
    font-size: 0.82rem;
    color: #666;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 0.3rem;
}
.metric-card .metric-icon {
    font-size: 1.8rem;
    margin-bottom: 0.5rem;
}

/* Section titles */
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0d47a1;
    margin: 1.5rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e3ecff;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Form container */
.form-container {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 2px 16px rgba(13,71,161,0.08);
    border: 1px solid rgba(13,71,161,0.06);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d47a1 0%, #1565c0 100%);
}
[data-testid="stSidebar"] * {
    color: white !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label {
    color: rgba(255,255,255,0.9) !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.2) !important;
}

/* Sidebar logo area */
.sidebar-logo {
    text-align: center;
    padding: 1rem 0 1.5rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.2);
    margin-bottom: 1rem;
}
.sidebar-logo h2 {
    font-size: 1.6rem;
    font-weight: 800;
    color: white;
    margin: 0.3rem 0;
    letter-spacing: -0.5px;
}
.sidebar-logo p {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.75);
    margin: 0;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1565c0, #1976d2);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-family: 'Plus Jakarta Sans', sans-serif;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(13,71,161,0.25);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #0d47a1, #1565c0);
    box-shadow: 0 4px 16px rgba(13,71,161,0.35);
    transform: translateY(-1px);
}

/* Success / Error messages */
.stSuccess {
    border-radius: 10px;
}
.stError {
    border-radius: 10px;
}

/* Input fields */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    border-radius: 8px !important;
    border: 1.5px solid #dde6ff !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #1976d2 !important;
    box-shadow: 0 0 0 3px rgba(25,118,210,0.12) !important;
}

/* Login card */
.login-card {
    background: white;
    border-radius: 20px;
    padding: 3rem;
    max-width: 420px;
    margin: 3rem auto;
    box-shadow: 0 8px 40px rgba(13,71,161,0.15);
    border: 1px solid rgba(13,71,161,0.06);
}
.login-logo {
    text-align: center;
    margin-bottom: 2rem;
}
.login-logo h1 {
    font-size: 2.5rem;
    font-weight: 800;
    color: #0d47a1;
    margin: 0;
}
.login-logo p {
    color: #888;
    font-size: 0.9rem;
    margin: 0.3rem 0 0 0;
}

/* Info badge */
.info-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #e8f0fe;
    color: #1565c0;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}

/* Table styling */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}

/* GPS info box */
.gps-box {
    background: #e8f0fe;
    border: 1.5px solid #bbdefb;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
    font-size: 0.9rem;
    color: #1565c0;
    font-weight: 500;
}

/* Rank badge */
.rank-badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
}
.rank-admin { background: #fce4ec; color: #c62828; }
.rank-korwil { background: #e8f5e9; color: #2e7d32; }
.rank-korcam { background: #e3f2fd; color: #1565c0; }
.rank-korkel { background: #fff3e0; color: #e65100; }
.rank-korgas { background: #f3e5f5; color: #6a1b9a; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: #e8f0fe;
    padding: 0.4rem;
    border-radius: 12px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 600;
    color: #1565c0;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #0d47a1 !important;
    box-shadow: 0 2px 8px rgba(13,71,161,0.12);
}

/* Chart area */
.chart-card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem;
    box-shadow: 0 2px 16px rgba(13,71,161,0.08);
    border: 1px solid rgba(13,71,161,0.06);
}

/* Divider */
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #dde6ff, transparent);
    margin: 1.5rem 0;
}

/* ============================================
   MOBILE RESPONSIVE — Optimasi untuk HP
   ============================================ */
@media (max-width: 768px) {

    /* Header lebih kompak di HP */
    .main-header {
        padding: 1.2rem 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .main-header h1 {
        font-size: 1.4rem;
    }
    .main-header p {
        font-size: 0.8rem;
    }

    /* Metric cards lebih kecil di HP */
    .metric-card {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    .metric-card .metric-value {
        font-size: 1.6rem;
    }
    .metric-card .metric-label {
        font-size: 0.72rem;
    }
    .metric-card .metric-icon {
        font-size: 1.3rem;
    }

    /* Form container di HP */
    .form-container {
        padding: 1rem;
        border-radius: 10px;
    }

    /* Login card full width di HP */
    .login-card {
        padding: 1.5rem 1rem;
        margin: 1rem auto;
        border-radius: 14px;
    }
    .login-logo h1 {
        font-size: 2rem;
    }

    /* Tombol lebih besar di HP — mudah dipencet */
    .stButton > button {
        min-height: 48px !important;
        font-size: 1rem !important;
        border-radius: 10px !important;
    }

    /* Input field lebih besar di HP */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        font-size: 16px !important;
        min-height: 44px !important;
        padding: 0.6rem 0.8rem !important;
    }

    /* Selectbox lebih besar di HP */
    .stSelectbox > div > div {
        min-height: 44px !important;
        font-size: 16px !important;
    }

    /* Section title lebih kecil di HP */
    .section-title {
        font-size: 0.95rem;
        margin: 1rem 0 0.7rem 0;
    }

    /* GPS box di HP */
    .gps-box {
        font-size: 0.82rem;
        padding: 0.8rem;
        flex-direction: column;
        gap: 0.4rem;
    }

    /* Tab di HP */
    .stTabs [data-baseweb="tab"] {
        font-size: 0.82rem;
        padding: 0.4rem 0.6rem;
    }

    /* Dataframe di HP */
    .stDataFrame {
        font-size: 0.8rem;
    }

    /* Sidebar lebih baik di HP */
    [data-testid="stSidebar"] {
        min-width: 200px !important;
    }
}

/* Tombol navigasi sidebar lebih besar */
[data-testid="stSidebar"] .stButton > button {
    min-height: 44px !important;
    font-size: 0.9rem !important;
    text-align: left !important;
    padding-left: 1rem !important;
}

/* Badge info */
.status-badge-merah {
    background: #ffebee;
    color: #c62828;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 700;
    display: inline-block;
}
.status-badge-kuning {
    background: #fff8e1;
    color: #f57f17;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 700;
    display: inline-block;
}
.status-badge-hijau {
    background: #e8f5e9;
    color: #2e7d32;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 700;
    display: inline-block;
}

/* Warning box wilayah terkunci */
.wilayah-locked {
    background: #e8f0fe;
    border: 2px solid #1976d2;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    color: #0d47a1;
    font-weight: 600;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA WILAYAH DKI JAKARTA (HARDCODED LENGKAP)
# ============================================================
WILAYAH_DKI = {
    "Jakarta Pusat": {
        "Gambir": ["Gambir", "Cideng", "Petojo Selatan", "Petojo Utara", "Kebon Kelapa", "Duri Pulo"],
        "Sawah Besar": ["Pasar Baru", "Mangga Dua Selatan", "Kartini", "Gunung Sahari Utara", "Karang Anyar"],
        "Kemayoran": ["Kemayoran", "Serdang", "Gunung Sahari Selatan", "Harapan Mulya", "Utan Panjang", "Cempaka Baru", "Sumur Batu", "Kebon Kosong"],
        "Senen": ["Senen", "Kenari", "Paseban", "Kramat", "Kwitang", "Bungur"],
        "Cempaka Putih": ["Cempaka Putih Timur", "Cempaka Putih Barat", "Rawasari"],
        "Menteng": ["Menteng", "Pegangsaan", "Cikini", "Gondangdia", "Kebon Sirih"],
        "Tanah Abang": ["Tanah Abang", "Karet Tengsin", "Kebon Kacang", "Kebon Melati", "Bendungan Hilir", "Petamburan", "Kampung Bali"],
        "Johar Baru": ["Johar Baru", "Kampung Rawa", "Galur", "Tanah Tinggi"],
    },
    "Jakarta Utara": {
        "Penjaringan": ["Penjaringan", "Pluit", "Kamal Muara", "Kapuk Muara", "Pejagalan"],
        "Pademangan": ["Pademangan Barat", "Pademangan Timur", "Ancol"],
        "Tanjung Priok": ["Tanjung Priok", "Sunter Agung", "Sunter Jaya", "Papanggo", "Sungai Bambu", "Kebon Bawang", "Lagoa", "Koja"],
        "Koja": ["Koja", "Lagoa", "Rawa Badak Selatan", "Rawa Badak Utara", "Tugu Selatan", "Tugu Utara"],
        "Cilincing": ["Cilincing", "Semper Barat", "Semper Timur", "Rorotan", "Marunda", "Kalibaru", "Sukapura"],
        "Kelapa Gading": ["Kelapa Gading Barat", "Kelapa Gading Timur", "Pegangsaan Dua"],
    },
    "Jakarta Barat": {
        "Kembangan": ["Kembangan Utara", "Kembangan Selatan", "Joglo", "Srengseng", "Meruya Utara", "Meruya Selatan"],
        "Kebon Jeruk": ["Kebon Jeruk", "Sukabumi Selatan", "Sukabumi Utara", "Kelapa Dua", "Duri Kepa", "Kedoya Selatan", "Kedoya Utara"],
        "Palmerah": ["Palmerah", "Slipi", "Kota Bambu Selatan", "Kota Bambu Utara", "Jati Pulo", "Kemanggisan", "Jatipulo"],
        "Grogol Petamburan": ["Grogol", "Tanjung Duren Selatan", "Tanjung Duren Utara", "Tomang", "Jelambar", "Jelambar Baru", "Wijaya Kusuma"],
        "Tambora": ["Tambora", "Kali Anyar", "Duri Utara", "Tanah Sereal", "Angke", "Jembatan Lima", "Pekojan", "Roa Malaka", "Duri Selatan", "Jembatan Besi"],
        "Cengkareng": ["Cengkareng Barat", "Cengkareng Timur", "Kapuk", "Rawa Buaya", "Kedaung Kaliangke", "Duri Kosambi"],
        "Kalideres": ["Kalideres", "Semanan", "Tegal Alur", "Pegadungan", "Kamal"],
    },
    "Jakarta Selatan": {
        "Jagakarsa": ["Jagakarsa", "Srengseng Sawah", "Ciganjur", "Lenteng Agung", "Tanjung Barat", "Cipedak"],
        "Pasar Minggu": ["Pasar Minggu", "Jati Padang", "Cilandak Timur", "Ragunan", "Pejaten Barat", "Pejaten Timur", "Kebagusan"],
        "Cilandak": ["Cilandak Barat", "Lebak Bulus", "Gandaria Selatan", "Cipete Selatan", "Pondok Labu"],
        "Pesanggrahan": ["Pesanggrahan", "Bintaro", "Ulujami", "Petukangan Selatan", "Petukangan Utara"],
        "Kebayoran Lama": ["Kebayoran Lama Selatan", "Kebayoran Lama Utara", "Pondok Pinang", "Cipulir", "Grogol Selatan", "Grogol Utara"],
        "Kebayoran Baru": ["Selong", "Gunung", "Kramat Pela", "Gandaria Utara", "Cipete Utara", "Pulo", "Petogogan", "Rawa Barat", "Senayan", "Melawai", "Mahakam", "Kartika"],
        "Mampang Prapatan": ["Mampang Prapatan", "Bangka", "Pela Mampang", "Tegal Parang", "Kuningan Barat"],
        "Pancoran": ["Pancoran", "Duren Tiga", "Kalibata", "Rawajati", "Pengadegan", "Cikoko"],
        "Tebet": ["Tebet Barat", "Tebet Timur", "Kebon Baru", "Bukit Duri", "Manggarai Selatan", "Manggarai"],
        "Setia Budi": ["Setiabudi", "Karet", "Karet Semanggi", "Karet Kuningan", "Kuningan Timur", "Menteng Atas", "Pasar Manggis", "Guntur"],
    },
    "Jakarta Timur": {
        "Pasar Rebo": ["Gedong", "Baru", "Cijantung", "Kalisari", "Pekayon"],
        "Ciracas": ["Ciracas", "Cibubur", "Kelapa Dua Wetan", "Susukan", "Rambutan"],
        "Cipayung": ["Cipayung", "Cilangkap", "Pondok Ranggon", "Munjul", "Setu", "Bambu Apus", "Lubang Buaya", "Ceger"],
        "Makasar": ["Makasar", "Pinang Ranti", "Kebon Pala", "Halim Perdana Kusuma", "Cipinang Melayu"],
        "Kramat Jati": ["Kramat Jati", "Batu Ampar", "Cawang", "Cililitan", "Dukuh", "Tengah", "Kampung Tengah"],
        "Jatinegara": ["Kampung Melayu", "Bidara Cina", "Cipinang Cempedak", "Cipinang Muara", "Rawa Bunga", "Cipinang Besar Selatan", "Cipinang Besar Utara", "Bali Mester"],
        "Duren Sawit": ["Duren Sawit", "Pondok Bambu", "Klender", "Pondok Kelapa", "Malaka Jaya", "Malaka Sari", "Pondok Kopi"],
        "Cakung": ["Cakung Barat", "Cakung Timur", "Penggilingan", "Rawa Terate", "Jatinegara", "Ujung Menteng", "Pulogebang"],
        "Pulo Gadung": ["Pulo Gadung", "Rawamangun", "Kayu Putih", "Jati", "Pisangan Timur", "Cipinang", "Jatinegara Kaum"],
        "Matraman": ["Matraman", "Palmeriam", "Kebon Manggis", "Utan Kayu Selatan", "Utan Kayu Utara", "Kayu Manis"],
    },
    "Kepulauan Seribu": {
        "Kepulauan Seribu Utara": ["Pulau Kelapa", "Pulau Harapan", "Pulau Panggang"],
        "Kepulauan Seribu Selatan": ["Pulau Tidung", "Pulau Pari", "Pulau Untung Jawa"],
    },
}


# ============================================================
# ENKRIPSI DATA (UU PDP Compliant)
# ============================================================
@st.cache_resource
def get_cipher():
    """Ambil cipher dari ENCRYPT_KEY di Secrets"""
    try:
        key = st.secrets["ENCRYPT_KEY"]
        return Fernet(key.encode())
    except:
        return None

def encrypt_data(data: str) -> str:
    if not data or not data.strip():
        return data
    try:
        cipher = get_cipher()
        if cipher:
            return cipher.encrypt(data.encode()).decode()
    except:
        pass
    return data

def decrypt_data(data: str) -> str:
    if not data or not data.strip():
        return data
    try:
        cipher = get_cipher()
        if cipher:
            return cipher.decrypt(data.encode()).decode()
    except:
        pass
    return data

# ============================================================
# DATABASE — PostgreSQL dengan koneksi stabil & auto-reconnect
# ============================================================
def get_db():
    """Buat koneksi PostgreSQL baru setiap query — paling stabil"""
    try:
        db_url = st.secrets["DATABASE_URL"]
        conn = psycopg2.connect(
            db_url,
            cursor_factory=RealDictCursor,
            connect_timeout=10,
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5
        )
        conn.autocommit = False
        return conn
    except Exception as e:
        st.error(f"❌ Gagal koneksi database: {str(e)}")
        return None

def run_query(query, params=None, fetch=True):
    """Jalankan query — koneksi dibuka & ditutup otomatis"""
    conn = get_db()
    if not conn:
        return [] if fetch else False
    try:
        cur = conn.cursor()
        cur.execute(query, params or ())
        if fetch:
            result = cur.fetchall()
            conn.close()
            return [dict(row) for row in result]
        else:
            conn.commit()
            conn.close()
            return True
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        if fetch:
            return []
        return False

def run_query_one(query, params=None):
    result = run_query(query, params, fetch=True)
    return result[0] if result else None

def get_count(query, params=None):
    """Helper khusus untuk query COUNT"""
    r = run_query_one(query, params)
    if not r:
        return 0
    return int(list(r.values())[0])

def init_db():
    """Inisialisasi semua tabel PostgreSQL"""
    conn = get_db()
    if not conn:
        return
    try:
        cur = conn.cursor()

        # Tabel users
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                nama_lengkap VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                kota VARCHAR(100) DEFAULT '',
                kecamatan VARCHAR(100) DEFAULT '',
                kelurahan VARCHAR(100) DEFAULT '',
                rw VARCHAR(20) DEFAULT '',
                created_at TIMESTAMP DEFAULT NOW(),
                is_active INTEGER DEFAULT 1,
                last_login TIMESTAMP,
                login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
        """)

        # Tabel warga
        cur.execute("""
            CREATE TABLE IF NOT EXISTS warga (
                id SERIAL PRIMARY KEY,
                nama_lengkap VARCHAR(255) NOT NULL,
                nik VARCHAR(512) UNIQUE NOT NULL,
                no_telepon VARCHAR(512),
                alamat TEXT,
                kota VARCHAR(100),
                kecamatan VARCHAR(100),
                kelurahan VARCHAR(100),
                rw INTEGER,
                rt INTEGER,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                diinput_oleh VARCHAR(100),
                diinput_nama VARCHAR(255),
                role_input VARCHAR(50),
                kota_petugas VARCHAR(100),
                kecamatan_petugas VARCHAR(100),
                kelurahan_petugas VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Tabel audit log
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100),
                nama VARCHAR(255),
                aksi VARCHAR(100),
                detail TEXT,
                ip_address VARCHAR(50),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Tambah kolom baru jika belum ada (untuk upgrade)
        for col_sql in [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS login_attempts INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP",
        ]:
            try:
                cur.execute(col_sql)
            except:
                pass

        # Admin default
        admin_pw = hash_password("admin123")
        cur.execute("""
            INSERT INTO users (username, password, nama_lengkap, role)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        """, ("admin", admin_pw, "Administrator Provinsi DKI Jakarta", "Admin"))

        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        conn.close()

def catat_log(username, nama, aksi, detail=""):
    """Catat aktivitas ke audit log"""
    run_query("""
        INSERT INTO audit_log (username, nama, aksi, detail)
        VALUES (%s, %s, %s, %s)
    """, (username, nama, aksi, detail), fetch=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ============================================================
# FUNGSI AUTENTIKASI — dengan proteksi brute force
# ============================================================
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES    = 15

def login(username, password):
    """Login dengan proteksi brute force"""
    from datetime import timezone
    now = datetime.now()

    # Cek apakah user ada
    user = run_query_one(
        "SELECT * FROM users WHERE username=%s AND is_active=1",
        (username,)
    )
    if not user:
        return None, "❌ Username atau password salah!"

    # Cek apakah akun terkunci
    locked_until = user.get("locked_until")
    if locked_until:
        if isinstance(locked_until, str):
            locked_until = datetime.fromisoformat(locked_until)
        # Hapus timezone info untuk perbandingan
        if hasattr(locked_until, 'tzinfo') and locked_until.tzinfo:
            locked_until = locked_until.replace(tzinfo=None)
        if now < locked_until:
            sisa = int((locked_until - now).total_seconds() / 60) + 1
            return None, f"🔒 Akun terkunci! Coba lagi dalam {sisa} menit."

    # Verifikasi password
    hashed = hash_password(password)
    if user["password"] != hashed:
        attempts = (user.get("login_attempts") or 0) + 1
        if attempts >= MAX_LOGIN_ATTEMPTS:
            from datetime import timedelta
            lock_time = now + timedelta(minutes=LOCKOUT_MINUTES)
            run_query("""
                UPDATE users SET login_attempts=%s, locked_until=%s
                WHERE username=%s
            """, (attempts, lock_time, username), fetch=False)
            catat_log(username, user["nama_lengkap"], "LOGIN_GAGAL_TERKUNCI",
                     f"Akun terkunci setelah {attempts} percobaan")
            return None, f"🔒 Terlalu banyak percobaan! Akun terkunci {LOCKOUT_MINUTES} menit."
        else:
            run_query(
                "UPDATE users SET login_attempts=%s WHERE username=%s",
                (attempts, username), fetch=False
            )
            sisa_coba = MAX_LOGIN_ATTEMPTS - attempts
            catat_log(username, user["nama_lengkap"], "LOGIN_GAGAL",
                     f"Password salah, sisa percobaan: {sisa_coba}")
            return None, f"❌ Password salah! Sisa percobaan: {sisa_coba}"

    # Login berhasil — reset attempts, catat waktu login
    run_query("""
        UPDATE users SET login_attempts=0, locked_until=NULL, last_login=%s
        WHERE username=%s
    """, (now, username), fetch=False)

    catat_log(username, user["nama_lengkap"], "LOGIN_BERHASIL", "Login ke sistem")
    return dict(user), None

def logout():
    user = st.session_state.get("user", {})
    if user:
        catat_log(user.get("username",""), user.get("nama_lengkap",""), "LOGOUT", "Keluar dari sistem")
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ============================================================
# HALAMAN LOGIN
# ============================================================
def page_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div class="login-card">
            <div class="login-logo">
                <div style="font-size:3rem;">🏙️</div>
                <h1>JAKDATA</h1>
                <p>Sistem Pendataan Warga DKI Jakarta</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown("### 🔐 Masuk ke Sistem")
            username = st.text_input("Username", placeholder="Masukkan username...")
            password = st.text_input("Password", type="password", placeholder="Masukkan password...")

            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button("🚀 Masuk", use_container_width=True):
                    if username and password:
                        user, pesan = login(username.strip().lower(), password)
                        if user:
                            st.session_state["user"] = user
                            st.session_state["page"] = "dashboard"
                            st.success("✅ Login berhasil!")
                            st.rerun()
                        else:
                            st.error(pesan)
                    else:
                        st.warning("⚠️ Harap isi username dan password.")

            st.markdown("---")
            st.caption("📌 Hubungi administrator untuk mendapatkan akun koordinator.")

# ============================================================
# SIDEBAR NAVIGASI
# ============================================================
def render_sidebar():
    user = st.session_state.get("user", {})

    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <div style="font-size:2.5rem;">🏙️</div>
            <h2>JAKDATA</h2>
            <p>Pendataan Warga DKI Jakarta</p>
        </div>
        """, unsafe_allow_html=True)

        role = user.get("role", "-")
        nama = user.get("nama_lengkap", "-")

        role_colors = {
            "Admin": "🔴", "Korwil": "🟢", "Korcam": "🔵", "Korkel": "🟠", "Korgas": "🟣"
        }
        icon = role_colors.get(role, "⚪")
        st.markdown(f"**{icon} {nama}**")
        st.markdown(f"*Peran: {role}*")

        if role in ["Korwil", "Korcam", "Korkel", "Korgas"]:
            if user.get("kota"):
                st.caption(f"📍 {user.get('kota', '')}")
            if user.get("kecamatan"):
                st.caption(f"🏘️ {user.get('kecamatan', '')}")
            if user.get("kelurahan"):
                st.caption(f"🏠 {user.get('kelurahan', '')}")
            if user.get("rw"):
                st.caption(f"🏡 RW {user.get('rw', '')}")

        # Tampilkan last login
        last_login = user.get("last_login")
        if last_login:
            if isinstance(last_login, str):
                last_login = last_login[:16]
            else:
                last_login = str(last_login)[:16]
            st.caption(f"🕐 Login: {last_login}")

        st.markdown("---")
        st.markdown("**📋 MENU NAVIGASI**")

        menus = ["📊 Dashboard", "➕ Input Data Warga", "📋 Data Warga"]
        if role == "Admin":
            menus += ["👥 Manajemen Tim", "📜 Audit Log", "⚙️ Pengaturan"]
        else:
            menus += ["⚙️ Pengaturan"]

        current_page = st.session_state.get("page", "dashboard")
        page_map = {
            "📊 Dashboard":        "dashboard",
            "➕ Input Data Warga": "input_warga",
            "📋 Data Warga":       "data_warga",
            "👥 Manajemen Tim":    "manajemen_tim",
            "📜 Audit Log":        "audit_log",
            "⚙️ Pengaturan":       "pengaturan",
        }

        for menu in menus:
            is_active = page_map.get(menu) == current_page
            if st.button(menu, use_container_width=True, key=f"nav_{menu}"):
                st.session_state["page"] = page_map[menu]
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Keluar", use_container_width=True):
            logout()


# ============================================================
# HALAMAN DASHBOARD
# ============================================================
def page_dashboard():
    user = st.session_state.get("user", {})
    role = user.get("role", "")

    st.markdown("""
    <div class="main-header">
        <h1>📊 Dashboard Monitoring</h1>
        <p>Sistem Pemantauan Kinerja Tim Koordinator Lapangan DKI Jakarta</p>
    </div>
    """, unsafe_allow_html=True)

    def get_count(query, params=None):
        """Helper ambil nilai COUNT dari PostgreSQL"""
        r = run_query_one(query, params)
        if not r:
            return 0
        # PostgreSQL mengembalikan 'count' bukan nama alias
        for key in ["count", "total"]:
            if key in r:
                return int(r[key])
        # Ambil nilai pertama apapun kuncinya
        return int(list(r.values())[0])

    # --- QUERY berdasarkan role ---
    if role == "Admin":
        total_warga      = get_count("SELECT COUNT(*) FROM warga")
        total_koordinator= get_count("SELECT COUNT(*) FROM users WHERE role != 'Admin' AND is_active=1")
        total_korwil     = get_count("SELECT COUNT(*) FROM users WHERE role='Korwil' AND is_active=1")
        total_korcam     = get_count("SELECT COUNT(*) FROM users WHERE role='Korcam' AND is_active=1")
        rows = run_query("SELECT kota, COUNT(*) as jumlah FROM warga GROUP BY kota ORDER BY jumlah DESC")
        df_kota = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["kota","jumlah"])
        rows = run_query("SELECT kecamatan, COUNT(*) as jumlah FROM warga GROUP BY kecamatan ORDER BY jumlah DESC LIMIT 15")
        df_kecamatan = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["kecamatan","jumlah"])
        rows = run_query("""
            SELECT u.nama_lengkap, u.kota, u.role, COUNT(w.id) as total_warga
            FROM users u LEFT JOIN warga w ON u.username = w.diinput_oleh
            WHERE u.role != 'Admin' AND u.is_active=1
            GROUP BY u.id, u.nama_lengkap, u.kota, u.role
            ORDER BY total_warga DESC
        """)
        df_korwil_perf = pd.DataFrame(rows) if rows else pd.DataFrame()

    elif role == "Korwil":
        kota = user.get("kota", "")
        total_warga      = get_count("SELECT COUNT(*) FROM warga WHERE kota=%s", (kota,))
        total_koordinator= get_count("SELECT COUNT(*) FROM users WHERE kota=%s AND role != 'Korwil' AND is_active=1", (kota,))
        total_korwil     = 1
        total_korcam     = get_count("SELECT COUNT(*) FROM users WHERE kota=%s AND role='Korcam' AND is_active=1", (kota,))
        rows = run_query("SELECT kecamatan as kota, COUNT(*) as jumlah FROM warga WHERE kota=%s GROUP BY kecamatan ORDER BY jumlah DESC", (kota,))
        df_kota = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["kota","jumlah"])
        rows = run_query("SELECT kelurahan as kecamatan, COUNT(*) as jumlah FROM warga WHERE kota=%s GROUP BY kelurahan ORDER BY jumlah DESC LIMIT 15", (kota,))
        df_kecamatan = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["kecamatan","jumlah"])
        rows = run_query("""
            SELECT u.nama_lengkap, u.kecamatan, u.role, COUNT(w.id) as total_warga
            FROM users u LEFT JOIN warga w ON u.username = w.diinput_oleh
            WHERE u.kota=%s AND u.role != 'Admin' AND u.is_active=1
            GROUP BY u.id, u.nama_lengkap, u.kecamatan, u.role
            ORDER BY total_warga DESC
        """, (kota,))
        df_korwil_perf = pd.DataFrame(rows) if rows else pd.DataFrame()

    else:
        username = user.get("username", "")
        total_warga      = get_count("SELECT COUNT(*) FROM warga WHERE diinput_oleh=%s", (username,))
        total_koordinator= 1
        total_korwil     = 0
        total_korcam     = 0
        df_kota          = pd.DataFrame(columns=["kota", "jumlah"])
        df_kecamatan     = pd.DataFrame(columns=["kecamatan", "jumlah"])
        df_korwil_perf   = pd.DataFrame()

    # --- METRIC CARDS ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">👥</div>
            <div class="metric-value">{total_warga:,}</div>
            <div class="metric-label">Total Warga Terdata</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #43a047;">
            <div class="metric-icon">🏢</div>
            <div class="metric-value">{total_koordinator:,}</div>
            <div class="metric-label">Total Koordinator Aktif</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #fb8c00;">
            <div class="metric-icon">🌆</div>
            <div class="metric-value">{total_korwil:,}</div>
            <div class="metric-label">Koordinator Kota (Korwil)</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #8e24aa;">
            <div class="metric-icon">🏘️</div>
            <div class="metric-value">{total_korcam:,}</div>
            <div class="metric-label">Koordinator Kecamatan (Korcam)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # --- GRAFIK ---
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        label1 = "Kota" if role == "Admin" else "Kecamatan"
        st.markdown(f'<div class="section-title">📊 Warga Terdata per {label1}</div>', unsafe_allow_html=True)
        if not df_kota.empty:
            st.bar_chart(df_kota.set_index("kota")["jumlah"])
        else:
            st.info("Belum ada data.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_chart2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        label2 = "Kecamatan" if role == "Admin" else "Kelurahan"
        st.markdown(f'<div class="section-title">📊 Warga Terdata per {label2} (Top 15)</div>', unsafe_allow_html=True)
        if not df_kecamatan.empty:
            st.bar_chart(df_kecamatan.set_index("kecamatan")["jumlah"])
        else:
            st.info("Belum ada data.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # --- TABEL KINERJA TIM ---
    st.markdown('<div class="section-title">🏆 Kinerja Tim Koordinator</div>', unsafe_allow_html=True)
    if not df_korwil_perf.empty:
        st.dataframe(
            df_korwil_perf.rename(columns={
                "nama_lengkap": "Nama Koordinator",
                "kota": "Kota", "kecamatan": "Kecamatan",
                "role": "Jabatan", "total_warga": "Total Warga Didata"
            }),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("Belum ada data kinerja tim.")


# ============================================================
# HALAMAN INPUT DATA WARGA
# ============================================================
def page_input_warga():
    user = st.session_state.get("user", {})

    st.markdown("""
    <div class="main-header">
        <h1>➕ Input Data Warga</h1>
        <p>Formulir Pendataan Warga DKI Jakarta</p>
    </div>
    """, unsafe_allow_html=True)

    # Wilayah petugas — terkunci ketat sesuai role
    role = user.get("role", "")
    prefill_kota      = user.get("kota", "") or ""
    prefill_kecamatan = user.get("kecamatan", "") or ""
    prefill_kelurahan = user.get("kelurahan", "") or ""
    prefill_rw        = user.get("rw", "") or ""

    # ── PILIHAN WILAYAH ──
    st.markdown('<div class="section-title">📍 Wilayah Tempat Tinggal Warga</div>',
                unsafe_allow_html=True)

    if role == "Admin":
        # Admin bebas pilih semua wilayah
        col_k, col_kec, col_kel = st.columns(3)
        with col_k:
            kota = st.selectbox("Kota/Kabupaten *",
                ["-- Pilih --"] + list(WILAYAH_DKI.keys()), key="sel_kota")
        with col_kec:
            kec_opts = ["-- Pilih --"] + list(WILAYAH_DKI[kota].keys()) \
                       if kota != "-- Pilih --" else ["-- Pilih --"]
            kecamatan = st.selectbox("Kecamatan *", kec_opts, key="sel_kecamatan")
        with col_kel:
            kel_opts = ["-- Pilih --"] + WILAYAH_DKI[kota][kecamatan] \
                       if kota != "-- Pilih --" and kecamatan != "-- Pilih --" \
                       else ["-- Pilih --"]
            kelurahan = st.selectbox("Kelurahan *", kel_opts, key="sel_kelurahan")

    elif role == "Korwil":
        # Korwil: kota terkunci, kecamatan & kelurahan bebas pilih
        st.markdown(f"""
        <div class="wilayah-locked">
            🔒 Wilayah tugas Anda: <strong>{prefill_kota}</strong>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        kota = prefill_kota
        col_kec, col_kel = st.columns(2)
        with col_kec:
            kec_opts = ["-- Pilih --"] + list(WILAYAH_DKI.get(kota, {}).keys())
            kecamatan = st.selectbox("Kecamatan *", kec_opts, key="sel_kecamatan")
        with col_kel:
            kel_opts = ["-- Pilih --"] + WILAYAH_DKI.get(kota, {}).get(kecamatan, []) \
                       if kecamatan != "-- Pilih --" else ["-- Pilih --"]
            kelurahan = st.selectbox("Kelurahan *", kel_opts, key="sel_kelurahan")

    elif role == "Korcam":
        # Korcam: kota & kecamatan terkunci, kelurahan bebas pilih
        st.markdown(f"""
        <div class="wilayah-locked">
            🔒 Wilayah tugas Anda: <strong>{prefill_kota} → {prefill_kecamatan}</strong>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        kota = prefill_kota
        kecamatan = prefill_kecamatan
        kel_opts = ["-- Pilih --"] + WILAYAH_DKI.get(kota, {}).get(kecamatan, [])
        kelurahan = st.selectbox("Kelurahan *", kel_opts, key="sel_kelurahan")

    elif role == "Korkel":
        # Korkel: kota, kecamatan & kelurahan semua terkunci
        st.markdown(f"""
        <div class="wilayah-locked">
            🔒 Wilayah tugas Anda: <strong>{prefill_kota} → {prefill_kecamatan} → {prefill_kelurahan}</strong>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        kota      = prefill_kota
        kecamatan = prefill_kecamatan
        kelurahan = prefill_kelurahan

    elif role == "Korgas":
        # Korgas: semua wilayah + RW terkunci
        st.markdown(f"""
        <div class="wilayah-locked">
            🔒 Wilayah tugas Anda: <strong>{prefill_kota} → {prefill_kecamatan} → {prefill_kelurahan} → RW {prefill_rw}</strong>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        kota      = prefill_kota
        kecamatan = prefill_kecamatan
        kelurahan = prefill_kelurahan

    else:
        kota = kecamatan = kelurahan = "-- Pilih --"

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── FORM DATA WARGA ──
    with st.form("form_warga", clear_on_submit=True):
        st.markdown('<div class="section-title">👤 Data Identitas Warga</div>',
                    unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            nama   = st.text_input("Nama Lengkap *", placeholder="Nama sesuai KTP...")
            nik    = st.text_input("NIK (16 digit) *", placeholder="3171xxxxxxxxxxxxxxxx",
                                   max_chars=16)
        with col2:
            no_telp = st.text_input("Nomor Telepon/WA", placeholder="08xxxxxxxxxx")

        alamat = st.text_area("Alamat Lengkap *",
                              placeholder="Jl. ..., RT/RW, Kelurahan, Kecamatan", height=80)

        col_rw, col_rt = st.columns(2)
        with col_rw:
            # Korgas: RW terkunci sesuai wilayah tugas
            if role == "Korgas" and prefill_rw:
                rw_val = int(prefill_rw) if str(prefill_rw).isdigit() else 1
                st.text_input("RW (Terkunci)", value=str(rw_val), disabled=True)
                rw = rw_val
            else:
                rw = st.number_input("RW *", min_value=1, max_value=99, value=1)
        with col_rt:
            rt = st.number_input("RT *", min_value=1, max_value=99, value=1)

        # GPS
        st.markdown('<div class="section-title">🗺️ Titik Koordinat GPS</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="gps-box">
            📍 Masukkan koordinat GPS secara manual.<br>
            Cara: Buka Google Maps → tahan layar di lokasi warga → catat angka yang muncul.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")

        col_lat, col_lon = st.columns(2)
        with col_lat:
            latitude = st.number_input("Latitude", value=-6.2088, format="%.6f", step=0.000001)
        with col_lon:
            longitude = st.number_input("Longitude", value=106.8456, format="%.6f", step=0.000001)

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        submit = st.form_submit_button("💾 Simpan Data Warga", use_container_width=True)

    if submit:
        # Validasi
        errors = []
        if not nama.strip():
            errors.append("Nama Lengkap wajib diisi.")
        if not nik.strip():
            errors.append("NIK wajib diisi.")
        elif not re.match(r'^\d{16}$', nik.strip()):
            errors.append("NIK harus berupa 16 digit angka.")
        if not alamat.strip():
            errors.append("Alamat Lengkap wajib diisi.")
        if kota == "-- Pilih --":
            errors.append("Kota wajib dipilih.")
        if kecamatan == "-- Pilih --":
            errors.append("Kecamatan wajib dipilih.")
        if kelurahan == "-- Pilih --":
            errors.append("Kelurahan wajib dipilih.")

        if errors:
            for err in errors:
                st.error(f"❌ {err}")
        else:
            # Cek duplikat NIK — enkripsi NIK dulu untuk perbandingan
            nik_encrypted = encrypt_data(nik.strip())
            existing = run_query_one(
                "SELECT id FROM warga WHERE nik=%s", (nik_encrypted,)
            )
            if existing:
                st.error("❌ NIK sudah terdaftar! Warga ini sudah pernah didata.")
            else:
                try:
                    ok = run_query("""
                        INSERT INTO warga
                        (nama_lengkap, nik, no_telepon, alamat, kota, kecamatan,
                         kelurahan, rw, rt, latitude, longitude,
                         diinput_oleh, diinput_nama, role_input,
                         kota_petugas, kecamatan_petugas, kelurahan_petugas)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        nama.strip(),
                        encrypt_data(nik.strip()),
                        encrypt_data(no_telp.strip()),
                        encrypt_data(alamat.strip()),
                        kota, kecamatan, kelurahan,
                        int(rw), int(rt),
                        float(latitude), float(longitude),
                        user["username"], user["nama_lengkap"], role,
                        user.get("kota", ""),
                        user.get("kecamatan", ""),
                        user.get("kelurahan", "")
                    ), fetch=False)
                    if ok:
                        catat_log(
                            user["username"], user["nama_lengkap"],
                            "INPUT_WARGA",
                            f"Input data warga: {nama.strip()} | {kecamatan} - {kelurahan} RW{rw} RT{rt}"
                        )
                        st.success(f"✅ Data warga **{nama}** berhasil disimpan!")
                        st.balloons()
                    else:
                        st.error("❌ Gagal menyimpan data.")
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {str(e)}")


# ============================================================
# HALAMAN DATA WARGA
# ============================================================
def page_data_warga():
    user = st.session_state.get("user", {})
    role = user.get("role", "")

    st.markdown("""
    <div class="main-header">
        <h1>📋 Daftar Data Warga</h1>
        <p>Tabel Rekap Pendataan Warga DKI Jakarta</p>
    </div>
    """, unsafe_allow_html=True)

    # Filter sesuai role
    def fetch_warga(query, params=None):
        rows = run_query(query, params)
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        # Dekripsi kolom sensitif
        for col in ["nik", "no_telepon", "alamat"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: decrypt_data(x) if x else x)
        return df

    if role == "Admin":
        df = fetch_warga("""
            SELECT nama_lengkap as "Nama", nik as "NIK", no_telepon as "Telepon",
                   alamat as "Alamat", kota as "Kota", kecamatan as "Kecamatan",
                   kelurahan as "Kelurahan", rw as "RW", rt as "RT",
                   diinput_nama as "Petugas", role_input as "Jabatan Petugas",
                   created_at as "Tanggal Input"
            FROM warga ORDER BY created_at DESC
        """)
    elif role == "Korwil":
        kota = user.get("kota", "")
        df = fetch_warga("""
            SELECT nama_lengkap as "Nama", nik as "NIK", no_telepon as "Telepon",
                   alamat as "Alamat", kota as "Kota", kecamatan as "Kecamatan",
                   kelurahan as "Kelurahan", rw as "RW", rt as "RT",
                   diinput_nama as "Petugas", created_at as "Tanggal Input"
            FROM warga WHERE kota=%s ORDER BY created_at DESC
        """, (kota,))
    elif role == "Korcam":
        kecamatan = user.get("kecamatan", "")
        df = fetch_warga("""
            SELECT nama_lengkap as "Nama", nik as "NIK",
                   kelurahan as "Kelurahan", rw as "RW", rt as "RT",
                   diinput_nama as "Petugas", created_at as "Tanggal Input"
            FROM warga WHERE kecamatan=%s ORDER BY created_at DESC
        """, (kecamatan,))
    else:
        username = user.get("username", "")
        df = fetch_warga("""
            SELECT nama_lengkap as "Nama", nik as "NIK",
                   kelurahan as "Kelurahan", rw as "RW", rt as "RT",
                   created_at as "Tanggal Input"
            FROM warga WHERE diinput_oleh=%s ORDER BY created_at DESC
        """, (username,))

    # Filter UI
    st.markdown('<div class="section-title">🔍 Filter Data</div>', unsafe_allow_html=True)
    col_f1, col_f2, col_f3 = st.columns([1, 1, 2])

    filtered_df = df.copy()

    with col_f1:
        if "Kota" in df.columns and not df.empty:
            kota_opts = ["Semua"] + sorted(df["Kota"].dropna().unique().tolist())
            sel_kota = st.selectbox("Filter Kota", kota_opts)
            if sel_kota != "Semua":
                filtered_df = filtered_df[filtered_df["Kota"] == sel_kota]

    with col_f2:
        if "Kecamatan" in df.columns and not df.empty:
            kec_opts = ["Semua"] + sorted(df["Kecamatan"].dropna().unique().tolist())
            sel_kec = st.selectbox("Filter Kecamatan", kec_opts)
            if sel_kec != "Semua":
                filtered_df = filtered_df[filtered_df["Kecamatan"] == sel_kec]

    with col_f3:
        search = st.text_input("🔎 Cari nama / NIK / alamat...", placeholder="Ketik untuk mencari...")
        if search:
            mask = filtered_df.apply(lambda row: row.astype(str).str.contains(search, case=False, na=False).any(), axis=1)
            filtered_df = filtered_df[mask]

    st.markdown(f'<span class="info-badge">📊 Menampilkan {len(filtered_df):,} dari {len(df):,} data</span>', unsafe_allow_html=True)
    st.markdown("")

    # Tampilkan tabel
    if not filtered_df.empty:
        st.dataframe(filtered_df, use_container_width=True, hide_index=True, height=400)

        # Download Excel
        st.markdown('<div class="section-title">📥 Unduh Data</div>', unsafe_allow_html=True)
        col_dl1, col_dl2 = st.columns([1, 3])
        with col_dl1:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name="Data Warga")
            excel_data = output.getvalue()

            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name=f"JAKDATA_Warga_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    else:
        st.info("📭 Tidak ada data yang cocok dengan filter.")


# ============================================================
# HALAMAN MANAJEMEN TIM
# ============================================================
def page_manajemen_tim():
    st.markdown("""
    <div class="main-header">
        <h1>👥 Manajemen Tim Koordinator</h1>
        <p>Kelola akun dan wilayah tugas tim koordinator lapangan</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["➕ Tambah Koordinator", "📋 Daftar Tim"])

    with tab1:
        st.markdown('<div class="section-title">➕ Daftarkan Koordinator Baru</div>', unsafe_allow_html=True)
        with st.form("form_tambah_koordinator"):
            col1, col2 = st.columns(2)
            with col1:
                nama_koor = st.text_input("Nama Lengkap *")
                username_koor = st.text_input("Username *", placeholder="huruf kecil, tanpa spasi")
                password_koor = st.text_input("Password *", type="password")
            with col2:
                role_koor = st.selectbox("Jabatan *", ["Korwil", "Korcam", "Korkel", "Korgas"])

                # Wilayah berdasarkan role
                kota_koor = st.selectbox("Kota/Kabupaten Tugas", ["-- Pilih --"] + list(WILAYAH_DKI.keys()))
                kec_koor = "-- Pilih --"
                kel_koor = "-- Pilih --"

                if kota_koor != "-- Pilih --" and role_koor in ["Korcam", "Korkel", "Korgas"]:
                    kec_koor = st.selectbox("Kecamatan Tugas", ["-- Pilih --"] + list(WILAYAH_DKI[kota_koor].keys()))

                if kota_koor != "-- Pilih --" and kec_koor != "-- Pilih --" and role_koor in ["Korkel", "Korgas"]:
                    kel_koor = st.selectbox("Kelurahan Tugas", ["-- Pilih --"] + WILAYAH_DKI[kota_koor][kec_koor])

                rw_koor = ""
                if role_koor == "Korgas":
                    rw_koor = st.text_input("RW Tugas")

            submit_koor = st.form_submit_button("✅ Daftarkan Koordinator", use_container_width=True)

        if submit_koor:
            errors = []
            if not nama_koor.strip(): errors.append("Nama Lengkap wajib diisi.")
            if not username_koor.strip(): errors.append("Username wajib diisi.")
            if not password_koor.strip(): errors.append("Password wajib diisi.")
            if kota_koor == "-- Pilih --": errors.append("Kota/Kabupaten wajib dipilih.")

            if errors:
                for e in errors: st.error(f"❌ {e}")
            else:
                ok = run_query("""
                    INSERT INTO users (username, password, nama_lengkap, role, kota, kecamatan, kelurahan, rw)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (username) DO NOTHING
                """, (
                    username_koor.strip().lower(),
                    hash_password(password_koor),
                    nama_koor.strip(),
                    role_koor,
                    kota_koor if kota_koor != "-- Pilih --" else "",
                    kec_koor if kec_koor != "-- Pilih --" else "",
                    kel_koor if kel_koor != "-- Pilih --" else "",
                    rw_koor
                ), fetch=False)
                if ok:
                    st.success(f"✅ Koordinator **{nama_koor}** ({role_koor}) berhasil didaftarkan!")
                else:
                    st.error("❌ Username sudah digunakan atau terjadi kesalahan.")

    with tab2:
        st.markdown('<div class="section-title">📋 Daftar Semua Koordinator</div>', unsafe_allow_html=True)
        rows = run_query("""
            SELECT u.nama_lengkap as "Nama", u.username as "Username",
                   u.role as "Jabatan", u.kota as "Kota",
                   u.kecamatan as "Kecamatan", u.kelurahan as "Kelurahan",
                   u.rw as "RW", COUNT(w.id) as "Total Warga Didata",
                   CASE WHEN u.is_active=1 THEN '✅ Aktif' ELSE '❌ Nonaktif' END as "Status",
                   u.created_at as "Dibuat"
            FROM users u
            LEFT JOIN warga w ON u.username = w.diinput_oleh
            WHERE u.role != 'Admin'
            GROUP BY u.id, u.nama_lengkap, u.username, u.role,
                     u.kota, u.kecamatan, u.kelurahan, u.rw,
                     u.is_active, u.created_at
            ORDER BY u.role, u.kota
        """)
        df_tim = pd.DataFrame(rows) if rows else pd.DataFrame()

        if not df_tim.empty:
            st.dataframe(df_tim, use_container_width=True, hide_index=True)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_tim.to_excel(writer, index=False, sheet_name="Tim Koordinator")
            st.download_button(
                "📥 Download Daftar Tim",
                data=output.getvalue(),
                file_name=f"JAKDATA_Tim_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("Belum ada koordinator terdaftar.")

        # Kelola status koordinator
        st.markdown('<div class="section-title">⚙️ Kelola Status Koordinator</div>', unsafe_allow_html=True)
        rows_u = run_query("SELECT id, nama_lengkap, username, role, is_active FROM users WHERE role != 'Admin'")
        df_users = pd.DataFrame(rows_u) if rows_u else pd.DataFrame()

        if not df_users.empty:
            col_a, col_b = st.columns([2, 1])
            with col_a:
                sel_user = st.selectbox(
                    "Pilih Koordinator",
                    df_users["id"].tolist(),
                    format_func=lambda x: f"{df_users[df_users['id']==x]['nama_lengkap'].values[0]} ({df_users[df_users['id']==x]['role'].values[0]})"
                )
            with col_b:
                user_row = df_users[df_users["id"] == sel_user].iloc[0]
                current_status = user_row["is_active"]
                action_label = "❌ Nonaktifkan" if current_status == 1 else "✅ Aktifkan"
                if st.button(action_label, use_container_width=True):
                    new_status = 0 if current_status == 1 else 1
                    run_query(
                        "UPDATE users SET is_active=%s WHERE id=%s",
                        (new_status, sel_user), fetch=False
                    )
                    st.success("✅ Status berhasil diubah!")
                    st.rerun()


# ============================================================
# HALAMAN PENGATURAN
# ============================================================
def page_pengaturan():
    user = st.session_state.get("user", {})

    st.markdown("""
    <div class="main-header">
        <h1>⚙️ Pengaturan Akun</h1>
        <p>Kelola informasi dan keamanan akun Anda</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">🔑 Ubah Password</div>', unsafe_allow_html=True)
    with st.form("form_ganti_password"):
        old_pass = st.text_input("Password Lama *", type="password")
        new_pass = st.text_input("Password Baru *", type="password")
        confirm_pass = st.text_input("Konfirmasi Password Baru *", type="password")
        submit_pass = st.form_submit_button("🔒 Ubah Password", use_container_width=False)

    if submit_pass:
        if not all([old_pass, new_pass, confirm_pass]):
            st.error("❌ Semua field wajib diisi.")
        elif new_pass != confirm_pass:
            st.error("❌ Konfirmasi password tidak cocok.")
        elif len(new_pass) < 6:
            st.error("❌ Password baru minimal 6 karakter.")
        else:
            found = run_query_one(
                "SELECT id FROM users WHERE username=%s AND password=%s",
                (user["username"], hash_password(old_pass))
            )
            if not found:
                st.error("❌ Password lama salah.")
            else:
                ok = run_query(
                    "UPDATE users SET password=%s WHERE username=%s",
                    (hash_password(new_pass), user["username"]), fetch=False
                )
                if ok:
                    st.success("✅ Password berhasil diubah!")

    st.markdown('<div class="section-title">ℹ️ Informasi Akun</div>', unsafe_allow_html=True)
    info_data = {
        "Nama Lengkap":    user.get("nama_lengkap", "-"),
        "Username":        user.get("username", "-"),
        "Jabatan":         user.get("role", "-"),
        "Kota Tugas":      user.get("kota") or "-",
        "Kecamatan Tugas": user.get("kecamatan") or "-",
        "Kelurahan Tugas": user.get("kelurahan") or "-",
        "RW Tugas":        user.get("rw") or "-",
    }
    for k, v in info_data.items():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"**{k}**")
        with col2:
            st.markdown(v)

    # Ganti password dengan catat log
    if submit_pass:
        pass  # sudah ditangani di atas


# ============================================================
# HALAMAN AUDIT LOG (Admin Only)
# ============================================================
def page_audit_log():
    st.markdown("""
    <div class="main-header">
        <h1>📜 Audit Log Aktivitas</h1>
        <p>Rekam jejak semua aktivitas pengguna dalam sistem JAKDATA</p>
    </div>
    """, unsafe_allow_html=True)

    # Filter
    st.markdown('<div class="section-title">🔍 Filter Log</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_aksi = st.selectbox("Filter Aksi", [
            "Semua", "LOGIN_BERHASIL", "LOGIN_GAGAL",
            "LOGIN_GAGAL_TERKUNCI", "LOGOUT", "INPUT_WARGA"
        ])
    with col2:
        filter_user = st.text_input("Cari Username...")
    with col3:
        limit = st.selectbox("Tampilkan", [50, 100, 200, 500], index=0)

    # Query
    query = """
        SELECT created_at as "Waktu", username as "Username",
               nama as "Nama", aksi as "Aksi", detail as "Detail"
        FROM audit_log
        WHERE 1=1
    """
    params = []
    if filter_aksi != "Semua":
        query += " AND aksi=%s"
        params.append(filter_aksi)
    if filter_user:
        query += " AND username ILIKE %s"
        params.append(f"%{filter_user}%")
    query += f" ORDER BY created_at DESC LIMIT {limit}"

    rows = run_query(query, params if params else None)
    df_log = pd.DataFrame(rows) if rows else pd.DataFrame()

    if not df_log.empty:
        # Warna berdasarkan aksi
        def style_aksi(val):
            if "GAGAL" in str(val) or "TERKUNCI" in str(val):
                return "color: #c62828; font-weight: bold"
            elif "BERHASIL" in str(val):
                return "color: #2e7d32; font-weight: bold"
            return ""

        st.markdown(f'<span class="info-badge">📊 {len(df_log)} aktivitas ditemukan</span>',
                   unsafe_allow_html=True)
        st.markdown("")
        st.dataframe(df_log, use_container_width=True, hide_index=True, height=450)

        # Download
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_log.to_excel(writer, index=False, sheet_name="Audit Log")
        st.download_button(
            "📥 Download Audit Log",
            data=output.getvalue(),
            file_name=f"JAKDATA_AuditLog_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("📭 Belum ada aktivitas tercatat.")

    # Ringkasan
    st.markdown('<div class="section-title">📊 Ringkasan Aktivitas Hari Ini</div>',
               unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    stats = [
        ("LOGIN_BERHASIL", "✅ Login Berhasil", "#43a047"),
        ("LOGIN_GAGAL",    "❌ Login Gagal",    "#e53935"),
        ("LOGIN_GAGAL_TERKUNCI", "🔒 Akun Terkunci", "#f57f17"),
        ("INPUT_WARGA",   "📝 Input Warga",    "#1976d2"),
    ]
    for col, (aksi, label, warna) in zip([col1,col2,col3,col4], stats):
        r = run_query_one("""
            SELECT COUNT(*) FROM audit_log
            WHERE aksi=%s AND created_at >= NOW() - INTERVAL '24 hours'
        """, (aksi,))
        jumlah = int(list(r.values())[0]) if r else 0
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color:{warna};">
                <div class="metric-value" style="color:{warna};font-size:1.8rem;">{jumlah}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)


# ============================================================
# MAIN APP
# ============================================================
def main():
    init_db()

    if "user" not in st.session_state:
        page_login()
        return

    render_sidebar()

    page = st.session_state.get("page", "dashboard")
    user_role = st.session_state.get("user", {}).get("role", "")

    if page == "dashboard":
        page_dashboard()
    elif page == "input_warga":
        page_input_warga()
    elif page == "data_warga":
        page_data_warga()
    elif page == "manajemen_tim":
        if user_role == "Admin":
            page_manajemen_tim()
        else:
            st.error("🚫 Akses ditolak. Halaman ini hanya untuk Admin.")
    elif page == "audit_log":
        if user_role == "Admin":
            page_audit_log()
        else:
            st.error("🚫 Akses ditolak. Halaman ini hanya untuk Admin.")
    elif page == "pengaturan":
        page_pengaturan()
    else:
        page_dashboard()


if __name__ == "__main__":
    main()
