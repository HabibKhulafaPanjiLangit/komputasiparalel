@echo off
REM MPI Payroll Interactive - Mode Parallel (4 proses)
echo ================================================
echo   MPI PAYROLL SYSTEM - INTERACTIVE MODE
echo   Running in PARALLEL mode (4 processes)
echo ================================================
echo.

mpiexec -n 4 D:\mpi-demo\.venv\Scripts\python.exe payroll_interactive.py

pause
