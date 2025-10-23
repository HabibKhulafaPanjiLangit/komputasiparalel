from mpi4py import MPI  # type: ignore
import time
import csv
import os

# Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Data global (hanya rank 0 yang menyimpan data lengkap)
data_karyawan = []
data_absen = []
data_gaji = []

# Simpan waktu eksekusi
serial_times = []
parallel_times = []
jumlah_data = []

# -------------------------------
# Fungsi bantu CSV
# -------------------------------
def simpan_ke_csv(nama_file, data, fieldnames):
    if rank != 0:
        return
    
    with open(nama_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f">> Data berhasil disimpan ke '{nama_file}'")

def muat_dari_csv(nama_file):
    if rank != 0:
        return []
    
    if not os.path.exists(nama_file):
        print(f"    File '{nama_file}' tidak ditemukan.")
        return []
    with open(nama_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)

# -------------------------------
# Input Data
# -------------------------------
def input_karyawan():
    global data_karyawan
    
    if rank != 0:
        return
    
    n = int(input("Masukkan jumlah karyawan: "))
    data_karyawan = []
    
    for i in range(n):
        print(f"\nData karyawan ke-{i+1}")
        idk = input("ID Karyawan: ")
        nama = input("Nama Karyawan: ")
        jabatan = input("Jabatan: ")

        while True:
            try:
                gaji_pokok = float(input("Gaji Pokok per Hari: "))
                break
            except ValueError:
                print("     Input tidak valid! Masukkan angka, contoh: 150000")

        data_karyawan.append({
            "id": idk,
            "nama": nama,
            "jabatan": jabatan,
            "gaji_pokok": gaji_pokok
        })
    print(">> Data karyawan berhasil disimpan.")

def input_karyawan_otomatis(jumlah):
    """Generate data karyawan otomatis untuk testing"""
    global data_karyawan
    
    if rank != 0:
        return
    
    data_karyawan = []
    jabatan_list = ["Manager", "Staff", "Supervisor", "Admin", "Developer"]
    
    for i in range(jumlah):
        data_karyawan.append({
            "id": f"K{i+1:04d}",
            "nama": f"Karyawan {i+1}",
            "jabatan": jabatan_list[i % len(jabatan_list)],
            "gaji_pokok": 150000 + (i % 5) * 50000
        })
    print(f">> {jumlah} data karyawan berhasil dibuat secara otomatis.")

# -------------------------------
# Input Absen
# -------------------------------
def input_absen():
    global data_absen
    
    if rank != 0:
        return
    
    if not data_karyawan:
        print("     Input data karyawan terlebih dahulu!")
        return

    data_absen = []
    for karyawan in data_karyawan:
        print(f"\nAbsen untuk {karyawan['nama']}")
        while True:
            try:
                hari_masuk = int(input("Jumlah Hari Masuk: "))
                break
            except ValueError:
                print("     Masukkan angka yang valid!")

        data_absen.append({
            "id": karyawan["id"],
            "hari_masuk": hari_masuk
        })
    print(">> Data absen berhasil disimpan.")

def input_absen_otomatis():
    """Generate data absen otomatis untuk testing"""
    global data_absen
    
    if rank != 0:
        return
    
    if not data_karyawan:
        print("     Input data karyawan terlebih dahulu!")
        return
    
    data_absen = []
    import random
    for karyawan in data_karyawan:
        data_absen.append({
            "id": karyawan["id"],
            "hari_masuk": random.randint(20, 26)  # 20-26 hari kerja per bulan
        })
    print(">> Data absen otomatis berhasil dibuat.")

# -------------------------------
# Hitung Gaji (Serial)
# -------------------------------
def hitung_gaji_serial():
    global data_gaji
    
    if rank != 0:
        return
    
    if not data_absen:
        print("     Input data absen terlebih dahulu!")
        return

    data_gaji = []
    start = time.perf_counter()
    
    for i, k in enumerate(data_karyawan):
        hari_masuk = int(data_absen[i]["hari_masuk"])
        total = float(k["gaji_pokok"]) * hari_masuk
        data_gaji.append({
            "id": k["id"],
            "nama": k["nama"],
            "total_gaji": total
        })
    
    end = time.perf_counter()
    elapsed = end - start
    serial_times.append(elapsed)
    jumlah_data.append(len(data_karyawan))
    
    print(f">> Gaji berhasil dihitung secara SERIAL dalam {elapsed:.6f} detik.")
    print(f"   Total karyawan: {len(data_karyawan)}")

# -------------------------------
# Hitung Gaji (Parallel MPI)
# -------------------------------
def hitung_gaji_parallel():
    global data_gaji
    
    if rank == 0:
        if not data_absen:
            print("     Input data absen terlebih dahulu!")
            # Broadcast signal untuk tidak ada pekerjaan
            for i in range(1, size):
                comm.send(None, dest=i, tag=0)
            return
        
        print(f">> Menghitung gaji secara paralel dengan {size} proses MPI...")
        start = time.perf_counter()
        
        # Bagi pekerjaan ke semua proses
        num_karyawan = len(data_karyawan)
        karyawan_per_process = num_karyawan // size
        remainder = num_karyawan % size
        
        # Distribusi data ke worker processes
        start_idx = 0
        for i in range(size):
            count = karyawan_per_process + (1 if i < remainder else 0)
            end_idx = start_idx + count
            
            if i == 0:
                # Rank 0 memproses bagiannya sendiri
                local_karyawan = data_karyawan[start_idx:end_idx]
                local_absen = data_absen[start_idx:end_idx]
            else:
                # Kirim ke worker processes
                chunk_karyawan = data_karyawan[start_idx:end_idx]
                chunk_absen = data_absen[start_idx:end_idx]
                comm.send((chunk_karyawan, chunk_absen), dest=i, tag=0)
            
            start_idx = end_idx
        
        # Rank 0 memproses bagiannya
        local_gaji = []
        for i, k in enumerate(local_karyawan):
            hari_masuk = int(local_absen[i]["hari_masuk"])
            total = float(k["gaji_pokok"]) * hari_masuk
            local_gaji.append({
                "id": k["id"],
                "nama": k["nama"],
                "total_gaji": total
            })
        
        # Kumpulkan hasil dari semua worker processes
        all_results = [local_gaji]
        for i in range(1, size):
            results = comm.recv(source=i, tag=1)
            all_results.append(results)
        
        # Gabungkan semua hasil
        data_gaji = []
        for result_chunk in all_results:
            data_gaji.extend(result_chunk)
        
        end = time.perf_counter()
        elapsed = end - start
        parallel_times.append(elapsed)
        jumlah_data.append(len(data_karyawan))
        
        print(f">> Gaji berhasil dihitung secara PARALEL (MPI) dalam {elapsed:.6f} detik.")
        print(f"   Total karyawan: {len(data_karyawan)}")
        print(f"   Proses MPI: {size}")
        
    else:
        # Worker processes
        data_chunk = comm.recv(source=0, tag=0)
        
        if data_chunk is None:
            return  # Tidak ada pekerjaan
        
        chunk_karyawan, chunk_absen = data_chunk
        
        # Proses data
        local_gaji = []
        for i, k in enumerate(chunk_karyawan):
            hari_masuk = int(chunk_absen[i]["hari_masuk"])
            total = float(k["gaji_pokok"]) * hari_masuk
            local_gaji.append({
                "id": k["id"],
                "nama": k["nama"],
                "total_gaji": total
            })
        
        # Kirim hasil kembali ke rank 0
        comm.send(local_gaji, dest=0, tag=1)

# -------------------------------
# Tampilkan Data Gaji
# -------------------------------
def tampilkan_gaji():
    if rank != 0:
        return
    
    if not data_gaji:
        print("     Belum ada data gaji yang dihitung.")
        return

    print("\n=== DATA GAJI KARYAWAN ===")
    for g in data_gaji:
        print(f"ID: {g['id']}\tNama: {g['nama']}\tTotal Gaji: Rp {float(g['total_gaji']):,.2f}")

# -------------------------------
# Simpan & Muat Data CSV
# -------------------------------
def simpan_semua_data():
    if rank != 0:
        return
    
    simpan_ke_csv("karyawan.csv", data_karyawan, ["id", "nama", "jabatan", "gaji_pokok"])
    simpan_ke_csv("absen.csv", data_absen, ["id", "hari_masuk"])
    simpan_ke_csv("gaji.csv", data_gaji, ["id", "nama", "total_gaji"])

def muat_semua_data():
    global data_karyawan, data_absen, data_gaji
    
    if rank != 0:
        return
    
    data_karyawan = muat_dari_csv("karyawan.csv")
    data_absen = muat_dari_csv("absen.csv")
    data_gaji = muat_dari_csv("gaji.csv")
    print(">> Semua data berhasil dimuat dari file CSV.")

# -------------------------------
# Tampilkan Perbandingan Waktu
# -------------------------------
def tampilkan_perbandingan():
    if rank != 0:
        return
    
    if not serial_times or not parallel_times:
        print("     Belum ada data perbandingan waktu eksekusi!")
        print("Silakan jalankan perhitungan serial dan paralel terlebih dahulu.")
        return

    print("\n=== HASIL PERBANDINGAN WAKTU EKSEKUSI ===")
    print(f"{'Jumlah Data':<15} {'Serial (s)':<15} {'Parallel (s)':<15} {'Speedup':<10}")
    print("-" * 60)
    
    for i in range(min(len(serial_times), len(parallel_times))):
        speedup = serial_times[i] / parallel_times[i] if parallel_times[i] != 0 else 0
        print(f"{jumlah_data[i]:<15} {serial_times[i]:<15.6f} {parallel_times[i]:<15.6f} {speedup:<10.2f}x")
    
    print("-" * 60)

# -------------------------------
# Demo Otomatis
# -------------------------------
def demo_otomatis():
    if rank == 0:
        print("\n=== DEMO OTOMATIS: PERBANDINGAN SERIAL VS PARALLEL ===")
        
        test_sizes = [1000, 5000, 10000]
        
        for size_test in test_sizes:
            print(f"\n>> Testing dengan {size_test} karyawan...")
            input_karyawan_otomatis(size_test)
            input_absen_otomatis()
            
            # Test serial
            hitung_gaji_serial()
            
            # Broadcast data untuk parallel test
            comm.bcast(None, root=0)  # Signal untuk memulai parallel
    else:
        test_sizes = [1000, 5000, 10000]
        for _ in test_sizes:
            comm.bcast(None, root=0)
    
    # Test parallel
    if rank == 0:
        for _ in test_sizes:
            hitung_gaji_parallel()
    else:
        for _ in test_sizes:
            hitung_gaji_parallel()
    
    if rank == 0:
        tampilkan_perbandingan()

# -------------------------------
# Menu utama
# -------------------------------
def menu():
    while True:
        if rank == 0:
            print("\n=== MENU PENGHITUNGAN GAJI KARYAWAN (MPI) ===")
            print("1. Input Data Karyawan")
            print("2. Input Data Absen")
            print("3. Hitung Gaji (Serial)")
            print("4. Hitung Gaji (Parallel - MPI)")
            print("5. Tampilkan Data Gaji")
            print("6. Keluar")
            print("7. Simpan Semua Data ke File CSV")
            print("8. Muat Data dari File CSV")
            print("9. Tampilkan Perbandingan Waktu")
            print("10. Input Data Otomatis (untuk testing)")
            print("11. Demo Otomatis (Benchmark)")
            print(f"\nINFO: Running dengan {size} proses MPI")
            pilihan = input("Pilih menu (1-11): ")
        else:
            pilihan = None
        
        # Broadcast pilihan ke semua proses
        pilihan = comm.bcast(pilihan, root=0)

        if pilihan == "1":
            input_karyawan()
        elif pilihan == "2":
            input_absen()
        elif pilihan == "3":
            hitung_gaji_serial()
        elif pilihan == "4":
            hitung_gaji_parallel()
        elif pilihan == "5":
            tampilkan_gaji()
        elif pilihan == "6":
            if rank == 0:
                print("Program selesai.")
            break
        elif pilihan == "7":
            simpan_semua_data()
        elif pilihan == "8":
            muat_semua_data()
        elif pilihan == "9":
            tampilkan_perbandingan()
        elif pilihan == "10":
            if rank == 0:
                jumlah = int(input("Jumlah karyawan yang akan dibuat: "))
                input_karyawan_otomatis(jumlah)
                input_absen_otomatis()
        elif pilihan == "11":
            demo_otomatis()
        else:
            if rank == 0:
                print("Pilihan tidak valid!")

# -------------------------------
# Jalankan Program
# -------------------------------
if __name__ == "__main__":
    menu()
