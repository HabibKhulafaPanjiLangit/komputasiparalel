from mpi4py import MPI  # type: ignore
import random
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def pi_montecarlo_mpi(total_points: int) -> float:
    """
    Menghitung nilai Pi menggunakan metode Monte Carlo dengan MPI
    
    Args:
        total_points: Total jumlah titik random yang akan digunakan
    
    Returns:
        Estimasi nilai Pi
    """
    
    # Bagi pekerjaan ke semua proses
    points_per_process = total_points // size
    remainder = total_points % size
    
    # Proses dengan rank lebih kecil mendapat 1 titik extra jika ada remainder
    if rank < remainder:
        local_points = points_per_process + 1
    else:
        local_points = points_per_process
    
    if rank == 0:
        print(f"\n[Rank {rank}] Menghitung Pi dengan {total_points:,} titik random")
        print(f"[Rank {rank}] Menggunakan {size} proses MPI")
        print(f"[Rank {rank}] Setiap proses menghitung ~{points_per_process:,} titik\n")
    
    # Setiap proses menghitung bagiannya sendiri
    local_count = 0
    random.seed(rank)  # Seed berbeda untuk setiap proses
    
    start_time = time.perf_counter()
    
    for i in range(local_points):
        x = random.random()
        y = random.random()
        
        # Cek apakah titik berada di dalam lingkaran kuadran
        if x*x + y*y <= 1.0:
            local_count += 1
    
    local_time = time.perf_counter() - start_time
    
    # Kumpulkan hasil dari semua proses menggunakan reduce
    total_count = comm.reduce(local_count, op=MPI.SUM, root=0)
    
    # Hitung nilai Pi hanya di rank 0
    if rank == 0:
        pi_estimate = 4.0 * total_count / total_points
        return pi_estimate, local_time
    else:
        return None, local_time

def pi_montecarlo_serial(total_points: int) -> float:
    """
    Menghitung nilai Pi secara serial (untuk perbandingan)
    
    Args:
        total_points: Total jumlah titik random yang akan digunakan
    
    Returns:
        Estimasi nilai Pi
    """
    if rank != 0:
        return None, 0
    
    print(f"\n[Serial] Menghitung Pi dengan {total_points:,} titik random")
    
    count = 0
    random.seed(0)
    
    start_time = time.perf_counter()
    
    for i in range(total_points):
        x = random.random()
        y = random.random()
        
        if x*x + y*y <= 1.0:
            count += 1
    
    elapsed_time = time.perf_counter() - start_time
    pi_estimate = 4.0 * count / total_points
    
    return pi_estimate, elapsed_time

def main():
    import math
    
    # Test dengan berbagai ukuran
    test_sizes = [100_000, 1_000_000, 10_000_000]
    
    if rank == 0:
        print("="*70)
        print(" "*15 + "MONTE CARLO PI CALCULATION (MPI)")
        print("="*70)
    
    for num_points in test_sizes:
        # MPI Parallel version
        pi_mpi, time_mpi = pi_montecarlo_mpi(num_points)
        
        if rank == 0:
            print(f"\n[MPI Parallel] Pi estimate: {pi_mpi:.10f}")
            print(f"[MPI Parallel] Error: {abs(pi_mpi - math.pi):.10f}")
            print(f"[MPI Parallel] Time: {time_mpi:.4f} seconds")
            print(f"[MPI Parallel] Using {size} processes")
        
        # Serial version (hanya untuk perbandingan pada dataset kecil)
        if num_points <= 1_000_000:
            pi_serial, time_serial = pi_montecarlo_serial(num_points)
            
            if rank == 0:
                print(f"\n[Serial] Pi estimate: {pi_serial:.10f}")
                print(f"[Serial] Error: {abs(pi_serial - math.pi):.10f}")
                print(f"[Serial] Time: {time_serial:.4f} seconds")
                
                if time_serial > 0:
                    speedup = time_serial / time_mpi
                    print(f"\nSpeedup: {speedup:.2f}x")
        
        if rank == 0:
            print("-"*70)
    
    if rank == 0:
        print("\nActual Pi value: {:.10f}".format(math.pi))
        print("="*70)

if __name__ == "__main__":
    main()
