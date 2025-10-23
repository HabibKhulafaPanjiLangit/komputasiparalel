from mpi4py import MPI  # type: ignore
import random
import time
from dataclasses import dataclass, asdict
from typing import List
import csv
import os

# Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

@dataclass
class Employee:
    id: int
    name: str
    base_salary: float
    overtime_hours: float = 0.0
    bonus: float = 0.0
    deductions: float = 0.0
    total_salary: float = 0.0

class PayrollSystemMPI:
    def __init__(self):
        self.employees: List[Employee] = []
        self.overtime_rate = 1.5  # 150% dari gaji per jam
        self.work_hours_per_month = 160  # 8 jam x 20 hari
    
    def add_employee(self, name: str, base_salary: float):
        """Hanya rank 0 yang menambahkan karyawan"""
        if rank == 0:
            emp = Employee(
                id=len(self.employees) + 1,
                name=name,
                base_salary=base_salary
            )
            self.employees.append(emp)
            print(f"[OK] Karyawan '{name}' berhasil ditambahkan (ID: {emp.id})")
    
    def update_overtime(self, emp_id: int, hours: float):
        if rank == 0:
            if 0 < emp_id <= len(self.employees):
                self.employees[emp_id - 1].overtime_hours = hours
                print(f"[OK] Lembur diupdate untuk ID {emp_id}")
            else:
                print("[X] ID karyawan tidak ditemukan!")
    
    def update_bonus(self, emp_id: int, bonus: float):
        if rank == 0:
            if 0 < emp_id <= len(self.employees):
                self.employees[emp_id - 1].bonus = bonus
                print(f"[OK] Bonus diupdate untuk ID {emp_id}")
            else:
                print("[X] ID karyawan tidak ditemukan!")
    
    def update_deductions(self, emp_id: int, deductions: float):
        if rank == 0:
            if 0 < emp_id <= len(self.employees):
                self.employees[emp_id - 1].deductions = deductions
                print(f"[OK] Potongan diupdate untuk ID {emp_id}")
            else:
                print("[X] ID karyawan tidak ditemukan!")
    
    def _calculate_single_salary(self, emp: Employee) -> Employee:
        """Hitung gaji satu karyawan"""
        # Hitung gaji per jam
        hourly_rate = emp.base_salary / self.work_hours_per_month
        
        # Hitung uang lembur
        overtime_pay = emp.overtime_hours * hourly_rate * self.overtime_rate
        
        # Total gaji = gaji pokok + lembur + bonus - potongan
        emp.total_salary = emp.base_salary + overtime_pay + emp.bonus - emp.deductions
        
        return emp
    
    def calculate_all_salaries_parallel(self):
        """Hitung gaji semua karyawan dengan MPI parallelization"""
        
        # Rank 0 memiliki data dan mendistribusikan ke worker processes
        if rank == 0:
            t0 = time.perf_counter()
            num_employees = len(self.employees)
            
            if num_employees == 0:
                print("Tidak ada karyawan untuk dihitung!")
                # Broadcast None untuk memberitahu worker tidak ada pekerjaan
                for i in range(1, size):
                    comm.send(None, dest=i, tag=0)
                return
            
            print(f"[Rank {rank}] Mendistribusikan {num_employees} karyawan ke {size} proses...")
            
            # Bagi pekerjaan ke semua proses (termasuk rank 0)
            employees_per_process = num_employees // size
            remainder = num_employees % size
            
            # Distribusi data ke worker processes
            start_idx = 0
            for i in range(size):
                # Proses yang lebih awal mendapat 1 extra jika ada remainder
                count = employees_per_process + (1 if i < remainder else 0)
                end_idx = start_idx + count
                
                if i == 0:
                    # Rank 0 memproses bagiannya sendiri
                    local_employees = self.employees[start_idx:end_idx]
                else:
                    # Kirim ke worker processes
                    chunk = self.employees[start_idx:end_idx]
                    comm.send(chunk, dest=i, tag=0)
                
                start_idx = end_idx
            
            # Rank 0 memproses bagiannya
            for i, emp in enumerate(local_employees):
                local_employees[i] = self._calculate_single_salary(emp)
            
            # Kumpulkan hasil dari semua worker processes
            all_results = [local_employees]
            for i in range(1, size):
                results = comm.recv(source=i, tag=1)
                all_results.append(results)
            
            # Gabungkan semua hasil
            processed_idx = 0
            for result_chunk in all_results:
                for emp in result_chunk:
                    self.employees[processed_idx] = emp
                    processed_idx += 1
            
            t1 = time.perf_counter()
            print(f"[OK] Gaji {num_employees} karyawan berhasil dihitung (MPI Parallel, {t1-t0:.3f}s)")
            print(f"  Menggunakan {size} proses MPI")
        
        else:
            # Worker processes
            # Terima data dari rank 0
            employees_chunk = comm.recv(source=0, tag=0)
            
            if employees_chunk is None:
                return  # Tidak ada pekerjaan
            
            # Proses data
            results = []
            for emp in employees_chunk:
                results.append(self._calculate_single_salary(emp))
            
            # Kirim hasil kembali ke rank 0
            comm.send(results, dest=0, tag=1)
    
    def calculate_all_salaries_serial(self):
        """Hitung gaji secara serial (hanya rank 0)"""
        if rank == 0:
            t0 = time.perf_counter()
            num_employees = len(self.employees)
            
            if num_employees == 0:
                print("Tidak ada karyawan untuk dihitung!")
                return
            
            for i in range(num_employees):
                self.employees[i] = self._calculate_single_salary(self.employees[i])
            
            t1 = time.perf_counter()
            print(f"[OK] Gaji {num_employees} karyawan berhasil dihitung (Serial, {t1-t0:.3f}s)")
    
    def display_all_payroll(self):
        """Tampilkan slip gaji semua karyawan (hanya rank 0)"""
        if rank != 0:
            return
        
        if not self.employees:
            print("Tidak ada data karyawan!")
            return
        
        print("\n" + "="*80)
        print(" "*25 + "DAFTAR GAJI KARYAWAN")
        print("="*80)
        print(f"{'ID':<5} {'Nama':<20} {'Gaji Pokok':>12} {'Lembur':>10} {'Bonus':>10} {'Potongan':>10} {'Total':>12}")
        print("-"*80)
        
        total_payroll = 0.0
        for emp in self.employees:
            hourly_rate = emp.base_salary / self.work_hours_per_month
            overtime_pay = emp.overtime_hours * hourly_rate * self.overtime_rate
            
            print(f"{emp.id:<5} {emp.name:<20} {emp.base_salary:>12,.0f} {overtime_pay:>10,.0f} "
                  f"{emp.bonus:>10,.0f} {emp.deductions:>10,.0f} {emp.total_salary:>12,.0f}")
            total_payroll += emp.total_salary
        
        print("-"*80)
        print(f"{'TOTAL PAYROLL':>66} {total_payroll:>12,.0f}")
        print("="*80 + "\n")
    
    def generate_sample_data(self, count: int = 100):
        """Generate data karyawan sample untuk testing (hanya rank 0)"""
        if rank != 0:
            return
        
        names = ["Andi", "Budi", "Citra", "Dewi", "Eko", "Fitri", "Gani", "Hana", "Indra", "Joko"]
        
        for i in range(count):
            name = f"{random.choice(names)} {i+1}"
            base_salary = random.uniform(5_000_000, 20_000_000)
            overtime = random.uniform(0, 20)
            bonus = random.uniform(0, 2_000_000) if random.random() > 0.5 else 0
            deductions = random.uniform(100_000, 500_000)
            
            emp = Employee(
                id=len(self.employees) + 1,
                name=name,
                base_salary=base_salary,
                overtime_hours=overtime,
                bonus=bonus,
                deductions=deductions
            )
            self.employees.append(emp)
        
        print(f"[OK] {count} data karyawan sample berhasil dibuat")
    
    def save_to_csv(self, filename: str):
        """Simpan data ke CSV (hanya rank 0)"""
        if rank != 0:
            return
        
        if not self.employees:
            print("Tidak ada data untuk disimpan!")
            return
        
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['id', 'name', 'base_salary', 'overtime_hours', 'bonus', 'deductions', 'total_salary']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for emp in self.employees:
                writer.writerow(asdict(emp))
        
        print(f">> Data berhasil disimpan ke '{filename}'")
    
    def load_from_csv(self, filename: str):
        """Muat data dari CSV (hanya rank 0)"""
        if rank != 0:
            return
        
        if not os.path.exists(filename):
            print(f">> File '{filename}' tidak ditemukan!")
            return
        
        self.employees = []
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                emp = Employee(
                    id=int(row['id']),
                    name=row['name'],
                    base_salary=float(row['base_salary']),
                    overtime_hours=float(row['overtime_hours']),
                    bonus=float(row['bonus']),
                    deductions=float(row['deductions']),
                    total_salary=float(row['total_salary'])
                )
                self.employees.append(emp)
        
        print(f">> {len(self.employees)} data karyawan berhasil dimuat dari '{filename}'")

def show_menu():
    if rank == 0:
        print("\n" + "="*50)
        print(" "*8 + "SISTEM PENGGAJIAN KARYAWAN (MPI)")
        print("="*50)
        print("1. Tambah Karyawan")
        print("2. Update Lembur")
        print("3. Update Bonus")
        print("4. Update Potongan")
        print("5. Hitung Semua Gaji (Serial)")
        print("6. Hitung Semua Gaji (Parallel MPI)")
        print("7. Tampilkan Slip Gaji")
        print("8. Generate Data Sample")
        print("9. Simpan ke CSV")
        print("10. Muat dari CSV")
        print("0. Keluar")
        print("="*50)
        print(f"INFO: Running dengan {size} proses MPI")

def main():
    payroll = PayrollSystemMPI()
    
    while True:
        show_menu()
        
        # Hanya rank 0 yang membaca input
        if rank == 0:
            choice = input("Pilih menu (0-10): ").strip()
        else:
            choice = None
        
        # Broadcast pilihan ke semua proses
        choice = comm.bcast(choice, root=0)
        
        if choice == "1":
            if rank == 0:
                name = input("Nama karyawan: ").strip()
                try:
                    salary = float(input("Gaji pokok: "))
                    payroll.add_employee(name, salary)
                except ValueError:
                    print("✗ Input gaji tidak valid!")
        
        elif choice == "2":
            if rank == 0:
                try:
                    emp_id = int(input("ID karyawan: "))
                    hours = float(input("Jam lembur: "))
                    payroll.update_overtime(emp_id, hours)
                except ValueError:
                    print("✗ Input tidak valid!")
        
        elif choice == "3":
            if rank == 0:
                try:
                    emp_id = int(input("ID karyawan: "))
                    bonus = float(input("Bonus: "))
                    payroll.update_bonus(emp_id, bonus)
                except ValueError:
                    print("✗ Input tidak valid!")
        
        elif choice == "4":
            if rank == 0:
                try:
                    emp_id = int(input("ID karyawan: "))
                    deductions = float(input("Potongan: "))
                    payroll.update_deductions(emp_id, deductions)
                except ValueError:
                    print("✗ Input tidak valid!")
        
        elif choice == "5":
            payroll.calculate_all_salaries_serial()
        
        elif choice == "6":
            payroll.calculate_all_salaries_parallel()
        
        elif choice == "7":
            payroll.display_all_payroll()
        
        elif choice == "8":
            if rank == 0:
                try:
                    count = int(input("Jumlah data sample (default 1000): ") or "1000")
                    payroll.generate_sample_data(count)
                except ValueError:
                    print("✗ Input tidak valid!")
        
        elif choice == "9":
            if rank == 0:
                filename = input("Nama file CSV (default: payroll_data.csv): ").strip() or "payroll_data.csv"
                payroll.save_to_csv(filename)
        
        elif choice == "10":
            if rank == 0:
                filename = input("Nama file CSV (default: payroll_data.csv): ").strip() or "payroll_data.csv"
                payroll.load_from_csv(filename)
        
        elif choice == "0":
            if rank == 0:
                print("\nTerima kasih! Program selesai.")
            break
        
        else:
            if rank == 0:
                print("✗ Pilihan tidak valid!")

if __name__ == "__main__":
    main()
