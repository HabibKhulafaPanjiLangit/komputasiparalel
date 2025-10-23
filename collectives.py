from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Rank 0 broadcast angka awal
init = 10 if rank == 0 else None
init = comm.bcast(init, root=0)

# Tiap rank bikin nilai lokal (contoh sederhana)
local = init + rank

# Reduce: jumlahkan semua ke rank 0
total = comm.reduce(local, op=MPI.SUM, root=0)

if rank == 0:
    print(f"init={init}, size={size}, total_sum={total}")
