"""Hemşire Hasta Takip Sistemi - Birim Testleri"""

import json
import os
import shutil
import tempfile
import unittest

# Test ortamını ayarla — gerçek dosyalara dokunma
_test_dir = tempfile.mkdtemp(prefix="hasta_test_")
os.chdir(_test_dir)

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_service import validate_patient, save_data, load_data
from encryption import encrypt_value, decrypt_value, encrypt_patient, decrypt_patient


def _make_patient(**overrides):
    base = {
        "id": "test-id-001",
        "name": "Test Hasta",
        "age": 30,
        "gender": "Erkek",
        "room": 1,
        "doctor": "Dr. Test",
        "diagnosis": "Test tanı",
        "anesthesia": "Genel",
        "date": "01.04.2026 10:00",
        "allergy": False,
        "allergy_type": "",
        "isolation": False,
        "isolation_reason": "",
        "fasting": False,
        "fall_risk": False,
        "dressing": False,
        "dressing_type": "",
        "notes": [],
    }
    base.update(overrides)
    return base


class TestValidatePatient(unittest.TestCase):

    def test_valid_patient(self):
        self.assertIsNone(validate_patient(_make_patient()))

    def test_missing_name(self):
        p = _make_patient()
        del p["name"]
        self.assertIsNotNone(validate_patient(p))

    def test_empty_name(self):
        self.assertIsNotNone(validate_patient(_make_patient(name="")))
        self.assertIsNotNone(validate_patient(_make_patient(name="   ")))

    def test_name_too_long(self):
        self.assertIsNotNone(validate_patient(_make_patient(name="A" * 501)))

    def test_age_boundaries(self):
        self.assertIsNotNone(validate_patient(_make_patient(age=0)))
        self.assertIsNone(validate_patient(_make_patient(age=1)))
        self.assertIsNone(validate_patient(_make_patient(age=120)))
        self.assertIsNotNone(validate_patient(_make_patient(age=121)))
        self.assertIsNotNone(validate_patient(_make_patient(age="30")))

    def test_invalid_gender(self):
        self.assertIsNotNone(validate_patient(_make_patient(gender="Diğer")))

    def test_invalid_room(self):
        self.assertIsNotNone(validate_patient(_make_patient(room=0)))
        self.assertIsNotNone(validate_patient(_make_patient(room=-1)))
        self.assertIsNotNone(validate_patient(_make_patient(room="1")))

    def test_text_field_too_long(self):
        self.assertIsNotNone(validate_patient(_make_patient(diagnosis="X" * 501)))

    def test_note_text_too_long(self):
        p = _make_patient(notes=[{"time": "now", "text": "X" * 2001, "type": "Diğer"}])
        self.assertIsNotNone(validate_patient(p))

    def test_not_a_dict(self):
        self.assertIsNotNone(validate_patient("not a dict"))
        self.assertIsNotNone(validate_patient(None))


class TestEncryption(unittest.TestCase):

    def test_encrypt_decrypt_roundtrip(self):
        original = "Hasta Adı Test"
        encrypted = encrypt_value(original)
        if encrypted != original:  # cryptography yüklüyse
            self.assertTrue(encrypted.startswith("ENC:"))
            self.assertEqual(decrypt_value(encrypted), original)

    def test_empty_value_passthrough(self):
        self.assertEqual(encrypt_value(""), "")
        self.assertIsNone(encrypt_value(None))

    def test_plaintext_passthrough(self):
        self.assertEqual(decrypt_value("plaintext"), "plaintext")
        self.assertEqual(decrypt_value(""), "")

    def test_patient_roundtrip(self):
        original = _make_patient(
            name="Gizli Hasta",
            doctor="Dr. Gizli",
            diagnosis="Gizli Tanı",
            notes=[{"time": "now", "text": "Gizli not", "type": "İlaç"}],
        )
        encrypted = encrypt_patient(original)
        decrypted = decrypt_patient(encrypted)

        self.assertEqual(decrypted["name"], "Gizli Hasta")
        self.assertEqual(decrypted["doctor"], "Dr. Gizli")
        self.assertEqual(decrypted["diagnosis"], "Gizli Tanı")
        self.assertEqual(decrypted["notes"][0]["text"], "Gizli not")


class TestSaveLoad(unittest.TestCase):

    def setUp(self):
        self._original_dir = os.getcwd()
        self._test_dir = tempfile.mkdtemp(prefix="hasta_sl_")
        os.chdir(self._test_dir)
        # config.DATA_FILE varsayılan olarak göreceli yol kullanır
        from config import BACKUP_DIR
        os.makedirs(BACKUP_DIR, exist_ok=True)

    def tearDown(self):
        os.chdir(self._original_dir)
        shutil.rmtree(self._test_dir, ignore_errors=True)

    def test_save_and_load_roundtrip(self):
        patients = [_make_patient(), _make_patient(id="test-id-002", name="İkinci Hasta", age=25)]
        save_data(patients)
        loaded = load_data()
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]["name"], "Test Hasta")
        self.assertEqual(loaded[1]["name"], "İkinci Hasta")

    def test_load_empty_returns_list(self):
        loaded = load_data()
        self.assertIsInstance(loaded, list)

    def test_save_creates_file(self):
        save_data([_make_patient()])
        from config import DATA_FILE
        self.assertTrue(os.path.exists(DATA_FILE))

    def test_age_migration(self):
        """Eski string yaş değerlerinin int'e dönüştürüldüğünü doğrula."""
        from config import DATA_FILE
        raw = [{"id": "m1", "name": "Eski", "age": "42", "gender": "Erkek",
                "room": 1, "diagnosis": "test", "anesthesia": "", "date": "",
                "doctor": "", "notes": []}]
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(raw, f)
        loaded = load_data()
        self.assertEqual(loaded[0]["age"], 42)
        self.assertIsInstance(loaded[0]["age"], int)


class TestPatientService(unittest.TestCase):

    def setUp(self):
        self._original_dir = os.getcwd()
        self._test_dir = tempfile.mkdtemp(prefix="hasta_ps_")
        os.chdir(self._test_dir)
        from config import BACKUP_DIR
        os.makedirs(BACKUP_DIR, exist_ok=True)
        save_data([])

    def tearDown(self):
        os.chdir(self._original_dir)
        shutil.rmtree(self._test_dir, ignore_errors=True)

    def test_add_and_get_patient(self):
        from patient_service import PatientService
        svc = PatientService()
        p = _make_patient()
        ok, err = svc.add_patient(p)
        self.assertTrue(ok)
        self.assertIsNone(err)
        self.assertEqual(len(svc.data), 1)
        self.assertIsNotNone(svc.get_patient("test-id-001"))

    def test_add_patient_room_full(self):
        from patient_service import PatientService
        svc = PatientService()
        svc.room_settings = {"1": {"max_patients": 1}}
        svc.add_patient(_make_patient(id="p1"))
        ok, err = svc.add_patient(_make_patient(id="p2"))
        self.assertFalse(ok)
        self.assertIn("dolu", err)

    def test_discharge_patient(self):
        from patient_service import PatientService
        svc = PatientService()
        svc.add_patient(_make_patient())
        name, ok = svc.discharge_patient("test-id-001")
        self.assertTrue(ok)
        self.assertEqual(name, "Test Hasta")
        self.assertEqual(len(svc.data), 0)

    def test_add_and_delete_note(self):
        from patient_service import PatientService
        svc = PatientService()
        svc.add_patient(_make_patient())
        ok, _ = svc.add_note("test-id-001", "İlaç", "Parasetamol verildi")
        self.assertTrue(ok)
        self.assertEqual(len(svc.get_patient("test-id-001")["notes"]), 1)

        ok, _ = svc.delete_note("test-id-001", 0)
        self.assertTrue(ok)
        self.assertEqual(len(svc.get_patient("test-id-001")["notes"]), 0)

    def test_note_length_limit(self):
        from patient_service import PatientService
        svc = PatientService()
        svc.add_patient(_make_patient())
        ok, err = svc.add_note("test-id-001", "Diğer", "X" * 2001)
        self.assertFalse(ok)
        self.assertIn("2000", err)

    def test_room_management(self):
        from patient_service import PatientService
        svc = PatientService()
        room_num, ok, _ = svc.add_room(3)
        self.assertTrue(ok)
        self.assertIn(str(room_num), svc.room_settings)

        ok, _ = svc.change_room_capacity(room_num, 4)
        self.assertTrue(ok)
        self.assertEqual(svc.room_settings[str(room_num)]["max_patients"], 4)

        ok, _ = svc.delete_room(room_num)
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
