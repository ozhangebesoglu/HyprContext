@echo off
REM HyprContext Windows - Kolay Başlatma Scripti

echo.
echo  ========================================
echo   HyprContext Windows
echo   Yapay Zeka Destekli Aktivite Izleyici
echo  ========================================
echo.

REM Python kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadi!
    echo Python 3.10+ yukleyin: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Virtual environment kontrolü
if not exist "venv" (
    echo [*] Virtual environment olusturuluyor...
    python -m venv venv
)

REM Aktif et
call venv\Scripts\activate.bat

REM Bağımlılıkları kontrol et
pip show typer >nul 2>&1
if errorlevel 1 (
    echo [*] Bagimliliklar yukleniyor...
    pip install -r requirements.txt
)

REM .env kontrolü
if not exist ".env" (
    echo [*] .env dosyasi olusturuluyor...
    copy config.example.env .env >nul
    echo [!] .env dosyasini duzenleyin!
    notepad .env
)

REM Başlat
echo.
echo [*] HyprContext baslatiliyor...
echo     Durdurmak icin Ctrl+C
echo.
python main.py run

pause


