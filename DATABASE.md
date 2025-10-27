# 💾 Database - Persistent Storage

## ✅ Yang Sudah Ditambahkan:

### **1. Database Module** (`database.py`)
- SQLAlchemy ORM models
- Auto-detect PostgreSQL atau SQLite
- 3 tables: `karyawan`, `absen`, `gaji`
- Auto-create tables on startup

### **2. Database Helper** (`db_helper.py`)
- Wrapper functions untuk semua operasi
- Fallback ke in-memory jika database tidak tersedia
- Functions:
  - `get_all_karyawan()`
  - `add_karyawan(id, nama, jabatan, gaji_pokok)`
  - `delete_karyawan(id)`
  - `get_all_absen()`
  - `add_absen(id, hari_masuk)`
  - `get_all_gaji()`
  - `clear_and_save_gaji(data, mode, waktu)`
  - `generate_dummy_data(jumlah)`

### **3. Dependencies**
```txt
sqlalchemy==1.4.50        # ORM untuk database
psycopg2-binary==2.9.9    # PostgreSQL driver
python-dotenv==1.0.0      # Environment variables
```

---

## 🎯 Cara Kerja:

### **Lokal Development:**
```python
# Otomatis gunakan SQLite
DATABASE_URL = 'sqlite:///payroll.db'
```
- ✅ File database: `payroll.db` (di folder project)
- ✅ Persistent di local
- ✅ Tidak perlu setup database server

### **Production (Railway/Render):**
```python
# Auto-detect dari environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')
# postgresql+psycopg2://user:pass@host:port/dbname
```
- ✅ Railway auto-provide PostgreSQL
- ✅ Render juga support PostgreSQL gratis
- ✅ Data persistent, tidak hilang saat restart

---

## 📊 Database Schema:

### **Table: karyawan**
```sql
id VARCHAR(50) PRIMARY KEY
nama VARCHAR(100) NOT NULL
jabatan VARCHAR(50) NOT NULL
gaji_pokok FLOAT NOT NULL
created_at DATETIME
updated_at DATETIME
```

### **Table: absen**
```sql
id VARCHAR(50) PRIMARY KEY
hari_masuk INTEGER NOT NULL
created_at DATETIME
updated_at DATETIME
```

### **Table: gaji**
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
karyawan_id VARCHAR(50) NOT NULL
nama VARCHAR(100) NOT NULL
jabatan VARCHAR(50) NOT NULL
gaji_pokok FLOAT NOT NULL
hari_masuk INTEGER NOT NULL
total_gaji FLOAT NOT NULL
mode_hitung VARCHAR(20)  -- 'serial' atau 'parallel'
waktu_hitung FLOAT       -- waktu eksekusi
created_at DATETIME
```

---

## 🚀 Setup di Railway:

### **Step 1: Deploy App**
(Sudah explained di DEPLOY.md)

### **Step 2: Add PostgreSQL**
1. Dashboard Railway → klik project Anda
2. Klik **"New"** → **"Database"** → **"PostgreSQL"**
3. Railway auto-create database
4. Environment variable `DATABASE_URL` otomatis di-set
5. **Restart app** (redeploy)

### **Step 3: Verify**
```bash
# Logs akan menampilkan:
[DB] Database initialized: postgresql+psycopg2://....
```

Done! Data sekarang persistent di PostgreSQL! 🎉

---

## 🔧 Environment Variables:

Railway/Render akan auto-set:
```bash
DATABASE_URL=postgresql://user:pass@host:port/dbname
PORT=5000
```

Untuk local, buat file `.env`:
```bash
# Opsional, default gunakan SQLite
DATABASE_URL=sqlite:///payroll.db
PORT=5000
```

---

## ✨ Keuntungan Database:

| Aspek | Sebelum (RAM) | Setelah (Database) |
|-------|--------------|-------------------|
| **Persistent** | ❌ Hilang saat restart | ✅ Tersimpan permanent |
| **Multi-user** | ⚠️ Conflict possible | ✅ ACID transactions |
| **Backup** | ❌ Manual | ✅ Auto backup |
| **Query** | ⚠️ Loop manual | ✅ SQL queries |
| **Scalability** | ❌ RAM limited | ✅ Unlimited storage |

---

## 📝 Testing Database:

```python
# Test koneksi
from database import init_db, Karyawan

engine, Session = init_db()
session = Session()

# Add test data
karyawan = Karyawan(
    id="K001",
    nama="John Doe",
    jabatan="Manager",
    gaji_pokok=10000000
)
session.add(karyawan)
session.commit()

# Query
all_karyawan = session.query(Karyawan).all()
print(f"Total karyawan: {len(all_karyawan)}")

session.close()
```

---

## 🆘 Troubleshooting:

**Error: No module named 'psycopg2'**
```bash
pip install psycopg2-binary
```

**Error: No module named 'sqlalchemy'**
```bash
pip install sqlalchemy==1.4.50
```

**Database not found (local)**
- Check file `payroll.db` ada di folder project
- Akan auto-create saat pertama kali run

**Connection error (production)**
- Pastikan PostgreSQL sudah ditambahkan di Railway/Render
- Check environment variable `DATABASE_URL` sudah di-set
- Restart app setelah add database

---

## 🎯 Next Steps:

1. ✅ **Deploy ke Railway** - Database auto-configured
2. ✅ **Add PostgreSQL** di Railway dashboard  
3. ✅ **Test persistence** - Add data, restart app, data masih ada!
4. ⏭️ **Optional**: Add backup/restore features
5. ⏭️ **Optional**: Add data migration tools

---

**Database is Ready! 🚀**

Semua perubahan sudah di-push ke GitHub.
Tinggal deploy dan add PostgreSQL di Railway!
