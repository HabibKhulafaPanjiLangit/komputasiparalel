from mpi4py import MPI  # type: ignore

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    msg = "Halo dari rank 0 -> 1"
    comm.send(msg, dest=1, tag=42)
    print(f"[{rank}] sent to 1: {msg}")

elif rank == 1:
    incoming = comm.recv(source=0, tag=42)
    print(f"[{rank}] received from 0: {incoming}")
