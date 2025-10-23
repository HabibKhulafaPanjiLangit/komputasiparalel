# MPI Payroll System - Komputasi Paralel

Sistem penggajian karyawan berbasis **MPI (Message Passing Interface)** dengan web dashboard untuk input data manual dan benchmark komputasi paralel.

## 🚀 Fitur Utama

### 1. **Web Dashboard**
- Interface modern untuk input data karyawan dan absensi
- Perhitungan gaji mode Serial dan Parallel
- Export hasil ke CSV
- Real-time status monitoring

### 2. **Program MPI**
- `pi_montecarlo_mpi.py` - Perhitungan Pi dengan Monte Carlo
- `demo_payroll_mpi.py` - Demo sistem payroll dasar
- `demo_payroll_complex.py` - Payroll dengan perhitungan kompleks
- `payroll_mpi.py` - Sistem OOP payroll
- `collectives.py` - Demo MPI collectives
- Dan program lainnya...

### 3. **Benchmark Performance**
- Perbandingan kecepatan Serial vs Parallel
- Speedup ratio dan efficiency metrics
- Hasil tersimpan dalam format CSV dan Markdown

## 📋 Requirements

```
Python 3.14+
mpi4py
Flask 3.1.2
```

## 🔧 Instalasi

1. **Clone repository**
```bash
git clone https://github.com/HabibKhulafaPanjiLangit/komputasiparalel.git
cd komputasiparalel
```

2. **Buat virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## 🎯 Cara Menggunakan

### Jalankan Web Dashboard

```bash
python web_server.py
```

Akses di browser: **http://localhost:5000**

### Jalankan Program MPI (Command Line)

```bash
# Contoh: Monte Carlo Pi
mpiexec -n 4 python pi_montecarlo_mpi.py

# Contoh: Payroll Complex
mpiexec -n 4 python demo_payroll_complex.py
```

## 📊 Web Dashboard - Panduan

### Tab "Data Karyawan"
1. Isi form untuk menambah karyawan (ID, Nama, Jabatan, Gaji Pokok)
2. Tambahkan data absensi (pilih karyawan, input hari masuk)
3. Klik **"Hitung (Serial)"** atau **"Hitung (Parallel)"**

### Tab "Benchmark MPI"
- Klik program MPI yang tersedia untuk menjalankan benchmark
- Lihat status real-time dan hasil output

### Tab "Hasil Gaji"
- Lihat tabel hasil perhitungan gaji
- Total gaji semua karyawan
- Export ke CSV

## 🧪 Hasil Benchmark

### Pi Monte Carlo (10 juta titik)
- **Speedup**: 4.81x dengan 4 proses
- **Error**: 0.0001854536

### Payroll Complex (1000 karyawan)
- **Average Speedup**: 3.34x
- **Efficiency**: 94.1%

## 📁 Struktur Project

```
mpi-demo/
├── web_server.py          # Flask backend
├── templates/
│   └── index.html         # Web dashboard
├── static/
│   ├── style.css          # Styling
│   └── app.js             # JavaScript
├── pi_montecarlo_mpi.py   # Program MPI
├── demo_payroll_*.py      # Variasi payroll
├── requirements.txt       # Dependencies
└── README.md             # Dokumentasi
```

## 🛠️ Technology Stack

- **Python 3.14** - Bahasa pemrograman
- **MPI4Py** - Message Passing Interface untuk komputasi paralel
- **Flask** - Web framework
- **HTML/CSS/JavaScript** - Frontend

## 📝 API Endpoints

- `GET /api/programs` - Daftar program MPI
- `POST /api/run/<program>` - Jalankan program
- `GET /api/status` - Status eksekusi
- `GET /api/karyawan` - Daftar karyawan
- `POST /api/karyawan` - Tambah karyawan
- `POST /api/absen` - Tambah absensi
- `POST /api/gaji/hitung` - Hitung gaji
- `GET /api/data/export` - Export CSV

## 👨‍💻 Author

**Habib Khulafa Panji Langit**
- GitHub: [@HabibKhulafaPanjiLangit](https://github.com/HabibKhulafaPanjiLangit)

## 📄 License

MIT License - bebas digunakan untuk pembelajaran dan pengembangan.

---

**⚡ Komputasi Paralel - Meningkatkan performa dengan MPI!**
