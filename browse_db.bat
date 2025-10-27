@echo off
echo ================================================================================
echo DATABASE BROWSER - MPI Payroll System
echo ================================================================================
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run database browser
python browse_database.py

echo.
echo Press any key to exit...
pause >nul
