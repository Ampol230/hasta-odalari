"""Hemşire Hasta Takip Sistemi - Hasta Dialog"""

import uuid
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QSpinBox,
    QCheckBox, QPushButton, QMessageBox, QCompleter
)
from PySide6.QtCore import Qt

from config import COLORS, GENDERS, DATE_FORMAT
from styles import FORM_INPUT_STYLE, CHECKBOX_STYLE


class PatientDialog(QDialog):
    def __init__(self, patient=None, room_list=None, doctor_list=None):
        super().__init__()
        self.setWindowTitle("Hasta Bilgisi Girişi")
        self.setMinimumWidth(380)
        self.setStyleSheet(f"background-color: {COLORS['bg_dark']}; color: {COLORS['text_main']};")

        layout = QFormLayout()
        layout.setSpacing(10)

        self.name = QLineEdit()
        self.name.setStyleSheet(FORM_INPUT_STYLE)
        
        self.age = QSpinBox()
        self.age.setRange(0, 120)
        self.age.setStyleSheet(FORM_INPUT_STYLE)

        self.gender = QComboBox()
        self.gender.addItems(GENDERS)
        self.gender.setStyleSheet(FORM_INPUT_STYLE)

        self.room = QComboBox()
        if room_list:
            self.room.addItems([str(r) for r in sorted(room_list)])
        else:
            self.room.addItems([str(i) for i in range(1, 17)])
        self.room.setStyleSheet(FORM_INPUT_STYLE)

        self.doctor = QLineEdit()
        self.doctor.setStyleSheet(FORM_INPUT_STYLE)
        self.doctor.setPlaceholderText("Örn: Dr. Ali Yılmaz")
        if doctor_list:
            completer = QCompleter(doctor_list)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.doctor.setCompleter(completer)

        self.diagnosis = QLineEdit()
        self.diagnosis.setStyleSheet(FORM_INPUT_STYLE)
        
        self.anesthesia = QLineEdit()
        self.anesthesia.setStyleSheet(FORM_INPUT_STYLE)

        self.allergy = QCheckBox("🩸 Alerjisi Var")
        self.allergy.setStyleSheet(CHECKBOX_STYLE)
        
        self.allergy_type = QLineEdit()
        self.allergy_type.setStyleSheet(FORM_INPUT_STYLE)
        self.allergy_type.setPlaceholderText("Neye alerji olduğunu yazın (örn: Penisilin, Örümcek ağı vb.)")
        self.allergy_type.setVisible(False)
        self.allergy.stateChanged.connect(self.toggle_allergy_input)
        
        self.isolation = QCheckBox("🔒 İzole Hasta")
        self.isolation.setStyleSheet(CHECKBOX_STYLE)
        
        self.isolation_reason = QLineEdit()
        self.isolation_reason.setStyleSheet(FORM_INPUT_STYLE)
        self.isolation_reason.setPlaceholderText("İzolasyon sebebi (örn: Enfeksiyon, Risk altında, vb.)")
        self.isolation_reason.setVisible(False)
        self.isolation.stateChanged.connect(self.toggle_isolation_input)
        
        self.fasting = QCheckBox("🚫 Aç Kalma (NPO)")
        self.fasting.setStyleSheet(CHECKBOX_STYLE)
        
        self.fall_risk = QCheckBox("⚠️ Düşme Riski Yüksek")
        self.fall_risk.setStyleSheet(CHECKBOX_STYLE)
        
        self.dressing = QCheckBox("🩹 Pansuman Gerekli")
        self.dressing.setStyleSheet(CHECKBOX_STYLE)
        
        self.dressing_type = QLineEdit()
        self.dressing_type.setStyleSheet(FORM_INPUT_STYLE)
        self.dressing_type.setPlaceholderText("Pansuman türü (örn: Yer değiştirme, Bakım, vb.)")
        self.dressing_type.setVisible(False)
        self.dressing.stateChanged.connect(self.toggle_dressing_input)

        layout.addRow("Ad Soyad:", self.name)
        layout.addRow("Yaş:", self.age)
        layout.addRow("Cinsiyet:", self.gender)
        layout.addRow("Oda No:", self.room)
        layout.addRow("Doktor:", self.doctor)
        layout.addRow("Tanı:", self.diagnosis)
        layout.addRow("Anestezi:", self.anesthesia)
        
        layout.addRow("Uyarılar:", self.allergy)
        layout.addRow("", self.allergy_type)
        layout.addRow("", self.isolation)
        layout.addRow("", self.isolation_reason)
        layout.addRow("", self.fasting)
        layout.addRow("", self.fall_risk)
        layout.addRow("", self.dressing)
        layout.addRow("", self.dressing_type)

        btn = QPushButton("💾 Kaydet")
        btn.setMinimumHeight(40)
        btn.setStyleSheet(f"background-color: {COLORS['accent']}; color: white; font-weight: bold; border-radius: 5px; margin-top: 10px;")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)

        self.setLayout(layout)

        if patient:
            self.patient_id = patient.get("id", str(uuid.uuid4()))
            self.patient_date = patient.get("date", datetime.now().strftime(DATE_FORMAT))
            self.name.setText(patient["name"])
            self.age.setValue(int(patient.get("age", 0)))
            self.gender.setCurrentText(patient["gender"])
            self.room.setCurrentText(str(patient["room"]))
            self.doctor.setText(patient.get("doctor", ""))
            self.diagnosis.setText(patient["diagnosis"])
            self.anesthesia.setText(patient["anesthesia"])
            
            self.allergy.setChecked(patient.get("allergy", False))
            self.toggle_allergy_input()
            self.allergy_type.setText(patient.get("allergy_type", ""))
            self.isolation.setChecked(patient.get("isolation", False))
            self.toggle_isolation_input()
            self.isolation_reason.setText(patient.get("isolation_reason", ""))
            self.fasting.setChecked(patient.get("fasting", False))
            self.fall_risk.setChecked(patient.get("fall_risk", False))
            self.dressing.setChecked(patient.get("dressing", False))
            self.toggle_dressing_input()
            self.dressing_type.setText(patient.get("dressing_type", ""))
        else:
            self.patient_id = str(uuid.uuid4())
            self.patient_date = datetime.now().strftime(DATE_FORMAT)

    def toggle_allergy_input(self):
        self.allergy_type.setVisible(self.allergy.isChecked())

    def toggle_isolation_input(self):
        self.isolation_reason.setVisible(self.isolation.isChecked())
    
    def toggle_dressing_input(self):
        self.dressing_type.setVisible(self.dressing.isChecked())

    def get_data(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Hata", "Hastanın adı boş bırakılamaz!")
            return None
        
        if self.age.value() <= 0:
            QMessageBox.warning(self, "Hata", "Yaş 0'dan büyük olmalıdır!")
            return None

        return {
            "id": self.patient_id,
            "name": self.name.text().strip(),
            "age": self.age.value(),
            "gender": self.gender.currentText(),
            "room": int(self.room.currentText()),
            "doctor": self.doctor.text().strip(),
            "diagnosis": self.diagnosis.text().strip(),
            "anesthesia": self.anesthesia.text().strip(),
            "date": self.patient_date,
            "allergy": self.allergy.isChecked(),
            "allergy_type": self.allergy_type.text().strip() if self.allergy.isChecked() else "",
            "isolation": self.isolation.isChecked(),
            "isolation_reason": self.isolation_reason.text().strip() if self.isolation.isChecked() else "",
            "fasting": self.fasting.isChecked(),
            "fall_risk": self.fall_risk.isChecked(),
            "dressing": self.dressing.isChecked(),
            "dressing_type": self.dressing_type.text().strip() if self.dressing.isChecked() else "",
            "notes": []
        }
