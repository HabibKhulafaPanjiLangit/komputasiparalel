import random
from dataclasses import dataclass
from typing import List

try:
    from omp4py import omp, omp_set_num_threads  # type: ignore
    HAS_OMP = True
except ImportError:
    print("Warning: omp4py not installed. Running in sequential mode.")
    HAS_OMP = False
    def omp(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def omp_set_num_threads(n):
        pass

# Set number of threads
if HAS_OMP:
    omp_set_num_threads(4)
# ===============================
# PROGRAM PENGHITUNGAN GAJI PARALEL (OpenMP/Serial)
# ===============================
import time
import csv
import os
import matplotlib.pyplot as plt

# Coba import omp4py
try:
    from omp4py import omp
    omp_enabled = True
except Exception:
    omp_enabled = False
    omp = None

# -------------------------------
# Data global
# -------------------------------
data_karyawan = []
data_absen = []
data_gaji = []

serial_times = []
parallel_times = []
jumlah_data = []

# -------------------------------
# Fungsi bantu CSV
# -------------------------------
def simpan_ke_csv(nama_file, data, fieldnames):
    with open(nama_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Data berhasil disimpan ke '{nama_file}'")

def muat_dari_csv(nama_file):
    if not os.path.exists(nama_file):
        print(f"    File '{nama_file}' tidak ditemukan.")
        return []
    with open(nama_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)

# -------------------------------
# Menu utama
# -------------------------------
def menu():
    while True:
        print("\n=== MENU PENGHITUNGAN GAJI KARYAWAN ===")
        print("1. Input Data Karyawan")
        print("2. Input Data Absen")
        print("3. Hitung Gaji (Serial)")
        print("4. Hitung Gaji (Parallel - OpenMP)")
        print("5. Tampilkan Data Gaji")
        print("6. Keluar")
        print("7. Simpan Semua Data ke File CSV")
        print("8. Muat Data dari File CSV")
        print("9. Tampilkan Grafik Perbandingan Waktu")

        pilihan = input("Pilih menu (1-9): ")

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
            print("Program selesai.")
            break
        elif pilihan == "7":
            simpan_semua_data()
        elif pilihan == "8":
            muat_semua_data()
        elif pilihan == "9":
            tampilkan_grafik()
        else:
            print("Pilihan tidak valid!")

# -------------------------------
# Input Data
# -------------------------------
def input_karyawan():
    try:
        n = int(input("Masukkan jumlah karyawan: "))
    except ValueError:
        print("Input tidak valid!")
        return
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
    print("✅ Data karyawan berhasil disimpan.")

# -------------------------------
# Input Absen
# -------------------------------
def input_absen():
    if not data_karyawan:
        print("     Input data karyawan terlebih dahulu!")
        return
    data_absen.clear()
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
    print("✅ Data absen berhasil disimpan.")

# -------------------------------
# Hitung Gaji (Serial)
# -------------------------------
def hitung_gaji_serial():
    if not data_absen:
        print("     Input data absen terlebih dahulu!")
        return
    data_gaji.clear()
    start = time.time()
    for i, k in enumerate(data_karyawan):
        hari_masuk = int(data_absen[i]["hari_masuk"])
        total = float(k["gaji_pokok"]) * hari_masuk
        data_gaji.append({
            "id": k["id"],
            "nama": k["nama"],
            "total_gaji": total
        })
    end = time.time()
    elapsed = end - start
    serial_times.append(elapsed)
    jumlah_data.append(len(data_karyawan))
    print(f"✅ Gaji berhasil dihitung secara SERIAL dalam {elapsed:.6f} detik.")

# -------------------------------
# Hitung Gaji (Parallel OpenMP)
# -------------------------------
def hitung_gaji_parallel():
    if not data_absen:
        print("     Input data absen terlebih dahulu!")
        return
    print("Menghitung gaji secara paralel...")
    data_gaji.clear()
    start = time.time()
    if omp_enabled and hasattr(omp, "parallel_for"):
        @omp("parallel for")
        def _():
            for i in range(len(data_karyawan)):
                k = data_karyawan[i]
                hari_masuk = int(data_absen[i]["hari_masuk"])
                total = float(k["gaji_pokok"]) * hari_masuk
                with omp.critical:
                    data_gaji.append({
                        "id": k["id"],
                        "nama": k["nama"],
                        "total_gaji": total
                    })
    else:
        for i in range(len(data_karyawan)):
            k = data_karyawan[i]
            hari_masuk = int(data_absen[i]["hari_masuk"])
            total = float(k["gaji_pokok"]) * hari_masuk
            data_gaji.append({
                "id": k["id"],
                "nama": k["nama"],
                "total_gaji": total
            })
    end = time.time()
    elapsed = end - start
    parallel_times.append(elapsed)
    jumlah_data.append(len(data_karyawan))
    if omp_enabled:
        print(f"✅ Gaji berhasil dihitung secara PARALEL (omp4py aktif) dalam {elapsed:.6f} detik.")
    else:
        print(f"     omp4py tidak aktif, perhitungan dijalankan secara SERIAL dalam {elapsed:.6f} detik.")

# -------------------------------
# Tampilkan Data Gaji
# -------------------------------
def tampilkan_gaji():
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
    simpan_ke_csv("karyawan.csv", data_karyawan, ["id", "nama", "jabatan", "gaji_pokok"])
    simpan_ke_csv("absen.csv", data_absen, ["id", "hari_masuk"])
    simpan_ke_csv("gaji.csv", data_gaji, ["id", "nama", "total_gaji"])

def muat_semua_data():
    global data_karyawan, data_absen, data_gaji
    data_karyawan = muat_dari_csv("karyawan.csv")
    data_absen = muat_dari_csv("absen.csv")
    data_gaji = muat_dari_csv("gaji.csv")
    print("✅ Semua data berhasil dimuat dari file CSV.")

# -------------------------------
# Tampilkan Grafik Perbandingan Waktu
# -------------------------------
def tampilkan_grafik():
    if not serial_times or not parallel_times:
        print("     Belum ada data perbandingan waktu eksekusi!")
        print("Silakan jalankan perhitungan serial dan paralel terlebih dahulu.")
        return
    plt.figure(figsize=(8, 5))
    plt.plot(jumlah_data[:len(serial_times)], serial_times, marker='o', label='Serial')
    plt.plot(jumlah_data[:len(parallel_times)], parallel_times, marker='s', label='Parallel (OpenMP)')
    plt.title('Perbandingan Waktu Eksekusi Serial vs Parallel')
    plt.xlabel('Jumlah Data Karyawan')
    plt.ylabel('Waktu Eksekusi (detik)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    print("\n=== HASIL SPEEDUP ===")
    for i in range(min(len(serial_times), len(parallel_times))):
        speedup = serial_times[i] / parallel_times[i] if parallel_times[i] != 0 else 0
        print(f"Data {jumlah_data[i]} karyawan → Speedup = {speedup:.2f}x")

# -------------------------------
# Jalankan Program
# -------------------------------
if __name__ == "__main__":
    menu()
