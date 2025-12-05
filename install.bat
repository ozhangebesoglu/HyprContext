@echo off
REM HyprContext Windows - Kurulum Scripti

echo.
echo  ========================================
echo   HyprContext Windows Kurulumu
echo  ========================================
echo.

REM Python kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadi!
    echo.
    echo Python 3.10+ yukleyin:
    echo https://www.python.org/downloads/
    echo.
    echo Kurulum sirasinda "Add Python to PATH" secenegini isaretleyin!
    pause
    exit /b 1
)

echo [OK] Python bulundu
python --version

REM Virtual environment oluştur
echo.
echo [*] Virtual environment olusturuluyor...
python -m venv venv

REM Aktif et
call venv\Scripts\activate.bat

REM Bağımlılıkları yükle
echo.
echo [*] Bagimliliklar yukleniyor...
pip install --upgrade pip
pip install -r requirements.txt

REM .env oluştur
echo.
if not exist ".env" (
    echo [*] Konfigurasyon dosyasi olusturuluyor...
    copy config.example.env .env >nul
    echo [!] .env dosyasi olusturuldu.
)

echo.
echo  ========================================
echo   Kurulum Tamamlandi!
echo  ========================================
echo.
echo Baslatmak icin: run.bat
echo veya: python main.py run
echo.
echo Ollama'nin yuklu ve calisir durumda oldugundan emin olun:
echo https://ollama.ai
echo.
echo Gerekli model: ollama pull gemma3
echo.

pause


