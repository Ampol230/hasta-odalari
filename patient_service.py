"""Hemşire Hasta Takip Sistemi - Hasta Servisi (İş Mantığı)

UI-bağımsız hasta yönetim katmanı.
Tüm veri değişiklikleri bu servis üzerinden yapılır.
"""

import logging
from datetime import datetime

from config import MAX_PATIENTS_PER_ROOM, DATE_FORMAT
from data_service import (
    load_data, save_data, get_discharged_patients,
    remove_patient_from_backups, load_room_settings, save_room_settings,
    validate_patient,
)

logger = logging.getLogger(__name__)


class PatientService:

    def __init__(self):
        self.data = load_data()
        self.room_settings = load_room_settings()

    # ── Sorgulama ─────────────────────────────────────────

    def get_stats(self):
        total_rooms = len(self.room_settings)
        room_counts: dict[int, int] = {}
        for p in self.data:
            room = p.get("room")
            if room is not None:
                room_counts[room] = room_counts.get(room, 0) + 1

        dolu = sum(
            1 for rk, s in self.room_settings.items()
            if room_counts.get(int(rk), 0) >= s.get("max_patients", MAX_PATIENTS_PER_ROOM)
        )
        toplam = len(self.data)
        max_kap = sum(s.get("max_patients", MAX_PATIENTS_PER_ROOM) for s in self.room_settings.values())
        yuzde = round(toplam / max_kap * 100) if max_kap > 0 else 0
        return {"toplam": toplam, "dolu": dolu, "bos": total_rooms - dolu, "yuzde": yuzde}

    def get_patient(self, patient_id):
        return next((p for p in self.data if p.get("id") == patient_id), None)

    def get_sorted_patients(self):
        return sorted(self.data, key=lambda x: int(x.get("room", 0)))

    def room_patient_count(self, room):
        return sum(1 for p in self.data if p.get("room") == room)

    def get_room_max(self, room_num):
        return self.room_settings.get(str(room_num), {}).get("max_patients", MAX_PATIENTS_PER_ROOM)

    def get_room_list(self):
        return sorted(int(k) for k in self.room_settings.keys())

    def get_doctor_list(self):
        return list({p.get("doctor", "") for p in self.data if p.get("doctor")})

    # ── Hasta CRUD ────────────────────────────────────────

    def add_patient(self, patient_data):
        """Döndürür: (başarılı, hata_mesajı)"""
        room_max = self.get_room_max(patient_data["room"])
        if self.room_patient_count(patient_data["room"]) >= room_max:
            return False, f"Bu oda tam kapasite dolu (Maks: {room_max})."

        error = validate_patient(patient_data)
        if error:
            return False, error

        self.data.append(patient_data)
        save_data(self.data)
        logger.info(f"Yeni hasta eklendi: {patient_data['name']} (ID: {patient_data['id']})")
        return True, None

    def edit_patient(self, patient_id, new_data):
        """Döndürür: (başarılı, hata_mesajı)"""
        patient = self.get_patient(patient_id)
        if not patient:
            return False, "Hasta bulunamadı."

        if new_data["room"] != patient["room"]:
            room_max = self.get_room_max(new_data["room"])
            if self.room_patient_count(new_data["room"]) >= room_max:
                return False, "Geçiş yapılmak istenen oda dolu."

        new_data["notes"] = patient.get("notes", [])
        patient.update(new_data)
        save_data(self.data)
        logger.info(f"Hasta düzenlendi: {patient['name']}")
        return True, None

    def discharge_patient(self, patient_id):
        """Döndürür: (hasta_adı | None, başarılı)"""
        patient = self.get_patient(patient_id)
        if not patient:
            return None, False

        name = patient["name"]
        self.data.remove(patient)
        save_data(self.data)
        logger.info(f"Hasta taburcu edildi: {name}")
        return name, True

    def restore_patient(self, patient_id, discharged_list):
        """Döndürür: (hasta_adı, başarılı, hata_mesajı)"""
        if any(p.get("id") == patient_id for p in self.data):
            return None, False, "Bu hasta zaten sistemde kayıtlı!"

        patient = next((p for p in discharged_list if p.get("id") == patient_id), None)
        if not patient:
            return None, False, "Hasta bulunamadı."

        name = patient.get("name", "Bilinmeyen")
        patient.pop("backup_file", None)
        patient.pop("backup_date", None)

        self.data.append(patient)
        save_data(self.data)
        remove_patient_from_backups(patient_id, name)
        logger.info(f"Hasta geri getirildi: {name}")
        return name, True, None

    # ── Not Yönetimi ──────────────────────────────────────

    def add_note(self, patient_id, note_type, text):
        """Döndürür: (başarılı, hata_mesajı)"""
        patient = self.get_patient(patient_id)
        if not patient:
            return False, "Hasta bulunamadı."
        if len(text) > 2000:
            return False, "Not metni 2000 karakteri geçemez."

        if "notes" not in patient:
            patient["notes"] = []

        patient["notes"].append({
            "time": datetime.now().strftime(DATE_FORMAT),
            "text": text.strip(),
            "type": note_type,
        })
        save_data(self.data)
        logger.info(f"Not eklendi — Hasta: {patient['name']}, Tür: {note_type}")
        return True, None

    def edit_note(self, patient_id, note_index, new_text):
        """Döndürür: (başarılı, hata_mesajı)"""
        patient = self.get_patient(patient_id)
        if not patient:
            return False, "Hasta bulunamadı."

        notes = patient.get("notes", [])
        if note_index < 0 or note_index >= len(notes):
            return False, "Geçersiz not indeksi."

        notes[note_index]["text"] = new_text.strip()
        notes[note_index]["time"] = datetime.now().strftime(DATE_FORMAT) + " (düzenlendi)"
        save_data(self.data)
        logger.info(f"Not düzenlendi — Hasta: {patient['name']}")
        return True, None

    def delete_note(self, patient_id, note_index):
        """Döndürür: (başarılı, hata_mesajı)"""
        patient = self.get_patient(patient_id)
        if not patient:
            return False, "Hasta bulunamadı."

        notes = patient.get("notes", [])
        if note_index < 0 or note_index >= len(notes):
            return False, "Geçersiz not indeksi."

        notes.pop(note_index)
        save_data(self.data)
        logger.info(f"Not silindi — Hasta: {patient['name']}")
        return True, None

    # ── Oda Yönetimi ──────────────────────────────────────

    def add_room(self, capacity):
        """Döndürür: (oda_numarası, başarılı, hata_mesajı)"""
        room_list = self.get_room_list()
        new_room = max(room_list) + 1 if room_list else 1

        self.room_settings[str(new_room)] = {"max_patients": capacity}
        save_room_settings(self.room_settings)
        logger.info(f"Yeni oda eklendi: Oda {new_room} (kapasite: {capacity})")
        return new_room, True, None

    def delete_room(self, room_num):
        """Döndürür: (başarılı, hata_mesajı)"""
        if len(self.room_settings) <= 1:
            return False, "En az 1 oda bulunmalıdır."

        count = self.room_patient_count(room_num)
        if count > 0:
            return False, (
                f"Oda {room_num} içinde {count} hasta var.\n"
                "Önce hastaları başka odaya taşıyın veya taburcu edin."
            )

        del self.room_settings[str(room_num)]
        save_room_settings(self.room_settings)
        logger.info(f"Oda silindi: Oda {room_num}")
        return True, None

    def change_room_capacity(self, room_num, new_capacity):
        """Döndürür: (başarılı, hata_mesajı)"""
        current_count = self.room_patient_count(room_num)
        if new_capacity < current_count:
            return False, (
                f"Oda {room_num} içinde {current_count} hasta var.\n"
                f"Kapasite {current_count}'den az olamaz."
            )

        self.room_settings[str(room_num)]["max_patients"] = new_capacity
        save_room_settings(self.room_settings)
        logger.info(f"Oda {room_num} kapasitesi değişti: {new_capacity}")
        return True, None

    # ── Taburcu Arşivi ────────────────────────────────────

    def get_discharged(self):
        return get_discharged_patients(self.data)
