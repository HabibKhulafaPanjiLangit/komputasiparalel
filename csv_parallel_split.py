try:
    from mpi4py import MPI  # type: ignore
except Exception:
    # Fallback single-process stub for environments without mpi4py so the script can run locally.
    class _FakeComm:
        def __init__(self):
            self._rank = 0
            self._size = 1
        def Get_rank(self):
            return self._rank
        def Get_size(self):
            return self._size
        def reduce(self, value, op=None, root=0):
            # In single-process fallback just return the local value
            return value
    class _MPI:
        SUM = None
        MAX = None
        COMM_WORLD = _FakeComm()
    MPI = _MPI()

import csv, time, os
from multiprocessing.pool import ThreadPool

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# === KONFIGURASI ===
DIR = r"D:\data\big_split"   # folder tempat file split disimpan
CPU_WORK = int(os.getenv("CPU_WORK", "0"))  # beban komputasi opsional
OMP_THREADS = int(os.getenv("OMP_NUM_THREADS", "1"))  # jumlah thread OpenMP per proses MPI
# ====================

path = os.path.join(DIR, f"big_{rank}.csv")  # setiap rank baca file sesuai nomor

if not os.path.exists(path):
    print(f"[Rank {rank}] File tidak ditemukan: {path}")
    exit(0)

t0 = time.perf_counter()

# Load data ke memori untuk OpenMP parallelization
rows_data = []
with open(path, "r", newline="", encoding="utf-8", errors="ignore") as f:
    reader = csv.reader(f)
    next(reader, None)  # lewati header
    rows_data = list(reader)

local_sum = 0.0
local_cnt = 0

def process_chunk(args):
    """Process a chunk of rows and return partial sum and count"""
    start, end = args
    psum = 0.0
    pcnt = 0
    for i in range(start, end):
        row = rows_data[i]
        try:
            val = float(row[2])
            tmp = val
            for _ in range(CPU_WORK):
                tmp = (tmp * 1.000001) ** 0.5
            psum += val
            pcnt += 1
        except (ValueError, IndexError):
            pass
    return psum, pcnt

if OMP_THREADS > 1 and len(rows_data) > 0:
    # Parallel processing using ThreadPool
    num_rows = len(rows_data)
    chunk_ranges = []
    for tid in range(OMP_THREADS):
        start = tid * num_rows // OMP_THREADS
        end = (tid + 1) * num_rows // OMP_THREADS
        chunk_ranges.append((start, end))
    
    with ThreadPool(processes=OMP_THREADS) as pool:
        results = pool.map(process_chunk, chunk_ranges)
    
    local_sum = sum(r[0] for r in results)
    local_cnt = sum(r[1] for r in results)
else:
    # Sequential fallback
    for row in rows_data:
        try:
            val = float(row[2])
            tmp = val
            for _ in range(CPU_WORK):
                tmp = (tmp * 1.000001) ** 0.5
            local_sum += val
            local_cnt += 1
        except (ValueError, IndexError):
            pass

t1 = time.perf_counter()
local_time = t1 - t0

# Reduksi hasil dari semua proses
global_sum  = comm.reduce(local_sum,  op=MPI.SUM, root=0)
global_cnt  = comm.reduce(local_cnt,  op=MPI.SUM, root=0)
global_time = comm.reduce(local_time, op=MPI.MAX, root=0)

if rank == 0:
    avg = (global_sum / global_cnt) if global_cnt else float("nan")
    omp_info = f", threads={OMP_THREADS}" if OMP_THREADS > 1 else ""
    print(f"rows={global_cnt}, sum={global_sum}, avg={avg}, time={global_time:.3f}s, procs={size}{omp_info}")