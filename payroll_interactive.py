"""
MPI Payroll System - Interactive CLI
Program penggajian karyawan dengan menu interaktif
Mendukung mode Serial dan Parallel (MPI)
"""

from mpi4py import MPI
import time
import csv
import os
from datetime import datetime

# MPI Setup
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Global data storage
data_karyawan = []
data_absen = []
data_gaji = []

# File paths
FILE_KARYAWAN = "karyawan.csv"
FILE_ABSEN = "absen.csv"
FILE_GAJI = "gaji.csv"


class Karyawan:
    def __init__(self, id_karyawan, nama, jabatan, gaji_pokok):
        self.id = id_karyawan
        self.nama = nama
        self.jabatan = jabatan
        self.gaji_pokok = gaji_pokok


class Absen:
    def __init__(self, id_karyawan, hari_masuk):
        self.id = id_karyawan
        self.hari_masuk = hari_masuk


class Gaji:
    def __init__(self, karyawan, absen):
        self.id = karyawan.id
        self.nama = karyawan.nama
        self.jabatan = karyawan.jabatan
        self.gaji_pokok = karyawan.gaji_pokok
        self.hari_masuk = absen.hari_masuk
        self.total_gaji = self.hitung_total()
    
    def hitung_total(self):
        """Hitung total gaji dengan berbagai komponen"""
        gaji_dasar = self.gaji_pokok * self.hari_masuk
        
        # Tunjangan berdasarkan jabatan
        if "Manager" in self.jabatan:
            tunjangan = gaji_dasar * 0.20
        elif "Supervisor" in self.jabatan:
            tunjangan = gaji_dasar * 0.15
        elif "Staff" in self.jabatan:
            tunjangan = gaji_dasar * 0.10
        else:
            tunjangan = gaji_dasar * 0.05
        
        # Bonus kehadiran
        if self.hari_masuk >= 25:
            bonus = gaji_dasar * 0.10
        elif self.hari_masuk >= 20:
            bonus = gaji_dasar * 0.05
        else:
            bonus = 0
        
        # Pajak 5%
        total_kotor = gaji_dasar + tunjangan + bonus
        pajak = total_kotor * 0.05
        
        return total_kotor - pajak


def clear_screen():
    """Clear console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Print program header"""
    print("\n" + "="*60)
    print("  MPI PAYROLL SYSTEM - INTERACTIVE MODE")
    print("  Komputasi Paralel dengan MPI4Py")
    print("="*60)
    if size > 1:
        print(f"  Running with {size} MPI processes")
    print("="*60 + "\n")


def print_menu():
    """Print main menu"""
    print("\n[MENU UTAMA]")
    print("1. Input Data Karyawan")
    print("2. Input Data Absen")
    print("3. Hitung Gaji (Serial)")
    print("4. Hitung Gaji (Parallel - MPI)")
    print("5. Tampilkan Data Gaji")
    print("6. Keluar")
    print("7. Simpan Semua Data ke File CSV")
    print("8. Muat Data dari File CSV")
    print("9. Generate Data Dummy (Auto)")
    print("0. Hapus Semua Data")
    print("-" * 60)


def input_karyawan():
    """Menu 1: Input data karyawan"""
    global data_karyawan
    
    print("\n[INPUT DATA KARYAWAN]")
    try:
        id_karyawan = input("ID Karyawan: ").strip()
        if not id_karyawan:
            print("[X] ID tidak boleh kosong!")
            return
        
        # Cek duplikat
        if any(k.id == id_karyawan for k in data_karyawan):
            print(f"[X] ID {id_karyawan} sudah ada!")
            return
        
        nama = input("Nama: ").strip()
        jabatan = input("Jabatan (Manager/Supervisor/Staff): ").strip()
        gaji_pokok = float(input("Gaji Pokok per Hari (Rp): "))
        
        karyawan = Karyawan(id_karyawan, nama, jabatan, gaji_pokok)
        data_karyawan.append(karyawan)
        
        print(f"[OK] Karyawan {nama} berhasil ditambahkan!")
        
    except ValueError:
        print("[X] Input tidak valid!")
    except KeyboardInterrupt:
        print("\n[!] Dibatalkan")


def input_absen():
    """Menu 2: Input data absen"""
    global data_absen, data_karyawan
    
    print("\n[INPUT DATA ABSEN]")
    
    if not data_karyawan:
        print("[X] Belum ada data karyawan! Tambahkan dulu di menu 1.")
        return
    
    # Tampilkan daftar karyawan
    print("\nDaftar Karyawan:")
    for i, k in enumerate(data_karyawan, 1):
        print(f"  {i}. {k.id} - {k.nama} ({k.jabatan})")
    
    try:
        pilihan = int(input("\nPilih nomor karyawan: ")) - 1
        
        if pilihan < 0 or pilihan >= len(data_karyawan):
            print("[X] Pilihan tidak valid!")
            return
        
        karyawan = data_karyawan[pilihan]
        
        # Cek apakah sudah ada data absen
        existing = next((a for a in data_absen if a.id == karyawan.id), None)
        if existing:
            print(f"[!] Absen untuk {karyawan.id} sudah ada ({existing.hari_masuk} hari)")
            update = input("Update data? (y/n): ").lower()
            if update != 'y':
                return
            data_absen.remove(existing)
        
        hari_masuk = int(input("Jumlah Hari Masuk (1-31): "))
        
        if hari_masuk < 1 or hari_masuk > 31:
            print("[X] Hari masuk harus antara 1-31!")
            return
        
        absen = Absen(karyawan.id, hari_masuk)
        data_absen.append(absen)
        
        print(f"[OK] Data absen {karyawan.nama} berhasil disimpan!")
        
    except ValueError:
        print("[X] Input tidak valid!")
    except KeyboardInterrupt:
        print("\n[!] Dibatalkan")


def hitung_gaji_serial():
    """Menu 3: Hitung gaji secara serial"""
    global data_gaji, data_karyawan, data_absen
    
    print("\n[HITUNG GAJI - MODE SERIAL]")
    
    if not data_karyawan or not data_absen:
        print("[X] Data karyawan atau absen belum lengkap!")
        return
    
    print("Memproses...")
    start_time = time.time()
    
    data_gaji = []
    
    for karyawan in data_karyawan:
        absen = next((a for a in data_absen if a.id == karyawan.id), None)
        if absen:
            gaji = Gaji(karyawan, absen)
            data_gaji.append(gaji)
            
            # Simulasi perhitungan kompleks
            for _ in range(100000):
                _ = sum([i**2 for i in range(100)])
    
    end_time = time.time()
    waktu = end_time - start_time
    
    print(f"[OK] Selesai! {len(data_gaji)} gaji dihitung")
    print(f"[>>] Waktu Eksekusi: {waktu:.4f} detik")


def hitung_gaji_parallel():
    """Menu 4: Hitung gaji secara parallel dengan MPI"""
    global data_gaji, data_karyawan, data_absen
    
    if rank == 0:
        print("\n[HITUNG GAJI - MODE PARALLEL MPI]")
        
        if not data_karyawan or not data_absen:
            print("[X] Data karyawan atau absen belum lengkap!")
            return
        
        print(f"Memproses dengan {size} proses...")
        start_time = time.time()
    else:
        start_time = None
    
    # Broadcast data ke semua proses
    data_karyawan_bcast = comm.bcast(data_karyawan, root=0)
    data_absen_bcast = comm.bcast(data_absen, root=0)
    
    # Bagi kerja
    n = len(data_karyawan_bcast)
    local_n = n // size
    remainder = n % size
    
    if rank < remainder:
        start = rank * (local_n + 1)
        end = start + local_n + 1
    else:
        start = rank * local_n + remainder
        end = start + local_n
    
    # Proses lokal
    local_gaji = []
    for i in range(start, end):
        karyawan = data_karyawan_bcast[i]
        absen = next((a for a in data_absen_bcast if a.id == karyawan.id), None)
        if absen:
            gaji = Gaji(karyawan, absen)
            local_gaji.append(gaji)
            
            # Simulasi perhitungan kompleks
            for _ in range(100000):
                _ = sum([i**2 for i in range(100)])
    
    # Gather hasil
    all_gaji = comm.gather(local_gaji, root=0)
    
    if rank == 0:
        data_gaji = []
        for gaji_list in all_gaji:
            data_gaji.extend(gaji_list)
        
        end_time = time.time()
        waktu = end_time - start_time
        
        print(f"[OK] Selesai! {len(data_gaji)} gaji dihitung")
        print(f"[>>] Waktu Eksekusi: {waktu:.4f} detik")
        print(f"[>>] Speedup potensial dengan {size} proses")


def tampilkan_gaji():
    """Menu 5: Tampilkan data gaji"""
    global data_gaji
    
    print("\n[DATA GAJI KARYAWAN]")
    
    if not data_gaji:
        print("[X] Belum ada data gaji. Hitung dulu di menu 3 atau 4.")
        return
    
    print("\n" + "="*100)
    print(f"{'ID':<10} {'Nama':<20} {'Jabatan':<15} {'Gaji/Hari':<12} {'Hari':<6} {'Total Gaji':<15}")
    print("="*100)
    
    total_semua = 0
    for gaji in data_gaji:
        print(f"{gaji.id:<10} {gaji.nama:<20} {gaji.jabatan:<15} "
              f"Rp {gaji.gaji_pokok:>9,.0f} {gaji.hari_masuk:>4} "
              f"Rp {gaji.total_gaji:>12,.0f}")
        total_semua += gaji.total_gaji
    
    print("="*100)
    print(f"{'TOTAL GAJI SEMUA KARYAWAN:':<82} Rp {total_semua:>12,.0f}")
    print("="*100)


def simpan_ke_csv():
    """Menu 7: Simpan semua data ke file CSV"""
    global data_karyawan, data_absen, data_gaji
    
    print("\n[SIMPAN DATA KE CSV]")
    
    try:
        # Simpan karyawan
        with open(FILE_KARYAWAN, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Nama', 'Jabatan', 'Gaji_Pokok'])
            for k in data_karyawan:
                writer.writerow([k.id, k.nama, k.jabatan, k.gaji_pokok])
        print(f"[OK] {len(data_karyawan)} data karyawan disimpan ke {FILE_KARYAWAN}")
        
        # Simpan absen
        with open(FILE_ABSEN, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Hari_Masuk'])
            for a in data_absen:
                writer.writerow([a.id, a.hari_masuk])
        print(f"[OK] {len(data_absen)} data absen disimpan ke {FILE_ABSEN}")
        
        # Simpan gaji
        if data_gaji:
            with open(FILE_GAJI, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Nama', 'Jabatan', 'Gaji_Pokok', 'Hari_Masuk', 'Total_Gaji'])
                for g in data_gaji:
                    writer.writerow([g.id, g.nama, g.jabatan, g.gaji_pokok, g.hari_masuk, g.total_gaji])
            print(f"[OK] {len(data_gaji)} data gaji disimpan ke {FILE_GAJI}")
        
        print("[>>] Semua data berhasil disimpan!")
        
    except Exception as e:
        print(f"[X] Error: {e}")


def muat_dari_csv():
    """Menu 8: Muat data dari file CSV"""
    global data_karyawan, data_absen, data_gaji
    
    print("\n[MUAT DATA DARI CSV]")
    
    try:
        # Muat karyawan
        if os.path.exists(FILE_KARYAWAN):
            data_karyawan = []
            with open(FILE_KARYAWAN, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    k = Karyawan(row['ID'], row['Nama'], row['Jabatan'], float(row['Gaji_Pokok']))
                    data_karyawan.append(k)
            print(f"[OK] {len(data_karyawan)} data karyawan dimuat dari {FILE_KARYAWAN}")
        else:
            print(f"[!] File {FILE_KARYAWAN} tidak ditemukan")
        
        # Muat absen
        if os.path.exists(FILE_ABSEN):
            data_absen = []
            with open(FILE_ABSEN, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    a = Absen(row['ID'], int(row['Hari_Masuk']))
                    data_absen.append(a)
            print(f"[OK] {len(data_absen)} data absen dimuat dari {FILE_ABSEN}")
        else:
            print(f"[!] File {FILE_ABSEN} tidak ditemukan")
        
        # Muat gaji
        if os.path.exists(FILE_GAJI):
            print(f"[!] File gaji ditemukan. Hitung ulang untuk data terbaru.")
        
        if data_karyawan and data_absen:
            print("[>>] Data berhasil dimuat! Silakan hitung gaji di menu 3/4.")
        
    except Exception as e:
        print(f"[X] Error: {e}")


def generate_dummy_data():
    """Menu 9: Generate data dummy otomatis"""
    global data_karyawan, data_absen
    
    print("\n[GENERATE DATA DUMMY]")
    
    jumlah = input("Jumlah karyawan dummy (default: 10): ").strip()
    try:
        jumlah = int(jumlah) if jumlah else 10
    except ValueError:
        jumlah = 10
    
    print(f"Generating {jumlah} karyawan dummy...")
    
    jabatan_list = ["Manager", "Supervisor", "Staff Senior", "Staff", "Operator"]
    nama_depan = ["Andi", "Budi", "Citra", "Deni", "Eka", "Fajar", "Gita", "Hadi", "Indra", "Joko"]
    nama_belakang = ["Pratama", "Wijaya", "Santoso", "Permana", "Saputra", "Kurniawan", "Putra", "Wibowo"]
    
    import random
    
    data_karyawan = []
    data_absen = []
    
    for i in range(1, jumlah + 1):
        id_karyawan = f"K{i:03d}"
        nama = f"{random.choice(nama_depan)} {random.choice(nama_belakang)}"
        jabatan = random.choice(jabatan_list)
        gaji_pokok = random.randint(150, 500) * 1000
        
        karyawan = Karyawan(id_karyawan, nama, jabatan, gaji_pokok)
        data_karyawan.append(karyawan)
        
        hari_masuk = random.randint(15, 30)
        absen = Absen(id_karyawan, hari_masuk)
        data_absen.append(absen)
    
    print(f"[OK] {jumlah} karyawan dan data absen berhasil di-generate!")
    print("[>>] Silakan hitung gaji di menu 3/4.")


def hapus_semua_data():
    """Menu 0: Hapus semua data"""
    global data_karyawan, data_absen, data_gaji
    
    print("\n[HAPUS SEMUA DATA]")
    konfirmasi = input("Yakin ingin menghapus semua data? (yes/no): ").lower()
    
    if konfirmasi == 'yes':
        data_karyawan = []
        data_absen = []
        data_gaji = []
        print("[OK] Semua data telah dihapus!")
    else:
        print("[!] Dibatalkan")


def main():
    """Main program loop"""
    if rank == 0:
        clear_screen()
        print_header()
        
        while True:
            print_menu()
            
            try:
                pilihan = input("\nPilih menu (0-9): ").strip()
                
                if pilihan == '1':
                    input_karyawan()
                elif pilihan == '2':
                    input_absen()
                elif pilihan == '3':
                    hitung_gaji_serial()
                elif pilihan == '4':
                    # Broadcast signal untuk parallel computation
                    signal = 4
                    comm.bcast(signal, root=0)
                    hitung_gaji_parallel()
                elif pilihan == '5':
                    tampilkan_gaji()
                elif pilihan == '6':
                    print("\n[>>] Terima kasih! Program selesai.\n")
                    # Signal other processes to exit
                    signal = -1
                    comm.bcast(signal, root=0)
                    break
                elif pilihan == '7':
                    simpan_ke_csv()
                elif pilihan == '8':
                    muat_dari_csv()
                elif pilihan == '9':
                    generate_dummy_data()
                elif pilihan == '0':
                    hapus_semua_data()
                else:
                    print("[X] Pilihan tidak valid!")
                
                input("\nTekan Enter untuk melanjutkan...")
                
            except KeyboardInterrupt:
                print("\n\n[!] Program dihentikan oleh user.")
                signal = -1
                comm.bcast(signal, root=0)
                break
            except Exception as e:
                print(f"\n[X] Error: {e}")
                input("\nTekan Enter untuk melanjutkan...")
    
    else:
        # Worker processes menunggu signal
        while True:
            signal = comm.bcast(None, root=0)
            
            if signal == -1:  # Exit signal
                break
            elif signal == 4:  # Parallel computation
                hitung_gaji_parallel()


if __name__ == "__main__":
    main()
