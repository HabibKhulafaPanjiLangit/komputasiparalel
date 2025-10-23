"""
Demo Otomatis Benchmark: Serial vs Parallel MPI
Program Penghitungan Gaji Karyawan
"""

from mpi4py import MPI  # type: ignore
import time
import random

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def generate_data(num_karyawan):
    """Generate data karyawan dan absen otomatis"""
    if rank != 0:
        return None, None
    
    karyawan = []
    absen = []
    
    for i in range(num_karyawan):
        karyawan.append({
            "id": f"K{i+1:04d}",
            "nama": f"Karyawan {i+1}",
            "gaji_pokok": 150000 + (i % 5) * 50000
        })
        absen.append({
            "id": f"K{i+1:04d}",
            "hari_masuk": random.randint(20, 26)
        })
    
    return karyawan, absen

def hitung_gaji_serial(data_karyawan, data_absen):
    """Hitung gaji secara serial"""
    if rank != 0:
        return None, 0
    
    start = time.perf_counter()
    
    data_gaji = []
    for i, k in enumerate(data_karyawan):
        hari_masuk = data_absen[i]["hari_masuk"]
        total = k["gaji_pokok"] * hari_masuk
        data_gaji.append({
            "id": k["id"],
            "nama": k["nama"],
            "total_gaji": total
        })
    
    elapsed = time.perf_counter() - start
    return data_gaji, elapsed

def hitung_gaji_parallel(data_karyawan, data_absen):
    """Hitung gaji secara parallel dengan MPI"""
    
    if rank == 0:
        start = time.perf_counter()
        
        num_karyawan = len(data_karyawan)
        karyawan_per_process = num_karyawan // size
        remainder = num_karyawan % size
        
        # Distribusi data
        start_idx = 0
        for i in range(size):
            count = karyawan_per_process + (1 if i < remainder else 0)
            end_idx = start_idx + count
            
            if i == 0:
                local_karyawan = data_karyawan[start_idx:end_idx]
                local_absen = data_absen[start_idx:end_idx]
            else:
                comm.send((data_karyawan[start_idx:end_idx], 
                          data_absen[start_idx:end_idx]), dest=i, tag=0)
            
            start_idx = end_idx
        
        # Proses lokal
        local_gaji = []
        for i, k in enumerate(local_karyawan):
            hari_masuk = local_absen[i]["hari_masuk"]
            total = k["gaji_pokok"] * hari_masuk
            local_gaji.append({
                "id": k["id"],
                "nama": k["nama"],
                "total_gaji": total
            })
        
        # Kumpulkan hasil
        all_results = [local_gaji]
        for i in range(1, size):
            results = comm.recv(source=i, tag=1)
            all_results.append(results)
        
        # Gabungkan hasil
        data_gaji = []
        for result_chunk in all_results:
            data_gaji.extend(result_chunk)
        
        elapsed = time.perf_counter() - start
        return data_gaji, elapsed
    
    else:
        # Worker process
        local_karyawan, local_absen = comm.recv(source=0, tag=0)
        
        local_gaji = []
        for i, k in enumerate(local_karyawan):
            hari_masuk = local_absen[i]["hari_masuk"]
            total = k["gaji_pokok"] * hari_masuk
            local_gaji.append({
                "id": k["id"],
                "nama": k["nama"],
                "total_gaji": total
            })
        
        comm.send(local_gaji, dest=0, tag=1)
        return None, 0

def main():
    if rank == 0:
        print("=" * 70)
        print(" " * 15 + "BENCHMARK: PENGHITUNGAN GAJI KARYAWAN")
        print(" " * 20 + "Serial vs Parallel (MPI)")
        print("=" * 70)
        print(f"\nMenggunakan {size} proses MPI\n")
    
    # Test dengan berbagai ukuran data
    test_sizes = [1000, 5000, 10000, 50000]
    
    results = []
    
    for num_karyawan in test_sizes:
        if rank == 0:
            print(f"\n{'='*70}")
            print(f"Testing dengan {num_karyawan:,} karyawan")
            print(f"{'='*70}")
        
        # Generate data
        data_karyawan, data_absen = generate_data(num_karyawan)
        
        # Test Serial
        if rank == 0:
            print(f"\n[Serial] Memproses {num_karyawan:,} karyawan...")
        
        gaji_serial, time_serial = hitung_gaji_serial(data_karyawan, data_absen)
        
        if rank == 0:
            print(f"  Waktu: {time_serial:.6f} detik")
        
        # Test Parallel MPI
        if rank == 0:
            print(f"\n[Parallel MPI] Memproses {num_karyawan:,} karyawan...")
        
        gaji_parallel, time_parallel = hitung_gaji_parallel(data_karyawan, data_absen)
        
        if rank == 0:
            print(f"  Waktu: {time_parallel:.6f} detik")
            
            speedup = time_serial / time_parallel if time_parallel > 0 else 0
            print(f"\n  >> Speedup: {speedup:.2f}x")
            print(f"  >> Efisiensi: {(speedup/size)*100:.1f}%")
            
            results.append({
                'size': num_karyawan,
                'serial': time_serial,
                'parallel': time_parallel,
                'speedup': speedup
            })
    
    # Summary
    if rank == 0:
        print("\n" + "=" * 70)
        print(" " * 25 + "RINGKASAN HASIL")
        print("=" * 70)
        print(f"\n{'Jumlah Data':<15} {'Serial (s)':<15} {'Parallel (s)':<15} {'Speedup':<10}")
        print("-" * 70)
        
        for r in results:
            print(f"{r['size']:<15,} {r['serial']:<15.6f} {r['parallel']:<15.6f} {r['speedup']:<10.2f}x")
        
        print("=" * 70)
        print(f"\nProses MPI yang digunakan: {size}")
        
        avg_speedup = sum(r['speedup'] for r in results) / len(results)
        print(f"Rata-rata Speedup: {avg_speedup:.2f}x")
        print(f"Rata-rata Efisiensi: {(avg_speedup/size)*100:.1f}%")
        print("=" * 70)

if __name__ == "__main__":
    main()
