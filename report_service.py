"""Hemşire Hasta Takip Sistemi - Rapor Servisi

Word (docx) nöbet teslim raporu oluşturma mantığı.
UI bağımsızdır; dosya adını veya hata mesajını döndürür.
"""

import os
import logging
from datetime import datetime

from config import DATE_FORMAT, get_patient_alerts

logger = logging.getLogger(__name__)


def generate_word_report(data, room_settings):
    """Word raporu oluştur.

    Döndürür: (dosya_adı | None, başarılı, hata_mesajı | None)
    """
    try:
        from docx import Document
        from docx.shared import Pt, Inches
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError:
        return None, False, (
            "python-docx kütüphanesi yüklü değil.\n"
            "Yüklemek için: pip install python-docx"
        )

    if not data:
        return None, False, "Çıktı alınacak hasta bulunamadı!"

    doc = Document()
    for section in doc.sections:
        section.top_margin = section.bottom_margin = Inches(0.5)
        section.left_margin = section.right_margin = Inches(0.5)

    # Başlık
    title = doc.add_heading("", level=0)
    run = title.add_run("🏥 HASTA TAKİP SİSTEMİ\nNÖBET TESLİM RAPORU")
    run.font.size = Pt(20)
    run.bold = True
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Bilgi satırı
    unique_rooms = len({p["room"] for p in data})
    info = doc.add_paragraph()
    info.add_run(
        f"📅 Hazırlama Tarihi: {datetime.now().strftime(DATE_FORMAT)}\n"
    ).bold = True
    info.add_run(
        f"📊 Toplam Hasta: {len(data)} | "
        f"Dolu Oda: {unique_rooms} | "
        f"Boş Oda: {len(room_settings) - unique_rooms}\n"
    ).font.size = Pt(14)
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("_" * 80)

    # Hasta tablosu
    table = doc.add_table(rows=1, cols=9)
    table.style = "Light Grid Accent 1"

    headers = [
        "Oda", "Ad Soyad", "Yaş", "Cinsiyet", "Doktor",
        "Uyarılar", "Tanı", "Anestezi", "Yatış Tarihi",
    ]
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for para in cell.paragraphs:
            for r in para.runs:
                r.font.bold = True
                r.font.size = Pt(14)
                r.font.color.rgb = None

    sorted_data = sorted(data, key=lambda x: int(x.get("room", 0)))

    for p in sorted_data:
        alerts = get_patient_alerts(p)
        uyari = "\n".join(
            f"{a['emoji']} {a['label']}: {a['detail']}" if a["detail"]
            else f"{a['emoji']} {a['label']}"
            for a in alerts
        ) if alerts else "-"

        rc = table.add_row().cells
        rc[0].text = str(p["room"]).zfill(2)
        rc[1].text = p["name"].upper()
        rc[2].text = str(p["age"])
        rc[3].text = p["gender"]
        rc[4].text = p.get("doctor", "Belirtilmedi")
        rc[5].text = uyari
        rc[6].text = p["diagnosis"]
        rc[7].text = p["anesthesia"]
        rc[8].text = p.get("date", "-")

        if alerts:
            for para in rc[5].paragraphs:
                for r in para.runs:
                    r.bold = True

    # Tedavi notları
    patients_with_notes = [p for p in sorted_data if p.get("notes")]
    if patients_with_notes:
        doc.add_paragraph()
        nh = doc.add_heading("", level=1)
        nr = nh.add_run("📝 TEDAVİ GÜNLÜKLERİ")
        nr.font.size = Pt(16)
        nr.bold = True

        for p in patients_with_notes:
            doc.add_heading(f"Oda {p['room']} - {p['name']}", level=2)
            for note in p["notes"]:
                np = doc.add_paragraph()
                np.add_run(f"[{note.get('type', 'Diğer')}] ").bold = True
                np.add_run(f"{note.get('time', '-')} — {note.get('text', '')}")

    doc.add_paragraph()
    footer = doc.add_paragraph()
    footer.add_run("Not: ").bold = True
    footer.add_run(
        "Bu rapor otomatik olarak Hemşire Hasta Takip Sistemi tarafından oluşturulmuştur."
    )
    fr = footer.add_run(
        f"\nSayfa Oluşturma: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
    )
    fr.italic = True
    footer.alignment = WD_ALIGN_PARAGRAPH.LEFT

    dosya_adi = f"Hasta_Raporu_{datetime.now().strftime('%d_%m_%Y_%H%M%S')}.docx"
    doc.save(dosya_adi)
    logger.info(f"Word raporu oluşturuldu: {dosya_adi}")
    return dosya_adi, True, None
