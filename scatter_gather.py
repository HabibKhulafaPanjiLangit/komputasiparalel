# file: scatter_gather_uneven.py
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    N = 37  # coba angka yang tidak habis dibagi size
    data = list(range(N))
    base, rem = divmod(N, size)
    sizes = [base + (1 if i < rem else 0) for i in range(size)]
    offsets = [0]
    for s in sizes[:-1]:
        offsets.append(offsets[-1] + s)
    chunks = [data[offsets[i]:offsets[i]+sizes[i]] for i in range(size)]
else:
    chunks = None
    sizes = None

sizes = comm.bcast(sizes, root=0)
local = comm.scatter(chunks, root=0)

local_sum = sum(x*x for x in local)
partials = comm.gather(local_sum, root=0)

if rank == 0:
    total = sum(partials)
    print(f"sizes={sizes}")
    print(f"partials={partials}")
    print(f"total={total}")
