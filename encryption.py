"""Hemşire Hasta Takip Sistemi - Veri Şifreleme Modülü

Hassas hasta verilerini Fernet (AES-128-CBC) ile şifreler.
cryptography kütüphanesi yüklü değilse şifreleme devre dışı kalır.
"""

import os
import logging

logger = logging.getLogger(__name__)

KEY_FILE = ".encryption_key"

SENSITIVE_FIELDS = [
    "name", "doctor", "diagnosis",
    "allergy_type", "isolation_reason", "dressing_type",
]

_fernet = None
_initialized = False


def _get_fernet():
    global _fernet, _initialized
    if _initialized:
        return _fernet

    _initialized = True
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        logger.warning("cryptography kütüphanesi yüklü değil — şifreleme devre dışı")
        return None

    try:
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "rb") as f:
                key = f.read().strip()
        else:
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as f:
                f.write(key)
            logger.info("Yeni şifreleme anahtarı oluşturuldu")

        _fernet = Fernet(key)
    except Exception as e:
        logger.error(f"Şifreleme başlatma hatası: {e}")
        _fernet = None

    return _fernet


def encrypt_value(value):
    if not value or not isinstance(value, str):
        return value
    f = _get_fernet()
    if f is None:
        return value
    try:
        return "ENC:" + f.encrypt(value.encode("utf-8")).decode("utf-8")
    except Exception as e:
        logger.error(f"Şifreleme hatası: {e}")
        return value


def decrypt_value(value):
    if not value or not isinstance(value, str) or not value.startswith("ENC:"):
        return value
    f = _get_fernet()
    if f is None:
        return value
    try:
        return f.decrypt(value[4:].encode("utf-8")).decode("utf-8")
    except Exception:
        return value


def encrypt_patient(patient):
    encrypted = patient.copy()
    for field in SENSITIVE_FIELDS:
        if encrypted.get(field):
            encrypted[field] = encrypt_value(str(encrypted[field]))
    if patient.get("notes"):
        encrypted["notes"] = []
        for note in patient["notes"]:
            enc_note = note.copy()
            if enc_note.get("text"):
                enc_note["text"] = encrypt_value(enc_note["text"])
            encrypted["notes"].append(enc_note)
    return encrypted


def decrypt_patient(patient):
    decrypted = patient.copy()
    for field in SENSITIVE_FIELDS:
        if decrypted.get(field):
            decrypted[field] = decrypt_value(decrypted[field])
    if patient.get("notes"):
        decrypted["notes"] = []
        for note in patient["notes"]:
            dec_note = note.copy()
            if dec_note.get("text"):
                dec_note["text"] = decrypt_value(dec_note["text"])
            decrypted["notes"].append(dec_note)
    return decrypted
