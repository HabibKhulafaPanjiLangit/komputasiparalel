"""
Demo otomatis untuk membandingkan performa Serial vs Parallel MPI
pada sistem penggajian karyawan
"""

from payroll_mpi import PayrollSystemMPI, rank
import time

def demo():
    payroll = PayrollSystemMPI()
    
    # Generate sample data
    if rank == 0:
        print("\n" + "="*60)
        print("   DEMO: PERBANDINGAN SERIAL VS PARALLEL MPI")
        print("="*60)
        print("\n>> Generating 10,000 sample employees...")
    
    payroll.generate_sample_data(10000)
    
    if rank == 0:
        print("\n" + "-"*60)
        print(">> TEST 1: SERIAL CALCULATION")
        print("-"*60)
    
    payroll.calculate_all_salaries_serial()
    
    if rank == 0:
        print("\n" + "-"*60)
        print(">> TEST 2: PARALLEL MPI CALCULATION")
        print("-"*60)
    
    payroll.calculate_all_salaries_parallel()
    
    if rank == 0:
        print("\n" + "-"*60)
        print(">> Displaying first 10 employees:")
        print("-"*60)
        
        # Display only first 10
        temp_employees = payroll.employees[:10]
        original_employees = payroll.employees
        payroll.employees = temp_employees
        payroll.display_all_payroll()
        payroll.employees = original_employees
        
        print("\n" + "="*60)
        print(">> DEMO COMPLETED!")
        print(f"   Total employees processed: {len(payroll.employees)}")
        print("="*60)

if __name__ == "__main__":
    demo()
