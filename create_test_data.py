import csv
import os

# Konfigurasi
output_dir = r"D:\data\big_split"
num_files = 4  # Sesuaikan dengan jumlah proses MPI yang akan digunakan
rows_per_file = 10000

# Buat folder jika belum ada
os.makedirs(output_dir, exist_ok=True)

for file_idx in range(num_files):
    filepath = os.path.join(output_dir, f"big_{file_idx}.csv")
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Header
        writer.writerow(["id", "name", "value"])
        
        # Data
        for row_idx in range(rows_per_file):
            writer.writerow([
                file_idx * rows_per_file + row_idx,
                f"item_{row_idx}",
                100.0 + (row_idx % 100)
            ])
    
    print(f"Created: {filepath}")

print(f"\nTotal files created: {num_files}")
print(f"Rows per file: {rows_per_file}")
