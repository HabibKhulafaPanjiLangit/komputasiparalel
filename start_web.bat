@echo off
REM Script untuk menjalankan Web Dashboard MPI
echo.
echo ============================================================
echo   Starting MPI Payroll System Web Dashboard
echo ============================================================
echo.
echo Web server akan berjalan di: http://localhost:5000
echo Tekan Ctrl+C untuk berhenti
echo.

REM Jalankan dengan Python dari venv
D:\mpi-demo\.venv\Scripts\python.exe web_server.py

pause
