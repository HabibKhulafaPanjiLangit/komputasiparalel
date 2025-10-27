"""
Payroll Demo - Serial Version (No MPI Required)
Demo sistem penggajian dengan data dummy - bisa jalan di production
"""

import random
from datetime import datetime, timedelta

def generate_dummy_employees(num=100):
    """Generate dummy employee data"""
    jabatan_list = ["Manager", "Supervisor", "Staff Senior", "Staff", "Operator"]
    nama_depan = ["Andi", "Budi", "Citra", "Deni", "Eka", "Fajar", "Gita", "Hadi", "Indra", "Joko"]
    nama_belakang = ["Pratama", "Wijaya", "Santoso", "Permana", "Saputra"]
    
    employees = []
    for i in range(num):
        emp = {
            'id': f'EMP{i+1:04d}',
            'nama': f"{random.choice(nama_depan)} {random.choice(nama_belakang)}",
            'jabatan': random.choice(jabatan_list),
            'gaji_pokok': random.randint(50, 200) * 10000,
            'hari_kerja': random.randint(20, 26)
        }
        employees.append(emp)
    
    return employees

def calculate_salary_serial(employees):
    """Calculate salary for all employees (serial version)"""
    results = []
    
    for emp in employees:
        total_gaji = emp['gaji_pokok'] * emp['hari_kerja']
        
        result = {
            'id': emp['id'],
            'nama': emp['nama'],
            'jabatan': emp['jabatan'],
            'gaji_pokok': emp['gaji_pokok'],
            'hari_kerja': emp['hari_kerja'],
            'total_gaji': total_gaji
        }
        results.append(result)
    
    return results

def main():
    """Main execution"""
    print("="*70)
    print("DEMO PAYROLL SYSTEM - SERIAL VERSION")
    print("="*70)
    
    # Generate dummy data
    print("\n[1/3] Generating dummy employee data...")
    num_employees = 10000
    employees = generate_dummy_employees(num_employees)
    print(f"      Created {len(employees)} employees")
    
    # Calculate salary
    print("\n[2/3] Calculating salaries...")
    start_time = datetime.now()
    results = calculate_salary_serial(employees)
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    
    print(f"      Processed {len(results)} records")
    print(f"      Elapsed time: {elapsed:.3f} seconds")
    
    # Show sample results
    print("\n[3/3] Sample Results (first 5):")
    print("-"*70)
    for i, result in enumerate(results[:5], 1):
        print(f"{i}. {result['nama']} ({result['jabatan']})")
        print(f"   Gaji Pokok: Rp {result['gaji_pokok']:,}")
        print(f"   Hari Kerja: {result['hari_kerja']} hari")
        print(f"   Total Gaji: Rp {result['total_gaji']:,}")
        print()
    
    # Statistics
    total_salary = sum(r['total_gaji'] for r in results)
    avg_salary = total_salary / len(results)
    
    print("="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    print(f"Total Employees:  {len(results):,}")
    print(f"Total Salary:     Rp {total_salary:,}")
    print(f"Average Salary:   Rp {avg_salary:,.0f}")
    print(f"Processing Time:  {elapsed:.3f} seconds")
    print(f"Throughput:       {len(results)/elapsed:,.0f} records/second")
    print("="*70)

if __name__ == '__main__':
    main()
