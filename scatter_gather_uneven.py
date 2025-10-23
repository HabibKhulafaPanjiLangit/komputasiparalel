# scatter_gather_uneven.py (versi final rapi)
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    N = 37  # contoh data tak habis dibagi
    data = list(range(N))
    base, rem = divmod(N, size)
    sizes = [base + (1 if i < rem else 0) for i in range(size)]
    offsets = [0]
    for s in sizes[:-1]:
        offsets.append(offsets[-1] + s)
    chunks = [data[offsets[i]:offsets[i] + sizes[i]] for i in range(size)]
else:
    chunks = None
    sizes = None

# broadcast sizes ke semua rank (untuk info/debug kalau perlu)
sizes = comm.bcast(sizes, root=0)

# scatter potongan data
local = comm.scatter(chunks, root=0)

# kerja lokal
local_sum = sum(x*x for x in local)

# kumpulkan hasil
partials = comm.gather(local_sum, root=0)

# sinkron opsional (biar output konsisten)
comm.Barrier()

if rank == 0:
    total = sum(partials)
    # verifikasi analitik: sum_{i=0}^{N-1} i^2 = n(n+1)(2n+1)/6 dengan n=N-1
    n = sum(sizes) - 1
    expected = n * (n + 1) * (2*n + 1) // 6
    print(f"sizes={sizes}")
    print(f"partials={partials}")
    print(f"total={total} (expected={expected})", flush=True)
