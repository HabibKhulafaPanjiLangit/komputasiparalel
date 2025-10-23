import csv, random, os
random.seed(42)

path = r"D:\data\sample.csv"
os.makedirs(os.path.dirname(path), exist_ok=True)  # auto-buat folder D:\data

N = 1000  # jumlah baris data
with open(path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "group", "value"])  # header
    for i in range(N):
        w.writerow([i, i % 10, round(random.uniform(0, 100), 3)])

print("CSV created:", path)
