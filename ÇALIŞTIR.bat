@echo off
REM ============ HEMŞIRE HASTA TAKIP SİSTEMİ - BAŞLATICI ============
REM Uygulamayı başlatmak için bu dosyayı çalıştırın
REM Created: 29.03.2026

setlocal enabledelayedexpansion

REM Başlatma dizinini kontrol et
if not exist "Hastaodaları.py" (
    echo HATA: Hastaodaları.py dosyası bulunamadı!
    echo Bu dosyayı proje klasöründen çalıştırın.
    pause
    exit /b 1
)

REM Virtual environment kontrol et
if not exist ".venv" (
    echo UYARI: Virtual environment bulunamadı!
    echo .venv klasörü oluşturuluyor...
    python -m venv .venv
    if !errorlevel! neq 0 (
        echo HATA: Virtual environment oluşturulamadı!
        echo Python yüklü olduğundan emin olun.
        pause
        exit /b 1
    )
)

REM Bağımlılıkları kontrol et ve yükle
echo Bağımlılıklar kontrol ediliyor...
.\.venv\Scripts\python.exe -m pip install -q -r requirements.txt 2>nul

if !errorlevel! neq 0 (
    echo UYARI: Bağımlılıklar yüklenirken bir sorun oluştu.
    echo Yükleme deneniyor...
    .\.venv\Scripts\pip.exe install PySide6==6.11.0 python-docx==1.2.0
)

echo.
echo Uygulamayı başlatıyorum...
echo.

REM Uygulamayı çalıştır
.\.venv\Scripts\python.exe Hastaodaları.py

if !errorlevel! neq 0 (
    echo.
    echo HATA: Uygulama çıkış kodunu geri döndü: !errorlevel!
    echo Ayrıntılar için hastaodasi.log dosyasını kontrol edin.
    pause
)

endlocal
