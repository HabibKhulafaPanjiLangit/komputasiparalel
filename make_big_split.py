import csv
import random
import os

# === KONFIGURASI ===
OUTDIR = r"D:\data\big_split"   # folder tujuan
P = 8                           # jumlah file yang mau dibuat
N = 1_000_000                   # total baris data
# ====================

random.seed(42)
os.makedirs(OUTDIR, exist_ok=True)

writers = []
files = []

# buat P file kosong
for i in range(P):
    filename = os.path.join(OUTDIR, f"big_{i}.csv")
    f = open(filename, "w", newline="", encoding="utf-8")
    writer = csv.writer(f)
    writer.writerow(["id", "group", "value"])  # header
    files.append(f)
    writers.append(writer)

# isi data acak ke masing-masing file
for i in range(N):
    part = i % P                   # pilih file ke-berapa
    writers[part].writerow([
        i,                         # id unik
        i % 10,                    # contoh kolom kategori
        round(random.uniform(0, 100), 6)  # nilai acak 0–100
    ])

# tutup semua file
for f in files:
    f.close()

print(f"Selesai! Dibuat {P} file di {OUTDIR} total {N} baris.")
