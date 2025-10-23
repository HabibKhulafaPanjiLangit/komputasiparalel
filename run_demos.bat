@echo off
REM Batch script untuk menjalankan demo MPI di Windows
REM Cara menggunakan: run_demos.bat

echo.
echo ========================================
echo   MPI DEMO RUNNER - PYTHON PROGRAMS
echo ========================================
echo.

echo Pilih program yang ingin dijalankan:
echo 1. Monte Carlo Pi (Speedup 4.81x)
echo 2. Demo Payroll Otomatis
echo 3. Benchmark Payroll Kompleks (Speedup 3.34x)
echo 4. Benchmark Payroll Sederhana
echo 5. Program Payroll Interaktif
echo 6. Jalankan Semua Demo
echo 0. Keluar
echo.

set /p choice="Masukkan pilihan (0-6): "

if "%choice%"=="1" (
    echo.
    echo [Running] Monte Carlo Pi Calculation...
    mpiexec -n 4 python pi_montecarlo_mpi.py
) else if "%choice%"=="2" (
    echo.
    echo [Running] Demo Payroll Otomatis...
    mpiexec -n 4 python demo_payroll_mpi.py
) else if "%choice%"=="3" (
    echo.
    echo [Running] Benchmark Payroll Kompleks...
    mpiexec -n 4 python demo_payroll_complex.py
) else if "%choice%"=="4" (
    echo.
    echo [Running] Benchmark Payroll Sederhana...
    mpiexec -n 4 python demo_payroll_benchmark.py
) else if "%choice%"=="5" (
    echo.
    echo [Running] Program Payroll Interaktif...
    mpiexec -n 4 python payroll_full_mpi.py
) else if "%choice%"=="6" (
    echo.
    echo [Running] Semua Demo...
    echo.
    
    echo === 1. Monte Carlo Pi ===
    mpiexec -n 4 python pi_montecarlo_mpi.py
    
    echo.
    echo === 2. Demo Payroll Otomatis ===
    mpiexec -n 4 python demo_payroll_mpi.py
    
    echo.
    echo === 3. Benchmark Payroll Kompleks ===
    mpiexec -n 4 python demo_payroll_complex.py
    
    echo.
    echo Semua demo selesai!
) else if "%choice%"=="0" (
    echo Keluar...
) else (
    echo Pilihan tidak valid!
)

echo.
pause
