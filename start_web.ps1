# Script PowerShell untuk menjalankan Web Dashboard
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  Starting MPI Payroll System Web Dashboard" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Web server akan berjalan di: " -NoNewline
Write-Host "http://localhost:5000" -ForegroundColor Green
Write-Host "Tekan Ctrl+C untuk berhenti`n"

# Jalankan dengan Python dari venv
& D:\mpi-demo\.venv\Scripts\python.exe web_server.py
