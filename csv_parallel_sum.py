from mpi4py import MPI
import csv, time, os

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# === KONFIGURASI ===
CSV_PATH   = r"D:\data\big.csv"   # sudah benar: file besar
COL_INDEX  = 2                    # kolom 'value'
HAS_HEADER = True
ENCODING   = "utf-8"
CPU_WORK   = int(os.getenv("CPU_WORK", "0"))  # 0=off, >0 = beban komputasi ringan
# ====================

def count_lines(path):
    with open(path, "r", newline="", encoding=ENCODING, errors="ignore") as f:
        return sum(1 for _ in f)

if rank == 0:
    total_lines = count_lines(CSV_PATH)
    start = 1 if HAS_HEADER else 0
    data_lines = max(0, total_lines - start)
    base, rem = divmod(data_lines, size)
    sizes = [base + (1 if i < rem else 0) for i in range(size)]
    offsets = [start]
    for s in sizes[:-1]:
        offsets.append(offsets[-1] + s)
else:
    sizes = None
    offsets = None

sizes   = comm.bcast(sizes, root=0)
offsets = comm.bcast(offsets, root=0)
my_start = offsets[rank]
my_size  = sizes[rank]

# ===== timer mulai =====
t0 = time.perf_counter()

local_sum = 0.0
local_cnt = 0
if my_size > 0:
    with open(CSV_PATH, "r", newline="", encoding=ENCODING, errors="ignore") as f:
        reader = csv.reader(f)
        for _ in range(my_start):
            next(reader, None)
        for _ in range(my_size):
            row = next(reader, None)
            if row is None: break
            try:
                val = float(row[COL_INDEX])
                # Beban CPU ringan (opsional) BIAR TIDAK MENGUBAH NILAI ASLI
                tmp = val
                for _ in range(CPU_WORK):
                    tmp = (tmp * 1.000001) ** 0.5
                # akumulasi pakai nilai asli
                local_sum += val
                local_cnt += 1
            except (ValueError, IndexError):
                pass

t1 = time.perf_counter()
local_time = t1 - t0
# ===== timer selesai =====

global_sum  = comm.reduce(local_sum,  op=MPI.SUM, root=0)
global_cnt  = comm.reduce(local_cnt,  op=MPI.SUM, root=0)
global_time = comm.reduce(local_time, op=MPI.MAX, root=0)  # waktu terlama antar-rank = critical path

if rank == 0:
    avg = (global_sum / global_cnt) if global_cnt else float("nan")
    print(f"rows={global_cnt}, sum={global_sum}, avg={avg}, time={global_time:.3f}s, procs={size}")
