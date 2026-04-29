"""Hemşire Hasta Takip Sistemi - Ana Pencere"""

import os
import logging
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QTextEdit, QLineEdit,
    QStackedWidget, QMessageBox, QGridLayout, QLabel, QListWidgetItem,
    QInputDialog, QTableWidget, QTableWidgetItem, QDialog,
    QSpinBox, QCheckBox, QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from config import (
    COLORS, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    MAX_PATIENTS_PER_ROOM,
    DATE_FORMAT, NOTE_TYPES, SHOW_TOOLTIPS,
    get_patient_alerts
)
from styles import MAIN_STYLESHEET
from patient_service import PatientService
from report_service import generate_word_report
from patient_dialog import PatientDialog
from templates import welcome_dashboard_html, patient_card_html

DOCX_AVAILABLE = True
try:
    from docx import Document
except ImportError:
    DOCX_AVAILABLE = False

logger = logging.getLogger(__name__)


class HastaDefter(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(WINDOW_TITLE)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(MAIN_STYLESHEET)

        self.service = PatientService()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)

        menu = QHBoxLayout()

        self.list_btn = QPushButton("📋 Hasta Listesi")
        self.map_btn = QPushButton("🏥 Oda Krokisi")
        
        self.word_btn = QPushButton("📄 Word Kaydet")
        self.word_btn.setStyleSheet(f"background-color: {COLORS['success']}; color: white; border: none;")
        if not DOCX_AVAILABLE:
            self.word_btn.setEnabled(False)

        self.stats_label = QLabel("📊 İstatistikler Yükleniyor...")
        self.stats_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-weight: bold; font-size: 14px; padding-left: 15px;")

        self.add_btn = QPushButton("➕ Yeni Kayıt")
        self.add_btn.setStyleSheet(f"background-color: {COLORS['accent']}; color: white; border: none;")
        
        self.edit_btn = QPushButton("✏ Düzenle")
        
        self.note_btn = QPushButton("📝 İşlem/Not Ekle")
        self.note_btn.setStyleSheet(f"background-color: {COLORS['warning']}; color: white; border: none;")

        self.note_manage_btn = QPushButton("📋 Not Düzenle")
        self.note_manage_btn.setStyleSheet(f"background-color: {COLORS['orange']}; color: white; border: none;")

        self.discharge_btn = QPushButton("👋 Taburcu Et")
        self.discharge_btn.setStyleSheet(f"background-color: {COLORS['danger']}; color: white; border: none;")
        
        self.restore_btn = QPushButton("🔄 Geri Al")
        self.restore_btn.setStyleSheet(f"background-color: #7B68EE; color: white; border: none;")

        menu.addWidget(self.list_btn)
        menu.addWidget(self.map_btn)
        menu.addWidget(self.word_btn)
        
        menu.addWidget(self.stats_label)
        menu.addStretch()
        
        menu.addWidget(self.add_btn)
        menu.addWidget(self.edit_btn)
        menu.addWidget(self.note_btn)
        menu.addWidget(self.note_manage_btn)
        menu.addWidget(self.discharge_btn)
        menu.addWidget(self.restore_btn)

        main_layout.addLayout(menu)

        self.pages = QStackedWidget()

        list_page = QWidget()
        list_layout = QHBoxLayout()
        list_layout.setContentsMargins(0, 15, 0, 0)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("search_bar")
        self.search_bar.setPlaceholderText("🔍 İsim, Oda, Doktor veya Uyarı ara...")
        self.search_bar.textChanged.connect(self.filter_patients)

        # Uyarı filtre checkboxları
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        self.filter_allergy = QCheckBox("🩸 Alerji")
        self.filter_isolation = QCheckBox("🔒 İzole")
        self.filter_fasting = QCheckBox("🚫 NPO")
        self.filter_fall = QCheckBox("⚠️ Düşme")
        self.filter_dressing = QCheckBox("🩹 Pansuman")
        for cb in [self.filter_allergy, self.filter_isolation, self.filter_fasting, self.filter_fall, self.filter_dressing]:
            cb.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
            cb.stateChanged.connect(self.filter_patients)
            filter_row.addWidget(cb)
        filter_row.addStretch()

        self.patient_list = QListWidget()

        left_panel.addWidget(self.search_bar)
        left_panel.addLayout(filter_row)
        left_panel.addWidget(self.patient_list)

        self.patient_view = QTextEdit()
        self.patient_view.setReadOnly(True)

        list_layout.addLayout(left_panel, 2)
        list_layout.addWidget(self.patient_view, 5)
        list_page.setLayout(list_layout)

        self.map_page = QWidget()
        self.map_layout = QGridLayout()
        self.map_layout.setSpacing(15)
        self.map_layout.setContentsMargins(0, 15, 0, 0)
        self.map_page.setLayout(self.map_layout)

        self.pages.addWidget(list_page)
        self.pages.addWidget(self.map_page)

        main_layout.addWidget(self.pages)
        self.setLayout(main_layout)

        self.refresh_list()
        self.draw_map()
        self.show_welcome_dashboard()

        self.patient_list.currentRowChanged.connect(self.show_patient)
        self.add_btn.clicked.connect(self.add_patient)
        self.edit_btn.clicked.connect(self.edit_patient)
        self.note_btn.clicked.connect(self.add_note)
        self.note_manage_btn.clicked.connect(self.manage_notes)
        self.discharge_btn.clicked.connect(self.discharge_patient)
        self.restore_btn.clicked.connect(self.show_discharged_patients)
        self.word_btn.clicked.connect(self.word_aktar)
        self.patient_list.itemDoubleClicked.connect(self.edit_patient)

        self.list_btn.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.map_btn.clicked.connect(lambda: self.pages.setCurrentIndex(1))

    def _get_stats(self):
        return self.service.get_stats()

    def add_note(self):
        try:
            item = self.patient_list.currentItem()
            if not item:
                QMessageBox.information(self, "Bilgi", "Lütfen not eklemek için listeden bir hasta seçin.")
                return

            selected_id = item.data(Qt.UserRole)
            patient = self.service.get_patient(selected_id)
            if not patient:
                return

            note_type, ok = QInputDialog.getItem(
                self, "İşlem Türü", "İşlem türünü seçin:",
                NOTE_TYPES, 0, False
            )
            if not ok:
                return

            text, ok = QInputDialog.getText(
                self, "Tedavi Günlüğü",
                f"{patient['name']} isimli hastaya uygulanan işlemi/notu yazın:"
            )
            if ok and text.strip():
                success, error = self.service.add_note(selected_id, note_type, text.strip())
                if success:
                    self.show_patient()
                    QMessageBox.information(self, "Başarılı", "İşlem/Not başarıyla eklendi.")
                else:
                    QMessageBox.warning(self, "Hata", error)
        except Exception as e:
            logger.error(f"Not ekleme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Not eklenirken hata oluştu: {e}")

    def manage_notes(self):
        """Seçili hastanın notlarını düzenle/sil."""
        try:
            item = self.patient_list.currentItem()
            if not item:
                QMessageBox.information(self, "Bilgi", "Lütfen listeden bir hasta seçin.")
                return

            selected_id = item.data(Qt.UserRole)
            patient = self.service.get_patient(selected_id)
            if not patient or not patient.get("notes"):
                QMessageBox.information(self, "Bilgi", "Bu hastanın henüz notu bulunmuyor.")
                return

            notes = patient["notes"]
            note_items = [f"[{n['type']}] {n['time']} - {n['text'][:50]}" for n in notes]

            selected, ok = QInputDialog.getItem(
                self, "Not Yönetimi", "Düzenlemek veya silmek istediğiniz notu seçin:",
                note_items, 0, False
            )
            if not ok:
                return

            idx = note_items.index(selected)
            action, ok = QInputDialog.getItem(
                self, "İşlem Seçin", "Bu not ile ne yapmak istiyorsunuz?",
                ["✏️ Düzenle", "🗑️ Sil"], 0, False
            )
            if not ok:
                return

            if "Sil" in action:
                reply = QMessageBox.question(self, "Onay", "Bu notu silmek istediğinize emin misiniz?")
                if reply == QMessageBox.Yes:
                    self.service.delete_note(selected_id, idx)
                    self.show_patient()
            else:
                new_text, ok = QInputDialog.getText(
                    self, "Not Düzenle", "Yeni metin:", text=notes[idx]["text"]
                )
                if ok and new_text.strip():
                    self.service.edit_note(selected_id, idx, new_text.strip())
                    self.show_patient()
        except Exception as e:
            logger.error(f"Not yönetimi hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Hata oluştu: {e}")

    def filter_patients(self, _=None):
        try:
            search_text = self.search_bar.text().lower()
            alert_filters = {
                "allergy": self.filter_allergy.isChecked(),
                "isolation": self.filter_isolation.isChecked(),
                "fasting": self.filter_fasting.isChecked(),
                "fall_risk": self.filter_fall.isChecked(),
                "dressing": self.filter_dressing.isChecked(),
            }
            any_alert_filter = any(alert_filters.values())

            sorted_data = self.service.get_sorted_patients()
            for i, p in enumerate(sorted_data):
                if i >= self.patient_list.count():
                    break
                item = self.patient_list.item(i)

                text_match = search_text in item.text().lower() if search_text else True
                alert_match = True
                if any_alert_filter:
                    alert_match = all(
                        p.get(key, False) for key, active in alert_filters.items() if active
                    )
                item.setHidden(not (text_match and alert_match))
        except Exception as e:
            logger.error(f"Filtreleme hatası: {e}")

    def room_patient_count(self, room):
        return self.service.room_patient_count(room)

    def refresh_list(self):
        try:
            self.patient_list.clear()
            sorted_data = self.service.get_sorted_patients()
            for p in sorted_data:
                oda_metni = str(p["room"]).zfill(2)
                doktor_adi = p.get("doctor", "Belirtilmedi")
                
                alerts = get_patient_alerts(p)
                uyari_emojileri = " ".join(a["emoji"] for a in alerts) + " " if alerts else ""
                badges = ""
                for a in alerts:
                    if a["detail"]:
                        badges += f"{a['emoji']} {a['label']}: {a['detail']}\n"
                    else:
                        badges += f"{a['emoji']} {a['label']}\n"
                
                ekran_yazisi = f"Oda {oda_metni}  •  {p['name']}  {uyari_emojileri}(Dr. {doktor_adi})"
                item = QListWidgetItem(ekran_yazisi)
                item.setData(Qt.UserRole, p.get("id"))
                
                if SHOW_TOOLTIPS:
                    tooltip_text = f"Doktor: {doktor_adi}\n\n{badges}Kayıt: {p.get('date', 'Bilinmiyor')}" if badges else f"Doktor: {doktor_adi}\nKayıt: {p.get('date', 'Bilinmiyor')}"
                    item.setToolTip(tooltip_text)
                self.patient_list.addItem(item)
                
            stats = self._get_stats()
            self.stats_label.setText(f"📊 Toplam: {stats['toplam']}  •  Dolu: {stats['dolu']}  •  Boş: {stats['bos']}  •  {stats['yuzde']}%")
            logger.info(f"Liste yenilendi - Toplam: {stats['toplam']}, Dolu Oda: {stats['dolu']}")
        except Exception as e:
            logger.error(f"Liste yenileme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Liste yenilenirken hata oluştu: {e}")

    def show_welcome_dashboard(self):
        try:
            stats = self._get_stats()
            self.patient_view.setHtml(welcome_dashboard_html(stats))
            logger.info("Hoş geldiniz dashboard gösterildi")
        except Exception as e:
            logger.error(f"Dashboard hatası: {e}")

    def show_patient(self, _index=None):
        try:
            item = self.patient_list.currentItem()
            if not item:
                self.show_welcome_dashboard()
                return

            selected_id = item.data(Qt.UserRole)
            p = self.service.get_patient(selected_id)

            if not p:
                self.show_welcome_dashboard()
                return

            self.patient_view.setHtml(patient_card_html(p))
            logger.info(f"Hasta görüntülendi: {p['name']}")
        except Exception as e:
            logger.error(f"Hasta gösterim hatası: {e}")
            self.patient_view.setText(f"Hata: {e}")

    def _get_room_max(self, room_num):
        return self.service.get_room_max(room_num)

    def _get_room_list(self):
        return self.service.get_room_list()

    def _get_doctor_list(self):
        return self.service.get_doctor_list()

    def add_patient(self):
        try:
            dialog = PatientDialog(room_list=self._get_room_list(), doctor_list=self._get_doctor_list())
            if dialog.exec():
                patient = dialog.get_data()
                if not patient:
                    return

                success, error = self.service.add_patient(patient)
                if not success:
                    QMessageBox.warning(self, "Hata", error)
                    return

                self.refresh_list()
                self.draw_map()
                self.search_bar.clear()
                QMessageBox.information(self, "Başarılı", f"{patient['name']} başarıyla kaydedildi.")
        except Exception as e:
            logger.error(f"Hasta ekleme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Hasta eklenirken hata oluştu: {e}")

    def edit_patient(self):
        try:
            item = self.patient_list.currentItem()
            if not item:
                QMessageBox.information(self, "Bilgi", "Lütfen düzenlemek için listeden bir hasta seçin.")
                return

            selected_id = item.data(Qt.UserRole)
            patient = self.service.get_patient(selected_id)
            if not patient:
                QMessageBox.warning(self, "Hata", "Hasta bulunamadı.")
                return

            dialog = PatientDialog(patient, room_list=self._get_room_list(), doctor_list=self._get_doctor_list())
            if dialog.exec():
                new_data = dialog.get_data()
                if not new_data:
                    return

                success, error = self.service.edit_patient(selected_id, new_data)
                if not success:
                    QMessageBox.warning(self, "Hata", error)
                    return

                self.refresh_list()
                self.draw_map()
                self.show_patient()
                QMessageBox.information(self, "Başarılı", "Hasta bilgileri güncellendi.")
        except Exception as e:
            logger.error(f"Hasta düzenleme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Hasta düzenlenirken hata oluştu: {e}")

    def discharge_patient(self):
        try:
            item = self.patient_list.currentItem()
            if not item:
                QMessageBox.information(self, "Bilgi", "Lütfen taburcu edilecek hastayı listeden seçin.")
                return

            selected_id = item.data(Qt.UserRole)
            patient = self.service.get_patient(selected_id)
            if not patient:
                QMessageBox.warning(self, "Hata", "Hasta bulunamadı.")
                return

            reply = QMessageBox.question(
                self, "Taburcu İşlemi",
                f"{patient['name']} isimli hastayı taburcu etmek istediğinize emin misiniz?\n(Bu işlem hastayı sistemden kaldırır.)"
            )
            if reply == QMessageBox.Yes:
                name, _ = self.service.discharge_patient(selected_id)
                self.refresh_list()
                self.draw_map()
                self.patient_view.clear()
                self.search_bar.clear()
                QMessageBox.information(self, "Başarılı", f"{name} taburcu edildi.")
        except Exception as e:
            logger.error(f"Taburcu işlemi hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Taburcu işleminde hata oluştu: {e}")

    def show_discharged_patients(self):
        try:
            discharged = self.service.get_discharged()
            
            if not discharged:
                QMessageBox.information(self, "Bilgi", "Son 90 gün içinde taburcu edilen hasta bulunamadı.")
                return
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Taburcu Edilen Hastalar (Son 90 Gün)")
            dialog.setMinimumWidth(900)
            dialog.setMinimumHeight(500)
            dialog.setStyleSheet(f"background-color: {COLORS['bg_dark']}; color: {COLORS['text_main']};")
            
            layout = QVBoxLayout()
            
            title_label = QLabel("Taburcu Edilen Hastalar - Son 90 Gün")
            title_label.setStyleSheet(f"color: {COLORS['accent']}; font-size: 16px; font-weight: bold; padding: 10px;")
            layout.addWidget(title_label)
            
            search_layout = QHBoxLayout()
            search_label = QLabel("🔍 Ara (Ad, Doktor, Oda):")
            search_label.setStyleSheet(f"color: {COLORS['text_main']}; font-weight: bold;")
            search_input = QLineEdit()
            search_input.setPlaceholderText("Hastanın adını, doktorunun adını veya oda numarasını yazın...")
            search_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {COLORS['bg_darker']};
                    border: 1px solid {COLORS['accent']};
                    border-radius: 5px;
                    padding: 8px;
                    color: {COLORS['text_main']};
                    font-size: 12px;
                }}
                QLineEdit:focus {{
                    border: 2px solid {COLORS['accent']};
                }}
            """)
            search_layout.addWidget(search_label)
            search_layout.addWidget(search_input)
            layout.addLayout(search_layout)
            
            table = QTableWidget()
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(["Ad Soyad", "Yaş", "Cinsiyet", "Oda", "Doktor", "Taburcu Tarihi"])
            table.setStyleSheet(f"""
                QTableWidget {{
                    background-color: {COLORS['bg_darker']};
                    gridline-color: #313338;
                }}
                QTableWidget::item {{
                    padding: 8px;
                    border: 1px solid #313338;
                }}
                QHeaderView::section {{
                    background-color: #313338;
                    color: {COLORS['text_main']};
                    padding: 8px;
                    border: none;
                    font-weight: bold;
                }}
            """)
            table.setColumnWidth(0, 200)
            table.setColumnWidth(1, 70)
            table.setColumnWidth(2, 100)
            table.setColumnWidth(3, 70)
            table.setColumnWidth(4, 150)
            table.setColumnWidth(5, 150)
            
            for i, patient in enumerate(discharged):
                table.insertRow(i)
                table.setItem(i, 0, QTableWidgetItem(patient.get("name", "-")))
                table.setItem(i, 1, QTableWidgetItem(str(patient.get("age", "-"))))
                table.setItem(i, 2, QTableWidgetItem(patient.get("gender", "-")))
                table.setItem(i, 3, QTableWidgetItem(str(patient.get("room", "-"))))
                table.setItem(i, 4, QTableWidgetItem(patient.get("doctor", "-")))
                table.setItem(i, 5, QTableWidgetItem(patient.get("backup_date", "-")))
                
                for j in range(6):
                    item = table.item(i, j)
                    item.setData(Qt.UserRole, patient.get("id"))
            
            def filter_table(search_text):
                for row in range(table.rowCount()):
                    match = False
                    search_text_lower = search_text.lower()
                    for col in range(table.columnCount()):
                        cell_text = table.item(row, col).text().lower()
                        if search_text_lower in cell_text:
                            match = True
                            break
                    table.setRowHidden(row, not match)
            
            search_input.textChanged.connect(filter_table)
            layout.addWidget(table)
            
            button_layout = QHBoxLayout()
            
            restore_btn = QPushButton("✅ Geri Getir")
            restore_btn.setStyleSheet(f"background-color: {COLORS['success']}; color: white; font-weight: bold; border-radius: 5px; padding: 10px;")
            restore_btn.clicked.connect(lambda: self._restore_patient(table, dialog, discharged))
            
            close_btn = QPushButton("❌ Kapat")
            close_btn.setStyleSheet(f"background-color: #404249; color: white; font-weight: bold; border-radius: 5px; padding: 10px;")
            close_btn.clicked.connect(dialog.close)
            
            button_layout.addWidget(restore_btn)
            button_layout.addWidget(close_btn)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Taburcu edilen hastalar gösterilirken hata: {e}")
            QMessageBox.critical(self, "Hata", f"Hata oluştu: {e}")

    def _restore_patient(self, table, dialog, discharged_list):
        try:
            selected_row = table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir hasta seçin.")
                return
            
            selected_id = table.item(selected_row, 0).data(Qt.UserRole)
            
            reply = QMessageBox.question(
                self, "Geri Getirme Onayı",
                "Bu hastayı sisteme geri getirmek istediğinize emin misiniz?\n\n"
                "Bu işlem sonunda hasta kalıcı olarak geri al listesinden silinecektir."
            )
            
            if reply == QMessageBox.Yes:
                name, success, error = self.service.restore_patient(selected_id, discharged_list)
                if not success:
                    QMessageBox.critical(self, "Hata", error)
                    return

                self.refresh_list()
                self.draw_map()
                QMessageBox.information(
                    self, "Başarılı",
                    f"{name} sisteme geri getirildi ve geri al listesinden kalıcı olarak silindi!"
                )
                dialog.close()
        except Exception as e:
            logger.error(f"Hasta geri getirme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Hata oluştu: {e}")

    def draw_map(self):
        try:
            for i in reversed(range(self.map_layout.count())):
                widget = self.map_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            room_list = self.service.get_room_list()

            rooms = {i: [] for i in room_list}
            for p in self.service.data:
                room_num = int(p["room"])
                if room_num in rooms:
                    rooms[room_num].append(p)

            # ─── ÜST PANEL ───
            header_widget = QWidget()
            header_widget.setStyleSheet(f"""
                QWidget {{ background-color: {COLORS['bg_darker']}; border-radius: 10px; }}
            """)
            header_layout = QHBoxLayout()
            header_layout.setContentsMargins(16, 10, 16, 10)

            title_label = QLabel("🏥 Oda Krokisi")
            title_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
            title_label.setStyleSheet(f"color: {COLORS['text_main']}; background: transparent;")

            stats = self.service.get_stats()
            stats_layout = QHBoxLayout()
            stats_layout.setSpacing(8)

            occupied_partial = len([rn for rn in room_list if 0 < len(rooms.get(rn, [])) < self._get_room_max(rn)])
            stat_chips = [
                (f"🟢 {stats['bos']} Boş", COLORS['success']),
                (f"🟡 {occupied_partial} Kısmi", COLORS['warning']),
                (f"🔴 {stats['dolu']} Dolu", COLORS['danger']),
                (f"📊 %{stats['yuzde']}", COLORS['accent']),
            ]
            for chip_text, chip_color in stat_chips:
                chip = QLabel(chip_text)
                chip.setStyleSheet(f"""
                    background-color: #313338;
                    color: {chip_color};
                    border: 1px solid #404249;
                    border-radius: 12px;
                    padding: 4px 10px;
                    font-size: 11px;
                    font-weight: bold;
                """)
                chip.setAlignment(Qt.AlignCenter)
                stats_layout.addWidget(chip)
            stats_layout.addStretch()

            add_room_btn = QPushButton("➕ Oda Ekle")
            add_room_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['accent']}; color: white; border: none;
                    font-weight: bold; padding: 8px 16px; border-radius: 6px; font-size: 12px;
                }}
                QPushButton:hover {{ background-color: #4752c4; }}
            """)
            add_room_btn.clicked.connect(self._add_room)

            del_room_btn = QPushButton("🗑️ Oda Sil")
            del_room_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent; color: {COLORS['danger']};
                    border: 1px solid {COLORS['danger']}; font-weight: bold;
                    padding: 8px 16px; border-radius: 6px; font-size: 12px;
                }}
                QPushButton:hover {{ background-color: {COLORS['danger']}; color: white; }}
            """)
            del_room_btn.clicked.connect(self._delete_room)

            header_layout.addWidget(title_label)
            header_layout.addSpacing(16)
            header_layout.addLayout(stats_layout)
            header_layout.addStretch()
            header_layout.addWidget(add_room_btn)
            header_layout.addSpacing(4)
            header_layout.addWidget(del_room_btn)
            header_widget.setLayout(header_layout)
            self.map_layout.addWidget(header_widget, 0, 0, 1, 4)

            # ─── ODA KARTLARI ───
            r, c = 1, 0
            for room_num in room_list:
                patients = rooms.get(room_num, [])
                max_p = self._get_room_max(room_num)
                occupancy = len(patients)

                if occupancy == 0:
                    accent = COLORS['success']
                    status_text = "BOŞ"
                elif occupancy < max_p:
                    accent = COLORS['warning']
                    status_text = "KISMİ"
                else:
                    accent = COLORS['danger']
                    status_text = "DOLU"

                card = QFrame()
                card.setFrameShape(QFrame.NoFrame)
                card.setStyleSheet(f"""
                    QFrame {{
                        background-color: #313338;
                        border: 1px solid #404249;
                        border-radius: 8px;
                        border-left: 3px solid {accent};
                    }}
                """)

                card_layout = QVBoxLayout()
                card_layout.setContentsMargins(12, 10, 12, 10)
                card_layout.setSpacing(4)

                # ── Oda numarası ──
                room_header = QHBoxLayout()

                room_num_lbl = QLabel(f"Oda {room_num}")
                room_num_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
                room_num_lbl.setStyleSheet(f"color: {COLORS['text_main']}; background: transparent;")

                status_lbl = QLabel(status_text)
                status_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
                status_lbl.setStyleSheet(f"""
                    color: {accent};
                    background: transparent;
                    padding: 2px 6px;
                """)
                status_lbl.setAlignment(Qt.AlignCenter)

                room_header.addWidget(room_num_lbl)
                room_header.addStretch()
                room_header.addWidget(status_lbl)
                card_layout.addLayout(room_header)

                # ── Doluluk barı ──
                bar_bg = QWidget()
                bar_bg.setFixedHeight(3)
                bar_bg.setStyleSheet("background-color: #404249; border-radius: 1px;")
                bar_fill = QWidget(bar_bg)
                fill_pct = int((occupancy / max_p) * 100) if max_p > 0 else 0
                bar_fill.setStyleSheet(f"background-color: {accent}; border-radius: 1px;")
                bar_fill.setGeometry(0, 0, max(fill_pct * 2, 0), 3)
                card_layout.addWidget(bar_bg)

                cap_info = QLabel(f"{occupancy} / {max_p}")
                cap_info.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; background: transparent;")
                cap_info.setAlignment(Qt.AlignRight)
                card_layout.addWidget(cap_info)

                # ── Ayırıcı ──
                divider = QFrame()
                divider.setFrameShape(QFrame.HLine)
                divider.setStyleSheet("background-color: #404249; border: none; max-height: 1px;")
                card_layout.addWidget(divider)
                card_layout.addSpacing(2)

                # ── Hasta listesi ──
                if patients:
                    for p_data in patients:
                        p_row = QHBoxLayout()
                        p_row.setSpacing(6)
                        p_row.setContentsMargins(0, 3, 0, 3)

                        alerts = get_patient_alerts(p_data)
                        alert_str = " ".join(a["emoji"] for a in alerts)

                        name_lbl = QLabel(p_data['name'])
                        name_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
                        name_lbl.setStyleSheet(f"color: {COLORS['text_main']}; background: transparent;")
                        p_row.addWidget(name_lbl)
                        p_row.addStretch()

                        if alert_str:
                            alert_lbl = QLabel(alert_str)
                            alert_lbl.setStyleSheet("font-size: 12px; background: transparent;")
                            p_row.addWidget(alert_lbl)

                        card_layout.addLayout(p_row)

                        doc_name = p_data.get('doctor', '-')
                        doc_lbl = QLabel(f"  Dr. {doc_name}")
                        doc_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; background: transparent;")
                        card_layout.addWidget(doc_lbl)
                else:
                    empty_lbl = QLabel("Hasta yok")
                    empty_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px; font-style: italic; background: transparent;")
                    empty_lbl.setAlignment(Qt.AlignCenter)
                    card_layout.addWidget(empty_lbl)
                    card_layout.addSpacing(12)

                card_layout.addStretch()

                # ── Kapasite ayarı ──
                cap_row = QHBoxLayout()
                cap_row.setSpacing(4)
                cap_lbl = QLabel("Kapasite:")
                cap_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; background: transparent;")
                cap_spin = QSpinBox()
                cap_spin.setRange(1, 4)
                cap_spin.setValue(max_p)
                cap_spin.setFixedWidth(50)
                cap_spin.setStyleSheet(f"""
                    QSpinBox {{
                        background-color: {COLORS['bg_darker']}; color: {COLORS['text_main']};
                        border: 1px solid #404249; border-radius: 4px; padding: 2px; font-size: 11px;
                    }}
                    QSpinBox::up-button {{
                        subcontrol-origin: border; subcontrol-position: top right;
                        width: 14px; border-left: 1px solid #404249; background-color: #313338;
                    }}
                    QSpinBox::up-button:hover {{ background-color: {COLORS['accent']}; }}
                    QSpinBox::up-arrow {{
                        image: none;
                        border-left: 3px solid transparent; border-right: 3px solid transparent;
                        border-bottom: 4px solid {COLORS['text_main']}; width: 0; height: 0;
                    }}
                    QSpinBox::down-button {{
                        subcontrol-origin: border; subcontrol-position: bottom right;
                        width: 14px; border-left: 1px solid #404249; background-color: #313338;
                    }}
                    QSpinBox::down-button:hover {{ background-color: {COLORS['accent']}; }}
                    QSpinBox::down-arrow {{
                        image: none;
                        border-left: 3px solid transparent; border-right: 3px solid transparent;
                        border-top: 4px solid {COLORS['text_main']}; width: 0; height: 0;
                    }}
                """)
                cap_spin.valueChanged.connect(lambda val, rn=room_num: self._change_room_capacity(rn, val))
                cap_row.addWidget(cap_lbl)
                cap_row.addWidget(cap_spin)
                cap_row.addStretch()
                card_layout.addLayout(cap_row)

                card.setLayout(card_layout)
                card.setMinimumHeight(170)
                card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                self.map_layout.addWidget(card, r, c)
                c += 1
                if c == 4:
                    c = 0
                    r += 1

            logger.info("Oda haritası güncellendi")
        except Exception as e:
            logger.error(f"Harita çizme hatası: {e}")

    def _add_room(self):
        try:
            cap, ok = QInputDialog.getInt(
                self, "Oda Ekle",
                "Yeni oda için maksimum hasta kapasitesi (1-4):",
                MAX_PATIENTS_PER_ROOM, 1, 4
            )
            if not ok:
                return

            new_room, _, _ = self.service.add_room(cap)
            self.draw_map()
            self.refresh_list()
            QMessageBox.information(self, "Başarılı", f"Oda {new_room} eklendi (Kapasite: {cap}).")
        except Exception as e:
            logger.error(f"Oda ekleme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Oda eklenirken hata oluştu: {e}")

    def _delete_room(self):
        try:
            room_list = self.service.get_room_list()
            if len(room_list) <= 1:
                QMessageBox.warning(self, "Uyarı", "En az 1 oda bulunmalıdır.")
                return

            room_strs = [f"Oda {r}" for r in room_list]
            selected, ok = QInputDialog.getItem(
                self, "Oda Sil", "Silmek istediğiniz odayı seçin:",
                room_strs, len(room_strs) - 1, False
            )
            if not ok:
                return

            room_num = int(selected.replace("Oda ", ""))
            reply = QMessageBox.question(self, "Oda Sil", f"Oda {room_num} silinecek. Emin misiniz?")
            if reply == QMessageBox.Yes:
                success, error = self.service.delete_room(room_num)
                if not success:
                    QMessageBox.warning(self, "Uyarı", error)
                    return
                self.draw_map()
                self.refresh_list()
                QMessageBox.information(self, "Başarılı", f"Oda {room_num} silindi.")
        except Exception as e:
            logger.error(f"Oda silme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Oda silinirken hata oluştu: {e}")

    def _change_room_capacity(self, room_num, new_capacity):
        try:
            success, error = self.service.change_room_capacity(room_num, new_capacity)
            if not success:
                QMessageBox.warning(self, "Uyarı", error)
                self.draw_map()
                return
            self.refresh_list()
        except Exception as e:
            logger.error(f"Kapasite değiştirme hatası: {e}")

    def word_aktar(self):
        try:
            dosya_adi, success, error = generate_word_report(
                self.service.data, self.service.room_settings
            )
            if not success:
                QMessageBox.warning(self, "Uyarı", error)
                return

            try:
                os.startfile(dosya_adi, 'print')
                QMessageBox.information(
                    self, "Başarılı",
                    f"Rapor yazıcıya gönderildi.\n(Dosya: {dosya_adi})"
                )
            except Exception as print_error:
                logger.warning(f"Yazıcı hatası: {print_error}")
                QMessageBox.information(
                    self, "Uyarı",
                    f"Rapor oluşturuldu ancak yazıcıya gönderilemedi.\n"
                    f"Dosya: {dosya_adi}\n\n{print_error}"
                )

        except PermissionError:
            logger.error("Word raporu - Dosya yazma izni hatası")
            QMessageBox.critical(
                self, "Hata",
                "Dosya yazma izni yok. Lütfen dosyayı kapatıp tekrar deneyin."
            )
        except Exception as e:
            logger.error(f"Word raporu oluşturma hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Rapor oluşturulurken bir hata oluştu:\n{str(e)}")
