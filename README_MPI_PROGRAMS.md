# Ringkasan Program MPI yang Telah Dibuat

## Program-Program yang Berhasil:

### 1. **pi_montecarlo_mpi.py** - Monte Carlo Pi Calculation
**Deskripsi:** Menghitung nilai Pi menggunakan metode Monte Carlo dengan paralelisasi MPI

**Hasil Benchmark:**
- 100,000 titik: Speedup **4.81x** (4 proses)
- 1,000,000 titik: Speedup **3.98x** (4 proses)
- 10,000,000 titik: Error hanya **0.0001854536**

**Fitur Utama:**
- MPI Reduction (MPI.SUM) untuk mengumpulkan hasil
- Distribusi pekerjaan otomatis ke semua proses
- Perbandingan serial vs parallel

**Cara Menjalankan:**
```bash
mpiexec -n 4 python pi_montecarlo_mpi.py
```

---

### 2. **payroll_mpi.py** - Sistem Penggajian Karyawan (OOP)
**Deskripsi:** Sistem penggajian dengan pendekatan Object-Oriented menggunakan MPI

**Fitur:**
- Class `PayrollSystemMPI` dengan dataclass `Employee`
- Fungsi calculate_all_salaries_parallel() dan calculate_all_salaries_serial()
- Support CSV import/export
- Menu interaktif untuk manajemen karyawan

**Cara Menjalankan:**
```bash
mpiexec -n 4 python payroll_mpi.py
```

---

### 3. **payroll_full_mpi.py** - Program Penggajian Lengkap
**Deskripsi:** Sistem penggajian dengan menu interaktif lengkap

**Menu:**
1. Input Data Karyawan
2. Input Data Absen
3. Hitung Gaji (Serial)
4. Hitung Gaji (Parallel - MPI)
5. Tampilkan Data Gaji
6. Keluar
7. Simpan ke CSV
8. Muat dari CSV
9. Tampilkan Perbandingan Waktu
10. Input Data Otomatis (testing)
11. Demo Otomatis (Benchmark)

**Cara Menjalankan:**
```bash
mpiexec -n 4 python payroll_full_mpi.py
```

---

### 4. **demo_payroll_mpi.py** - Demo Otomatis Payroll
**Deskripsi:** Demo otomatis untuk menampilkan perbandingan serial vs parallel

**Output:**
- Generate 10,000 karyawan otomatis
- Hitung gaji serial dan parallel
- Tampilkan 10 karyawan pertama sebagai sample

**Cara Menjalankan:**
```bash
mpiexec -n 4 python demo_payroll_mpi.py
```

---

### 5. **demo_payroll_benchmark.py** - Benchmark Sederhana
**Deskripsi:** Benchmark dengan perhitungan sederhana (hanya perkalian)

**Test Size:** 1,000 - 50,000 karyawan

**Hasil:** 
- Menunjukkan bahwa untuk komputasi ringan, overhead MPI > keuntungan
- Average Speedup: 0.32x (overhead dominan)

**Cara Menjalankan:**
```bash
mpiexec -n 4 python demo_payroll_benchmark.py
```

---

### 6. **demo_payroll_complex.py** - Benchmark dengan Komputasi Kompleks ⭐
**Deskripsi:** Benchmark dengan perhitungan pajak yang CPU-intensive

**Hasil Benchmark:**
- 100 karyawan: Speedup **3.00x** (Efisiensi 74.9%)
- 500 karyawan: Speedup **3.10x** (Efisiensi 77.6%)
- 1,000 karyawan: Speedup **3.76x** (Efisiensi 94.1%) 🏆
- 2,000 karyawan: Speedup **3.49x** (Efisiensi 87.2%)

**Rata-rata:** Speedup **3.34x** dengan efisiensi **83.4%**

**Fitur Perhitungan:**
- Gaji pokok + lembur + tunjangan + bonus
- Perhitungan pajak progresif dengan simulasi CPU-intensive
- 1000 iterasi komputasi matematika per karyawan

**Cara Menjalankan:**
```bash
mpiexec -n 4 python demo_payroll_complex.py
```

---

## Konsep MPI yang Digunakan:

### 1. **Basic Communication**
- `comm.send()` - Mengirim data ke proses lain
- `comm.recv()` - Menerima data dari proses lain
- `comm.bcast()` - Broadcast data ke semua proses

### 2. **Collective Operations**
- `comm.reduce()` - Reduce operation (SUM, MAX, MIN, dll)
- Distribusi data dengan scatter pattern manual

### 3. **Work Distribution**
```python
# Pembagian kerja merata
karyawan_per_process = total // size
remainder = total % size

# Proses awal dapat sisa jika ada
if rank < remainder:
    local_count = karyawan_per_process + 1
else:
    local_count = karyawan_per_process
```

### 4. **Rank 0 Pattern**
- Rank 0 sebagai master/coordinator
- Rank 0 mengumpulkan dan menampilkan hasil akhir
- Worker processes (rank 1-n) hanya melakukan komputasi

---

## Perbedaan dengan OpenMP:

| Aspek | OpenMP | MPI |
|-------|--------|-----|
| **Model** | Shared Memory | Distributed Memory |
| **Threads/Processes** | Threads | Processes |
| **Skalabilitas** | Single Machine | Multiple Machines (Cluster) |
| **Komunikasi** | Memory Sharing | Message Passing |
| **Overhead** | Rendah | Sedang-Tinggi |
| **Use Case** | CPU-intensive, single node | Large-scale, distributed computing |

---

## Kesimpulan:

✅ **MPI Sangat Efektif Untuk:**
- Komputasi yang CPU-intensive (contoh: pajak kompleks = 3.34x speedup)
- Dataset besar yang bisa dibagi-bagi
- Aplikasi yang bisa di-scale ke cluster

❌ **MPI Kurang Efektif Untuk:**
- Komputasi sangat ringan (overhead > benefit)
- Dataset kecil
- Operasi yang membutuhkan banyak komunikasi antar proses

🎯 **Best Practice:**
- Maksimalkan komputasi per proses
- Minimalkan komunikasi antar proses
- Gunakan MPI untuk problem yang "embarrassingly parallel"

---

## File Tambahan:

- `send_recv.py` - Contoh dasar MPI send/receive
- `hello_mpi.py` - Hello World dengan MPI
- `payroll_openmp.py` - Versi OpenMP untuk perbandingan

---

**Semua program sudah diperbaiki dan berjalan tanpa error Unicode!** ✓
