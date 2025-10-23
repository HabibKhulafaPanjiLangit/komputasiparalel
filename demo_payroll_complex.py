"""
Demo Benchmark dengan Komputasi Lebih Berat
Simulasi perhitungan gaji yang lebih kompleks untuk menunjukkan manfaat MPI
"""

from mpi4py import MPI  # type: ignore
import time
import random
import math

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def hitung_pajak_kompleks(gaji_bruto):
    """Simulasi perhitungan pajak yang lebih kompleks (CPU intensive)"""
    # Simulasi komputasi berat dengan iterasi
    result = gaji_bruto
    for _ in range(1000):  # Simulasi komputasi
        result = math.sqrt(result * result + 1)
        result = math.log(result + 1)
        result = math.exp(result / 10)
    
    # Perhitungan pajak progresif
    if gaji_bruto <= 5000000:
        pajak = gaji_bruto * 0.05
    elif gaji_bruto <= 10000000:
        pajak = 250000 + (gaji_bruto - 5000000) * 0.15
    elif gaji_bruto <= 20000000:
        pajak = 1000000 + (gaji_bruto - 10000000) * 0.25
    else:
        pajak = 3500000 + (gaji_bruto - 20000000) * 0.30
    
    return pajak

def generate_data(num_karyawan):
    """Generate data karyawan"""
    if rank != 0:
        return None, None
    
    karyawan = []
    absen = []
    
    for i in range(num_karyawan):
        karyawan.append({
            "id": f"K{i+1:04d}",
            "nama": f"Karyawan {i+1}",
            "gaji_pokok": 150000 + (i % 5) * 50000,
            "tunjangan": random.randint(50000, 200000),
            "bonus_kinerja": random.randint(0, 500000)
        })
        absen.append({
            "id": f"K{i+1:04d}",
            "hari_masuk": random.randint(20, 26),
            "lembur": random.randint(0, 20)
        })
    
    return karyawan, absen

def hitung_gaji_serial(data_karyawan, data_absen):
    """Hitung gaji secara serial dengan komputasi kompleks"""
    if rank != 0:
        return None, 0
    
    start = time.perf_counter()
    
    data_gaji = []
    for i, k in enumerate(data_karyawan):
        hari_masuk = data_absen[i]["hari_masuk"]
        lembur = data_absen[i]["lembur"]
        
        # Perhitungan gaji kompleks
        gaji_pokok_total = k["gaji_pokok"] * hari_masuk
        gaji_lembur = k["gaji_pokok"] * 1.5 * lembur
        gaji_bruto = gaji_pokok_total + gaji_lembur + k["tunjangan"] + k["bonus_kinerja"]
        
        # Hitung pajak (CPU intensive)
        pajak = hitung_pajak_kompleks(gaji_bruto)
        
        gaji_netto = gaji_bruto - pajak
        
        data_gaji.append({
            "id": k["id"],
            "nama": k["nama"],
            "gaji_bruto": gaji_bruto,
            "pajak": pajak,
            "gaji_netto": gaji_netto
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
            lembur = local_absen[i]["lembur"]
            
            gaji_pokok_total = k["gaji_pokok"] * hari_masuk
            gaji_lembur = k["gaji_pokok"] * 1.5 * lembur
            gaji_bruto = gaji_pokok_total + gaji_lembur + k["tunjangan"] + k["bonus_kinerja"]
            
            pajak = hitung_pajak_kompleks(gaji_bruto)
            gaji_netto = gaji_bruto - pajak
            
            local_gaji.append({
                "id": k["id"],
                "nama": k["nama"],
                "gaji_bruto": gaji_bruto,
                "pajak": pajak,
                "gaji_netto": gaji_netto
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
            lembur = local_absen[i]["lembur"]
            
            gaji_pokok_total = k["gaji_pokok"] * hari_masuk
            gaji_lembur = k["gaji_pokok"] * 1.5 * lembur
            gaji_bruto = gaji_pokok_total + gaji_lembur + k["tunjangan"] + k["bonus_kinerja"]
            
            pajak = hitung_pajak_kompleks(gaji_bruto)
            gaji_netto = gaji_bruto - pajak
            
            local_gaji.append({
                "id": k["id"],
                "nama": k["nama"],
                "gaji_bruto": gaji_bruto,
                "pajak": pajak,
                "gaji_netto": gaji_netto
            })
        
        comm.send(local_gaji, dest=0, tag=1)
        return None, 0

def main():
    if rank == 0:
        print("=" * 70)
        print(" " * 10 + "BENCHMARK: PERHITUNGAN GAJI KOMPLEKS (MPI)")
        print(" " * 15 + "dengan Simulasi Perhitungan Pajak")
        print("=" * 70)
        print(f"\nMenggunakan {size} proses MPI")
        print("Setiap perhitungan gaji melibatkan komputasi pajak yang kompleks\n")
    
    # Test dengan berbagai ukuran data
    test_sizes = [100, 500, 1000, 2000]
    
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
            print(f"\n[Serial] Memproses {num_karyawan:,} karyawan dengan perhitungan kompleks...")
        
        gaji_serial, time_serial = hitung_gaji_serial(data_karyawan, data_absen)
        
        if rank == 0:
            print(f"  Waktu: {time_serial:.4f} detik")
        
        # Test Parallel MPI
        if rank == 0:
            print(f"\n[Parallel MPI] Memproses {num_karyawan:,} karyawan dengan perhitungan kompleks...")
        
        gaji_parallel, time_parallel = hitung_gaji_parallel(data_karyawan, data_absen)
        
        if rank == 0:
            print(f"  Waktu: {time_parallel:.4f} detik")
            
            speedup = time_serial / time_parallel if time_parallel > 0 else 0
            efisiensi = (speedup / size) * 100
            
            print(f"\n  >> Speedup: {speedup:.2f}x")
            print(f"  >> Efisiensi: {efisiensi:.1f}%")
            
            results.append({
                'size': num_karyawan,
                'serial': time_serial,
                'parallel': time_parallel,
                'speedup': speedup,
                'efisiensi': efisiensi
            })
    
    # Summary
    if rank == 0:
        print("\n" + "=" * 70)
        print(" " * 25 + "RINGKASAN HASIL")
        print("=" * 70)
        print(f"\n{'Jumlah':<12} {'Serial (s)':<14} {'Parallel (s)':<14} {'Speedup':<12} {'Efisiensi'}")
        print("-" * 70)
        
        for r in results:
            print(f"{r['size']:<12,} {r['serial']:<14.4f} {r['parallel']:<14.4f} {r['speedup']:<12.2f}x {r['efisiensi']:.1f}%")
        
        print("=" * 70)
        print(f"\nProses MPI yang digunakan: {size}")
        
        avg_speedup = sum(r['speedup'] for r in results) / len(results)
        avg_efisiensi = sum(r['efisiensi'] for r in results) / len(results)
        
        print(f"Rata-rata Speedup: {avg_speedup:.2f}x")
        print(f"Rata-rata Efisiensi: {avg_efisiensi:.1f}%")
        print("\nKesimpulan:")
        print("- Untuk komputasi kompleks, MPI memberikan speedup yang signifikan")
        print("- Overhead komunikasi MPI terkompensasi oleh paralelisasi komputasi")
        print("=" * 70)

if __name__ == "__main__":
    main()
