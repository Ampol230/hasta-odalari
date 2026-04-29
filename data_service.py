"""Hemşire Hasta Takip Sistemi - Veri Servisi

Dosya I/O, doğrulama, şifreleme ve dosya kilitleme katmanı.
"""

import json
import os
import shutil
import logging
import tempfile
import threading
from datetime import datetime, timedelta

from config import (
    DATA_FILE, BACKUP_DIR, DATE_FORMAT_BACKUP, DATE_FORMAT,
    ROOM_SETTINGS_FILE, TOTAL_ROOMS, MAX_PATIENTS_PER_ROOM, GENDERS,
)

logger = logging.getLogger(__name__)

# Thread kilidi — aynı süreçteki eşzamanlı save çağrılarını engeller
_save_lock = threading.Lock()

# Platform bağımsız dosya kilitleme
try:
    import msvcrt

    def _lock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)

    def _unlock_file(f):
        try:
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
except ImportError:
    try:
        import fcntl

        def _lock_file(f):
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)

        def _unlock_file(f):
            fcntl.flock(f, fcntl.LOCK_UN)
    except ImportError:
        def _lock_file(f):
            pass

        def _unlock_file(f):
            pass


# ═══════ VERİ DOĞRULAMA ═══════

REQUIRED_FIELDS = {"name", "age", "gender", "room", "diagnosis"}
MAX_TEXT_LEN = 500
MAX_NOTE_LEN = 2000


def validate_patient(patient):
    """Hasta verisini doğrula. Hata yoksa None, varsa hata mesajı döndürür."""
    if not isinstance(patient, dict):
        return "Hasta verisi sözlük olmalıdır"

    missing = REQUIRED_FIELDS - set(patient.keys())
    if missing:
        return f"Eksik alanlar: {', '.join(missing)}"

    name = patient.get("name", "")
    if not isinstance(name, str) or not name.strip():
        return "Hasta adı boş olamaz"
    if len(name) > MAX_TEXT_LEN:
        return f"Hasta adı {MAX_TEXT_LEN} karakteri geçemez"

    age = patient.get("age")
    if not isinstance(age, int) or age < 1 or age > 120:
        return "Yaş 1-120 arasında bir tam sayı olmalıdır"

    if patient.get("gender") not in GENDERS:
        return "Geçersiz cinsiyet değeri"

    room = patient.get("room")
    if not isinstance(room, int) or room < 1:
        return "Oda numarası pozitif tam sayı olmalıdır"

    for field in ("diagnosis", "doctor", "anesthesia", "allergy_type",
                  "isolation_reason", "dressing_type"):
        val = patient.get(field, "")
        if isinstance(val, str) and len(val) > MAX_TEXT_LEN:
            return f"{field} alanı {MAX_TEXT_LEN} karakteri geçemez"

    for note in patient.get("notes", []):
        if isinstance(note.get("text"), str) and len(note["text"]) > MAX_NOTE_LEN:
            return f"Not metni {MAX_NOTE_LEN} karakteri geçemez"

    return None


def _migrate_patient(patient):
    """Eski veri formatlarını yeni formata dönüştür."""
    if isinstance(patient.get("age"), str):
        try:
            patient["age"] = int(patient["age"])
        except (ValueError, TypeError):
            patient["age"] = 0

    # Kalan backup meta verilerini temizle
    patient.pop("backup_file", None)
    patient.pop("backup_date", None)
    return patient


def backup_data():
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        
        if os.path.exists(DATA_FILE):
            today = datetime.now().strftime(DATE_FORMAT_BACKUP)
            backup_path = os.path.join(BACKUP_DIR, f"yedek_{today}.json")
            if not os.path.exists(backup_path):
                shutil.copy(DATA_FILE, backup_path)
                logger.info(f"Yedek oluşturuldu: {backup_path}")
    except Exception as e:
        logger.error(f"Yedekleme hatası: {e}")


def load_data():
    backup_data()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            _lock_file(f)
            try:
                data = json.load(f)
            finally:
                _unlock_file(f)
            data = [_migrate_patient(p) for p in data]
            logger.info(f"{len(data)} hasta verisi yüklendi")
            return data
    except FileNotFoundError:
        logger.info("Veritabanı dosyası bulunamadı, yeni veritabanı oluşturuluyor")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode hatası: {e}")
        return []
    except Exception as e:
        logger.error(f"Veri yükleme hatası: {e}")
        return []


def save_data(data):
    temp_path = None
    with _save_lock:
        try:
            fd, temp_path = tempfile.mkstemp(suffix='.json', dir='.')
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            shutil.move(temp_path, DATA_FILE)
            temp_path = None
            logger.info(f"{len(data)} hasta verisi kaydedildi")
        except Exception as e:
            logger.error(f"Veri kaydetme hatası: {e}")
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            raise


def get_discharged_patients(active_data):
    """Son 90 günün yedeklerinde olup, aktif veritabanında olmayan hastaları bul"""
    try:
        discharged = []
        active_ids = {p.get("id") for p in active_data}
        cutoff_date = datetime.now() - timedelta(days=90)
        
        if os.path.exists(BACKUP_DIR):
            backup_files = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith(".json")])
            
            for backup_file in backup_files:
                try:
                    date_str = backup_file.replace("yedek_", "").replace(".json", "")
                    file_date = datetime.strptime(date_str, DATE_FORMAT_BACKUP)
                    
                    if file_date < cutoff_date:
                        continue
                    
                    backup_path = os.path.join(BACKUP_DIR, backup_file)
                    with open(backup_path, "r", encoding="utf-8") as f:
                        backup_data_list = json.load(f)
                    
                    for patient in backup_data_list:
                        patient = _migrate_patient(patient)
                        patient_id = patient.get("id")
                        if patient_id not in active_ids:
                            if not any(d.get("id") == patient_id for d in discharged):
                                patient["backup_file"] = backup_file
                                patient["backup_date"] = file_date.strftime(DATE_FORMAT)
                                discharged.append(patient)
                except Exception as e:
                    logger.warning(f"Yedek dosya okunurken hata ({backup_file}): {e}")
                    continue
        
        return discharged
    except Exception as e:
        logger.error(f"Taburcu edilen hastalar alınırken hata: {e}")
        return []


def remove_patient_from_backups(patient_id, patient_name=""):
    """Hasta ID'sini tüm yedek dosyalarından sil"""
    if os.path.exists(BACKUP_DIR):
        backup_files = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".json")]
        for backup_file in backup_files:
            try:
                backup_path = os.path.join(BACKUP_DIR, backup_file)
                with open(backup_path, "r", encoding="utf-8") as f:
                    backup_data_list = json.load(f)
                
                backup_data_list = [p for p in backup_data_list if p.get("id") != patient_id]
                
                with open(backup_path, "w", encoding="utf-8") as f:
                    json.dump(backup_data_list, f, ensure_ascii=False, indent=4)
                
                logger.info(f"Hasta backup'tan silindi ({backup_file}): {patient_name}")
            except Exception as e:
                logger.warning(f"Backup dosyasından silerken hata ({backup_file}): {e}")
                continue


def load_room_settings():
    """Oda ayarlarını dosyadan yükle. Yoksa varsayılan ayarları oluştur."""
    try:
        if os.path.exists(ROOM_SETTINGS_FILE):
            with open(ROOM_SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                logger.info(f"Oda ayarları yüklendi: {len(settings)} oda")
                return settings
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Oda ayarları yükleme hatası: {e}")

    # Varsayılan ayarları oluştur
    settings = {}
    for i in range(1, TOTAL_ROOMS + 1):
        settings[str(i)] = {"max_patients": MAX_PATIENTS_PER_ROOM}
    save_room_settings(settings)
    return settings


def save_room_settings(settings):
    """Oda ayarlarını dosyaya kaydet."""
    try:
        with open(ROOM_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
            logger.info(f"Oda ayarları kaydedildi: {len(settings)} oda")
    except Exception as e:
        logger.error(f"Oda ayarları kaydetme hatası: {e}")
        raise
