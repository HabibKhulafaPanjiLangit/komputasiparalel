# 🌐 MPI Payroll System - Web Dashboard

Dashboard berbasis web untuk menjalankan dan monitoring program MPI secara real-time melalui browser.

## 📋 Fitur

- ✅ **Web Interface** - Jalankan program MPI melalui browser
- ✅ **Real-time Status** - Monitor program yang sedang berjalan
- ✅ **Benchmark Results** - Lihat hasil komputasi serial vs parallel
- ✅ **Multiple Processes** - Pilih jumlah proses MPI (2, 4, 8, 16)
- ✅ **History Log** - Simpan semua hasil benchmark
- ✅ **Responsive Design** - Tampilan modern dan mobile-friendly

## 🚀 Cara Menggunakan

### 1. Install Dependencies

```bash
# Install Flask
pip install flask

# Atau install dari requirements.txt
pip install -r requirements.txt
```

### 2. Jalankan Web Server

```bash
python web_server.py
```

### 3. Buka Browser

Akses dashboard di: **http://localhost:5000**

## 📱 Tampilan Dashboard

Dashboard menampilkan:
- **Status Bar** - Menunjukkan program yang sedang berjalan
- **Program Cards** - Pilihan program MPI yang tersedia
- **Process Selector** - Pilih jumlah proses MPI (2-16)
- **Results Section** - Hasil benchmark dengan output lengkap

## 🎯 Program yang Tersedia

### 1. Monte Carlo Pi Calculation
- **File**: `pi_montecarlo_mpi.py`
- **Speedup**: 4.81x (4 proses)
- **Deskripsi**: Menghitung nilai Pi dengan metode Monte Carlo

### 2. Demo Payroll Otomatis
- **File**: `demo_payroll_mpi.py`
- **Deskripsi**: Demo sistem penggajian 10,000 karyawan

### 3. Benchmark Payroll Kompleks
- **File**: `demo_payroll_complex.py`
- **Speedup**: 3.34x (4 proses)
- **Deskripsi**: Perhitungan gaji dengan pajak CPU-intensive

### 4. Benchmark Payroll Sederhana
- **File**: `demo_payroll_benchmark.py`
- **Speedup**: 0.33x (overhead dominan)
- **Deskripsi**: Perhitungan gaji sederhana

## 🔌 API Endpoints

### GET /api/programs
Mendapatkan daftar program MPI yang tersedia

**Response:**
```json
[
  {
    "id": "pi_montecarlo",
    "name": "Monte Carlo Pi Calculation",
    "file": "pi_montecarlo_mpi.py",
    "description": "...",
    "expected_speedup": "4.81x"
  }
]
```

### POST /api/run/<program_id>
Menjalankan program MPI

**Request Body:**
```json
{
  "processes": 4
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "timestamp": "2025-10-23T...",
    "program_id": "pi_montecarlo",
    "num_processes": 4,
    "elapsed_time": 2.35,
    "output": "...",
    "success": true
  }
}
```

### GET /api/status
Mendapatkan status program yang sedang berjalan

**Response:**
```json
{
  "running": true,
  "program": "pi_montecarlo",
  "start_time": 1234567890,
  "elapsed": 5.2
}
```

### GET /api/results
Mendapatkan hasil benchmark sebelumnya

### POST /api/results/clear
Menghapus semua hasil benchmark

## 💡 Tips Penggunaan

1. **Pilih Jumlah Proses**
   - 2 proses: Untuk testing cepat
   - 4 proses: Optimal untuk laptop/PC biasa
   - 8-16 proses: Untuk komputer dengan banyak core

2. **Monitor Status**
   - Status bar akan menunjukkan program yang sedang berjalan
   - Elapsed time ditampilkan real-time

3. **Lihat Hasil**
   - Hasil otomatis tersimpan di section bawah
   - Klik "Hapus Semua Hasil" untuk clear history

## 🛠️ Troubleshooting

### Port 5000 sudah digunakan
```bash
# Edit web_server.py, ganti port di baris terakhir:
app.run(debug=True, host='0.0.0.0', port=8000)
```

### Program tidak berjalan
- Pastikan MPI sudah terinstall: `mpiexec --version`
- Pastikan file .py ada di direktori yang sama
- Cek error di terminal server

### Browser tidak bisa akses
- Pastikan firewall tidak memblokir port 5000
- Coba akses http://127.0.0.1:5000

## 📊 Contoh Output

Setelah menjalankan program, dashboard akan menampilkan:
- Waktu eksekusi
- Jumlah proses yang digunakan
- Output lengkap dari program (termasuk speedup)
- Status success/error

## 🔒 Keamanan

⚠️ **PERINGATAN**: Web server ini untuk development/demo saja!

Jangan gunakan di production tanpa:
- Authentication
- Rate limiting
- Input validation
- HTTPS/SSL

## 📝 Lisensi

Demo project untuk pembelajaran MPI dan parallel computing.

---

**Developed with ❤️ for MPI Learning**
