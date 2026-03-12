@echo off
chcp 65001 >nul
color 0A

echo.
echo ========================================
echo   FACE SWAP PROFESSIONAL - SETUP
echo ========================================
echo.

python --version
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not installed!
    pause
    exit /b 1
)

echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo Run: python gui_professional.py
echo.
pause