"""
Hemşire Hasta Takip Sistemi - Yapılandırma Dosyası
Uygulamanın merkezi ayarlarını içerir
"""

import os

# ============ UYGULAMA BİLGİLERİ ============
APP_NAME = "Hemşire Hasta Takip Sistemi"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Sağlık Bilişimi Ekibi"
APP_DATE = "29.03.2026"

# ============ VERİ DOSYALARI ============
DATA_FILE = "hastalar.json"
ROOM_SETTINGS_FILE = "room_settings.json"
BACKUP_DIR = "Yedekler"
LOG_FILE = "hastaodasi.log"

# ============ PENCERE AYARLARI ============
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750
WINDOW_TITLE = "Hemşire Hasta Takip Sistemi"

# ============ ODA AYARLARI ============
TOTAL_ROOMS = 16
MAX_PATIENTS_PER_ROOM = 2

# ============ TARİH VE SAAT FORMATLARI ============
DATE_FORMAT = "%d.%m.%Y %H:%M"
DATE_FORMAT_BACKUP = "%d_%m_%Y"

# ============ STIL SABİTLERİ (RENKLER) ============
COLORS = {
    "bg_dark": "#2b2d31",
    "bg_darker": "#1e1f22",
    "text_main": "#dbdee1",
    "text_muted": "#a6a6a6",
    "text_error": "#ff4d4d",
    "accent": "#5865F2",
    "success": "#238636",
    "warning": "#d29922",
    "danger": "#da3633",
    "orange": "#b35900",
    "blue": "#005A9E"
}

# ============ NOT TÜRLERİ ============
NOTE_TYPES = [
    "Muayene",
    "İlaç",
    "Ameliyat Öncesi Hazırlık",
    "Tıbbi İşlem",
    "Diğer"
]

NOTE_COLORS = {
    "Muayene": "#005A9E",
    "İlaç": "#238636",
    "Ameliyat Öncesi Hazırlık": "#b35900",
    "Tıbbi İşlem": "#d29922",
    "Diğer": "#404249"
}

# ============ CİNSİYET SEÇENEKLERİ ============
GENDERS = ["Erkek", "Kadın"]

# ============ GÖSTERİM AYARLARI ============
SHOW_DOCTOR_IN_LIST = True
SHOW_TOOLTIPS = True

# ============ HASTA UYARI YARDIMCISI ============
def get_patient_alerts(p):
    """Hasta uyarılarını yapılandırılmış liste olarak döndür."""
    alerts = []
    if p.get("allergy"):
        text = p.get("allergy_type", "")
        alerts.append({"emoji": "🩸", "label": "Alerjisi Var", "detail": text, "key": "allergy"})
    if p.get("isolation"):
        text = p.get("isolation_reason", "")
        alerts.append({"emoji": "🔒", "label": "İzole Hasta", "detail": text, "key": "isolation"})
    if p.get("fasting"):
        alerts.append({"emoji": "🚫", "label": "Aç Kalma (NPO)", "detail": "", "key": "fasting"})
    if p.get("fall_risk"):
        alerts.append({"emoji": "⚠️", "label": "Düşme Riski", "detail": "", "key": "fall_risk"})
    if p.get("dressing"):
        text = p.get("dressing_type", "")
        alerts.append({"emoji": "🩹", "label": "Pansuman Gerekli", "detail": text, "key": "dressing"})
    return alerts

# ============ OTOMATİK AYARLAR ============
# Yedek klasörünü oluştur (eğer yoksa)
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)
