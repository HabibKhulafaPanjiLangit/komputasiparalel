"""
Helper script untuk perhitungan gaji parallel dengan MPI
Dipanggil oleh web application
"""

from mpi4py import MPI  # type: ignore
import csv

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def main():
    # Baca data dari file temp
    if rank == 0:
        # Master process membaca data
        karyawan = []
        absen = []
        
        with open('temp_karyawan.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            karyawan = list(reader)
        
        with open('temp_absen.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            absen = list(reader)
        
        # Distribusi pekerjaan
        num_karyawan = len(karyawan)
        per_process = num_karyawan // size
        remainder = num_karyawan % size
        
        start_idx = 0
        for i in range(size):
            count = per_process + (1 if i < remainder else 0)
            end_idx = start_idx + count
            
            if i == 0:
                local_karyawan = karyawan[start_idx:end_idx]
                local_absen = absen[start_idx:end_idx]
            else:
                comm.send((karyawan[start_idx:end_idx], absen[start_idx:end_idx]), dest=i, tag=0)
            
            start_idx = end_idx
        
        # Proses lokal
        local_gaji = []
        for i, k in enumerate(local_karyawan):
            hari_masuk = int(local_absen[i]["hari_masuk"])
            total = float(k["gaji_pokok"]) * hari_masuk
            local_gaji.append({
                "id": k["id"],
                "nama": k["nama"],
                "total_gaji": total
            })
        
        # Kumpulkan hasil
        all_gaji = [local_gaji]
        for i in range(1, size):
            hasil = comm.recv(source=i, tag=1)
            all_gaji.append(hasil)
        
        # Gabungkan dan simpan
        gaji_final = []
        for chunk in all_gaji:
            gaji_final.extend(chunk)
        
        # Simpan ke file
        with open('temp_gaji.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'nama', 'total_gaji'])
            writer.writeheader()
            writer.writerows(gaji_final)
        
        print(f"[MPI] Berhasil menghitung {len(gaji_final)} gaji dengan {size} proses")
    
    else:
        # Worker process
        local_karyawan, local_absen = comm.recv(source=0, tag=0)
        
        local_gaji = []
        for i, k in enumerate(local_karyawan):
            hari_masuk = int(local_absen[i]["hari_masuk"])
            total = float(k["gaji_pokok"]) * hari_masuk
            local_gaji.append({
                "id": k["id"],
                "nama": k["nama"],
                "total_gaji": total
            })
        
        comm.send(local_gaji, dest=0, tag=1)

if __name__ == "__main__":
    main()
