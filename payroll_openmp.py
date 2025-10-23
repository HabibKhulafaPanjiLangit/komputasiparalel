import random
from dataclasses import dataclass
from typing import List

try:
    from omp4py import omp, omp_set_num_threads  # type: ignore
    HAS_OMP = True
except ImportError:
    print("Warning: omp4py not installed. Running in sequential mode.")
    HAS_OMP = False
    def omp(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def omp_set_num_threads(n):
        pass

# Set number of threads
if HAS_OMP:
    omp_set_num_threads(4)

@dataclass
class Employee:
    id: int
    name: str
    base_salary: float
    overtime_hours: float = 0.0
    bonus: float = 0.0
    deductions: float = 0.0
    total_salary: float = 0.0

class PayrollSystem:
    def __init__(self):
        self.employees: List[Employee] = []
        self.overtime_rate = 1.5  # 150% dari gaji per jam
        self.work_hours_per_month = 160  # 8 jam x 20 hari
    
    def add_employee(self, name: str, base_salary: float):
        emp = Employee(
            id=len(self.employees) + 1,
            name=name,
            base_salary=base_salary
        )
        self.employees.append(emp)
        print(f"✓ Karyawan '{name}' berhasil ditambahkan (ID: {emp.id})")
    
    def update_overtime(self, emp_id: int, hours: float):
        if 0 < emp_id <= len(self.employees):
            self.employees[emp_id - 1].overtime_hours = hours
            print(f"✓ Lembur diupdate untuk ID {emp_id}")
        else:
            print("✗ ID karyawan tidak ditemukan!")
    
    def update_bonus(self, emp_id: int, bonus: float):
        if 0 < emp_id <= len(self.employees):
            self.employees[emp_id - 1].bonus = bonus
            print(f"✓ Bonus diupdate untuk ID {emp_id}")
        else:
            print("✗ ID karyawan tidak ditemukan!")
    
    def update_deductions(self, emp_id: int, deductions: float):
        if 0 < emp_id <= len(self.employees):
            self.employees[emp_id - 1].deductions = deductions
            print(f"✓ Potongan diupdate untuk ID {emp_id}")
        else:
            print("✗ ID karyawan tidak ditemukan!")
    
    @omp
    def calculate_all_salaries(self):
        """Hitung gaji semua karyawan dengan paralelisasi OpenMP"""
        import time
        
        t0 = time.perf_counter()
        num_employees = len(self.employees)
        
        if num_employees == 0:
            print("Tidak ada karyawan untuk dihitung!")
            return
        
        if HAS_OMP:
            # Parallel calculation
            with omp("parallel for"):
                for i in range(num_employees):
                    self._calculate_single_salary(i)
        else:
            # Sequential fallback
            for i in range(num_employees):
                self._calculate_single_salary(i)
        
        t1 = time.perf_counter()
        mode = "Parallel (OpenMP)" if HAS_OMP else "Sequential"
        print(f"✓ Gaji {num_employees} karyawan berhasil dihitung ({mode}, {t1-t0:.3f}s)")
    
    def _calculate_single_salary(self, index: int):
        """Hitung gaji satu karyawan"""
        emp = self.employees[index]
        
        # Hitung gaji per jam
        hourly_rate = emp.base_salary / self.work_hours_per_month
        
        # Hitung uang lembur
        overtime_pay = emp.overtime_hours * hourly_rate * self.overtime_rate
        
        # Total gaji = gaji pokok + lembur + bonus - potongan
        emp.total_salary = emp.base_salary + overtime_pay + emp.bonus - emp.deductions
    
    def display_all_payroll(self):
        """Tampilkan slip gaji semua karyawan"""
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
        """Generate data karyawan sample untuk testing"""
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
        
        print(f"✓ {count} data karyawan sample berhasil dibuat")

def show_menu():
    print("\n" + "="*50)
    print(" "*10 + "SISTEM PENGGAJIAN KARYAWAN")
    print("="*50)
    print("1. Tambah Karyawan")
    print("2. Update Lembur")
    print("3. Update Bonus")
    print("4. Update Potongan")
    print("5. Hitung Semua Gaji (Parallel)")
    print("6. Tampilkan Slip Gaji")
    print("7. Generate Data Sample")
    print("0. Keluar")
    print("="*50)

def main():
    payroll = PayrollSystem()
    
    while True:
        show_menu()
        choice = input("Pilih menu (0-7): ").strip()
        
        if choice == "1":
            name = input("Nama karyawan: ").strip()
            try:
                salary = float(input("Gaji pokok: "))
                payroll.add_employee(name, salary)
            except ValueError:
                print("✗ Input gaji tidak valid!")
        
        elif choice == "2":
            try:
                emp_id = int(input("ID karyawan: "))
                hours = float(input("Jam lembur: "))
                payroll.update_overtime(emp_id, hours)
            except ValueError:
                print("✗ Input tidak valid!")
        
        elif choice == "3":
            try:
                emp_id = int(input("ID karyawan: "))
                bonus = float(input("Bonus: "))
                payroll.update_bonus(emp_id, bonus)
            except ValueError:
                print("✗ Input tidak valid!")
        
        elif choice == "4":
            try:
                emp_id = int(input("ID karyawan: "))
                deductions = float(input("Potongan: "))
                payroll.update_deductions(emp_id, deductions)
            except ValueError:
                print("✗ Input tidak valid!")
        
        elif choice == "5":
            payroll.calculate_all_salaries()
        
        elif choice == "6":
            payroll.display_all_payroll()
        
        elif choice == "7":
            try:
                count = int(input("Jumlah data sample (default 100): ") or "100")
                payroll.generate_sample_data(count)
            except ValueError:
                print("✗ Input tidak valid!")
        
        elif choice == "0":
            print("\nTerima kasih! Program selesai.")
            break
        
        else:
            print("✗ Pilihan tidak valid!")

if __name__ == "__main__":
    main()
