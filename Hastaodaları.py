"""Hemşire Hasta Takip Sistemi - Başlatıcı"""

import sys
import time
import logging
import ctypes

from config import LOG_FILE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

_mutex_handle = None


def _ensure_single_instance():
    """Windows mutex ile tek örnek kontrolü."""
    global _mutex_handle
    try:
        _mutex_handle = ctypes.windll.kernel32.CreateMutexW(
            None, False, "HemsireHastaTakipSistemi_Mutex"
        )
        if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            return False
    except Exception:
        pass  # Mutex desteklenmiyorsa devam et
    return True


if __name__ == "__main__":
    try:
        logger.info("=== UYGULAMA BAŞLATILDI ===")

        if not _ensure_single_instance():
            logger.warning("Uygulama zaten çalışıyor — çıkılıyor")
            from PySide6.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            QMessageBox.warning(
                None, "Zaten Çalışıyor",
                "Hemşire Hasta Takip Sistemi zaten açık.\n"
                "Birden fazla kopya çalıştırılamaz."
            )
            sys.exit(1)

        from PySide6.QtWidgets import QApplication, QSplashScreen
        from PySide6.QtGui import QPixmap, QFont, QColor, QPainter
        from PySide6.QtCore import Qt

        app = QApplication(sys.argv)

        # Splash screen
        splash_pixmap = QPixmap(600, 400)
        splash_pixmap.fill(QColor("#1e1f22"))

        painter = QPainter(splash_pixmap)

        title_font = QFont("Segoe UI", 48, QFont.Bold)
        painter.setFont(title_font)
        painter.setPen(QColor("#5865F2"))
        painter.drawText(splash_pixmap.rect(), Qt.AlignCenter | Qt.AlignTop, "\n🏥")

        title_font2 = QFont("Segoe UI", 28, QFont.Bold)
        painter.setFont(title_font2)
        painter.setPen(QColor("#dbdee1"))
        painter.drawText(splash_pixmap.rect(), Qt.AlignCenter | Qt.AlignTop,
                        "Hemşire Hasta\nTakip Sistemi\n")

        credits_font = QFont("Segoe UI", 12)
        painter.setFont(credits_font)
        painter.setPen(QColor("#a6a6a6"))
        painter.drawText(splash_pixmap.rect(), Qt.AlignCenter | Qt.AlignBottom,
                        "Hazırlayan: Melik Börüde\nSürüm 1.0.0  •  29.03.2026\n")

        painter.end()

        splash = QSplashScreen(splash_pixmap)
        splash.show()
        app.processEvents()

        splash.showMessage("Veritabanı yükleniyor...", Qt.AlignBottom | Qt.AlignCenter, QColor("#5865F2"))
        app.processEvents()
        time.sleep(0.3)

        splash.showMessage("Arayüz hazırlanıyor...", Qt.AlignBottom | Qt.AlignCenter, QColor("#5865F2"))
        app.processEvents()
        time.sleep(0.3)

        splash.showMessage("Hoş geldiniz!", Qt.AlignBottom | Qt.AlignCenter, QColor("#238636"))
        app.processEvents()
        time.sleep(0.5)

        from main_window import HastaDefter

        window = HastaDefter()
        window.show()
        splash.finish(window)

        logger.info("Arayüz görüntülendi")
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Uygulamada kritik hata: {e}")
        print(f"HATA: {e}")
        sys.exit(1)
