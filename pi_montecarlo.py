from mpi4py import MPI
import random, time, math

def estimate_pi(trials: int) -> float:
    inside = 0
    for _ in range(trials):
        x, y = random.random(), random.random()
        if x*x + y*y <= 1.0:
            inside += 1
    return 4.0 * inside / trials

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# total percobaan dibagi rata
TOTAL_TRIALS = 4_000_000
local_trials = TOTAL_TRIALS // size

# seed berbeda per-rank biar sampel tidak identik
random.seed(123456 + rank)

t0 = time.perf_counter()
local_pi = estimate_pi(local_trials)

# rata-rata estimasi dari semua rank
avg_pi = comm.reduce(local_pi, op=MPI.SUM, root=0)
t1 = time.perf_counter()

if rank == 0:
    pi_est = avg_pi / size
    err = abs(math.pi - pi_est)
    print(f"Pi ~= {pi_est:.6f} | error={err:.6f} | procs={size} | time={t1 - t0:.3f}s")


