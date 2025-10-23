import csv, random, os
random.seed(42)

path = r"D:\data\big.csv"
os.makedirs(os.path.dirname(path), exist_ok=True)  # buat folder otomatis kalau belum ada

N = 1_000_000  # jumlah baris data
with open(path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id","group","value"])
    for i in range(N):
        w.writerow([i, i % 10, round(random.uniform(0, 100), 6)])

print("CSV created:", path)
