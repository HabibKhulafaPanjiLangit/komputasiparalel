# Script PowerShell untuk menjalankan semua demo MPI
# Cara menggunakan: .\run_demos.ps1

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  MPI DEMO RUNNER - PYTHON PROGRAMS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Pilih program yang ingin dijalankan:" -ForegroundColor Yellow
Write-Host "1. Monte Carlo Pi (Speedup 4.81x)"
Write-Host "2. Demo Payroll Otomatis"
Write-Host "3. Benchmark Payroll Kompleks (Speedup 3.34x)"
Write-Host "4. Benchmark Payroll Sederhana"
Write-Host "5. Program Payroll Interaktif"
Write-Host "6. Jalankan Semua Demo"
Write-Host "0. Keluar`n"

$choice = Read-Host "Masukkan pilihan (0-6)"

switch ($choice) {
    "1" {
        Write-Host "`n[Running] Monte Carlo Pi Calculation..." -ForegroundColor Green
        mpiexec -n 4 python pi_montecarlo_mpi.py
    }
    "2" {
        Write-Host "`n[Running] Demo Payroll Otomatis..." -ForegroundColor Green
        mpiexec -n 4 python demo_payroll_mpi.py
    }
    "3" {
        Write-Host "`n[Running] Benchmark Payroll Kompleks..." -ForegroundColor Green
        mpiexec -n 4 python demo_payroll_complex.py
    }
    "4" {
        Write-Host "`n[Running] Benchmark Payroll Sederhana..." -ForegroundColor Green
        mpiexec -n 4 python demo_payroll_benchmark.py
    }
    "5" {
        Write-Host "`n[Running] Program Payroll Interaktif..." -ForegroundColor Green
        mpiexec -n 4 python payroll_full_mpi.py
    }
    "6" {
        Write-Host "`n[Running] Semua Demo...`n" -ForegroundColor Green
        
        Write-Host "`n=== 1. Monte Carlo Pi ===" -ForegroundColor Cyan
        mpiexec -n 4 python pi_montecarlo_mpi.py
        
        Write-Host "`n`n=== 2. Demo Payroll Otomatis ===" -ForegroundColor Cyan
        mpiexec -n 4 python demo_payroll_mpi.py
        
        Write-Host "`n`n=== 3. Benchmark Payroll Kompleks ===" -ForegroundColor Cyan
        mpiexec -n 4 python demo_payroll_complex.py
        
        Write-Host "`nSemua demo selesai!" -ForegroundColor Green
    }
    "0" {
        Write-Host "`nKeluar..." -ForegroundColor Yellow
    }
    default {
        Write-Host "`nPilihan tidak valid!" -ForegroundColor Red
    }
}

Write-Host "`n"
