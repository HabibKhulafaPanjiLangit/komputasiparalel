# 📊 Cara Melihat Database - MPI Payroll System

## 📍 Dimana Database Disimpan?

### 🔹 Local Development (Komputer Anda)
- **File:** `payroll.db` (SQLite)
- **Lokasi:** `d:\mpi-demo\payroll.db`
- **Type:** SQLite database file

### 🔹 Production (Railway.app)
- **Type:** PostgreSQL
- **Provider:** Railway PostgreSQL Service
- **Connection:** Via environment variable `DATABASE_URL`

---

## 🛠️ Cara Lihat Database - 4 Metode

### ✅ 1. WEB DASHBOARD (Paling Mudah!)

#### Langkah:
1. Jalankan web server:
   ```bash
   python web_server.py
   ```
   
2. Buka browser: http://localhost:5000

3. Klik tab **"Database Browser"**

4. Klik tombol **"🔄 Refresh Database"**

5. Lihat semua table dengan data lengkap!

#### Screenshot:
```
┌─────────────────────────────────────────┐
│  Tab: Database Browser                  │
├─────────────────────────────────────────┤
│  📊 Database Information                │
│  Path: d:\mpi-demo\payroll.db          │
│  Size: 28 KB                            │
│  Tables: 3                              │
│                                         │
│  📁 KARYAWAN (1 records)               │
│  Columns: id, nama, jabatan, gaji_pokok│
│  ┌──────┬─────┬────────┬────────┐     │
│  │ id   │nama │jabatan │gaji    │     │
│  ├──────┼─────┼────────┼────────┤     │
│  │TEST01│Test │Tester  │500,000 │     │
│  └──────┴─────┴────────┴────────┘     │
└─────────────────────────────────────────┘
```

---

### ✅ 2. CLI TOOL (Command Line)

#### Metode A: Menggunakan BAT File
```bash
browse_db.bat
```

#### Metode B: Python Script Langsung
```bash
python browse_database.py
```

#### Output:
```
================================================================================
DATABASE BROWSER - MPI Payroll System
================================================================================
Database: payroll.db

[OK] Ditemukan 3 tables

--------------------------------------------------------------------------------
TABLE: KARYAWAN (1 records)
--------------------------------------------------------------------------------
+---------+-----------+-----------+--------------+
| id      | nama      | jabatan   | gaji_pokok   |
+=========+===========+===========+==============+
| TEST001 | Test User | Tester    | 500,000      |
+---------+-----------+-----------+--------------+
```

---

### ✅ 3. SQLITE BROWSER (GUI Tool)

#### Download & Install:
https://sqlitebrowser.org/

#### Langkah:
1. Download **DB Browser for SQLite**
2. Install aplikasi
3. Buka aplikasi
4. File → Open Database
5. Pilih: `d:\mpi-demo\payroll.db`
6. Lihat data di tab "Browse Data"

#### Screenshot:
```
┌────────────────────────────────────┐
│ DB Browser for SQLite              │
├────────────────────────────────────┤
│ File  Edit  View  Tools  Help      │
├────────────────────────────────────┤
│ Database Structure  Browse Data    │
│                                    │
│ Table: karyawan                    │
│ ┌─────────┬──────────┬──────────┐ │
│ │ id      │ nama     │ jabatan  │ │
│ ├─────────┼──────────┼──────────┤ │
│ │ TEST001 │Test User │ Tester   │ │
│ └─────────┴──────────┴──────────┘ │
└────────────────────────────────────┘
```

---

### ✅ 4. PYTHON CODE (Programmatic)

#### Quick Check:
```python
import sqlite3

# Connect to database
conn = sqlite3.connect('payroll.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", cursor.fetchall())

# Get karyawan data
cursor.execute("SELECT * FROM karyawan")
for row in cursor.fetchall():
    print(row)

conn.close()
```

#### Jalankan:
```bash
python -c "import sqlite3; conn = sqlite3.connect('payroll.db'); cursor = conn.cursor(); cursor.execute('SELECT * FROM karyawan'); print(cursor.fetchall())"
```

---

## 🌐 Production Database (Railway)

### 📋 Setup PostgreSQL di Railway:

#### 1. Add Database Service:
```
1. Buka Railway Dashboard: https://railway.app/dashboard
2. Pilih project: web-production-709f
3. Klik "+ New"
4. Pilih "Database"
5. Pilih "PostgreSQL"
6. Railway akan otomatis:
   - Create PostgreSQL instance
   - Set environment variable DATABASE_URL
   - Connect ke aplikasi Anda
```

#### 2. Verify Connection:
```
1. Di Railway Dashboard
2. Klik PostgreSQL service
3. Tab "Variables"
4. Lihat DATABASE_URL (otomatis ter-link ke web service)
```

#### 3. View Data di Railway:

##### Metode A: Railway Dashboard
```
1. Klik PostgreSQL service
2. Tab "Data"
3. Pilih table: karyawan, absen, gaji
4. Lihat semua records
```

##### Metode B: Railway CLI
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# Connect to database
railway run psql $DATABASE_URL

# Query
SELECT * FROM karyawan;
```

---

## 🔍 Database Structure

### Table: karyawan
```sql
CREATE TABLE karyawan (
    id VARCHAR PRIMARY KEY,
    nama VARCHAR NOT NULL,
    jabatan VARCHAR NOT NULL,
    gaji_pokok FLOAT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Table: absen
```sql
CREATE TABLE absen (
    id SERIAL PRIMARY KEY,
    karyawan_id VARCHAR NOT NULL,
    tanggal DATE NOT NULL,
    hadir BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    FOREIGN KEY (karyawan_id) REFERENCES karyawan(id)
);
```

### Table: gaji
```sql
CREATE TABLE gaji (
    id SERIAL PRIMARY KEY,
    karyawan_id VARCHAR NOT NULL,
    nama VARCHAR,
    jabatan VARCHAR,
    gaji_pokok FLOAT,
    hari_kerja INTEGER,
    total_gaji FLOAT,
    created_at TIMESTAMP,
    FOREIGN KEY (karyawan_id) REFERENCES karyawan(id)
);
```

---

## 📊 Query Examples

### Get All Employees:
```sql
SELECT * FROM karyawan;
```

### Get Employees with Attendance:
```sql
SELECT k.*, COUNT(a.id) as total_hadir
FROM karyawan k
LEFT JOIN absen a ON k.id = a.karyawan_id
GROUP BY k.id;
```

### Get Salary Calculation:
```sql
SELECT k.nama, k.jabatan, g.hari_kerja, g.total_gaji
FROM gaji g
JOIN karyawan k ON g.karyawan_id = k.id
ORDER BY g.total_gaji DESC;
```

### Get Statistics:
```sql
-- Total employees
SELECT COUNT(*) as total_karyawan FROM karyawan;

-- Average salary
SELECT AVG(total_gaji) as rata_rata_gaji FROM gaji;

-- By jabatan
SELECT jabatan, COUNT(*) as jumlah, AVG(gaji_pokok) as avg_gaji
FROM karyawan
GROUP BY jabatan;
```

---

## 🛡️ Database Management Tools

### For SQLite (Local):
1. **DB Browser for SQLite** - https://sqlitebrowser.org/
2. **SQLiteStudio** - https://sqlitestudio.pl/
3. **DBeaver** - https://dbeaver.io/

### For PostgreSQL (Railway):
1. **Railway Dashboard** - Built-in Data viewer
2. **pgAdmin** - https://www.pgadmin.org/
3. **DBeaver** - https://dbeaver.io/
4. **TablePlus** - https://tableplus.com/

---

## 🔗 Connection Strings

### Local SQLite:
```
sqlite:///payroll.db
```

### Railway PostgreSQL:
```
Otomatis dari environment variable:
DATABASE_URL=postgresql://user:password@host:port/database
```

---

## ⚙️ Environment Detection

Aplikasi otomatis detect environment:

```python
def get_database_url():
    # Production: PostgreSQL from DATABASE_URL
    if 'DATABASE_URL' in os.environ:
        return os.environ['DATABASE_URL']
    
    # Local: SQLite file
    return 'sqlite:///payroll.db'
```

**Local:** File `payroll.db` di folder project  
**Railway:** PostgreSQL dari DATABASE_URL environment variable

---

## 📝 Tips & Troubleshooting

### ✅ Check Database Exists:
```bash
# Windows
dir payroll.db

# Check dengan Python
python -c "import os; print('EXISTS' if os.path.exists('payroll.db') else 'NOT FOUND')"
```

### ✅ Check Database Size:
```bash
python -c "import os; print(f'Size: {os.path.getsize(\"payroll.db\")/1024:.2f} KB')"
```

### ✅ Backup Database:
```bash
# Copy file
copy payroll.db payroll_backup.db

# Export to SQL
sqlite3 payroll.db .dump > backup.sql
```

### ✅ Reset Database:
```bash
# Delete file (akan auto-create saat app run)
del payroll.db

# Or via Python
python -c "from database import init_db; init_db()"
```

---

## 🚀 Quick Start Commands

### Start Web Server & Browse Database:
```bash
# 1. Start server
python web_server.py

# 2. Open browser
start http://localhost:5000

# 3. Klik tab "Database Browser"
```

### Browse Database CLI:
```bash
# Quick browse
python browse_database.py

# Or use BAT file
browse_db.bat
```

### Check Database via Python:
```bash
python -c "from db_helper import *; print(get_all_karyawan())"
```

---

## 📞 Support

**GitHub Repo:**  
https://github.com/HabibKhulafaPanjiLangit/komputasiparalel

**Railway App:**  
https://web-production-709f.up.railway.app

**Documentation:**
- `DATABASE.md` - Database schema & setup
- `DEPLOY.md` - Deployment guide
- `README.md` - General info
