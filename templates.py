"""Hemşire Hasta Takip Sistemi - HTML Şablonları"""

import html

from config import NOTE_COLORS, get_patient_alerts


def welcome_dashboard_html(stats):
    """Ana dashboard HTML şablonu"""
    return f"""
    <table width='100%' cellpadding='0' cellspacing='0' style='font-family: Segoe UI, Arial, sans-serif; color: #dbdee1; background-color: #1e1f22;'>
        <tr><td style='padding: 40px 32px 16px 32px;'>
            <h1 style='font-size: 36px; color: #ffffff; margin: 0 0 6px 0; font-weight: bold;'>Hoş Geldiniz</h1>
            <p style='color: #72767d; font-size: 15px; margin: 0 0 28px 0;'>Hasta Odaları Yönetim Sistemi</p>
        </td></tr>
        <tr><td style='padding: 0 32px 40px 32px;'>
            <table width='100%' cellpadding='0' cellspacing='10'>
                <tr>
                    <td width='50%' style='background-color: #5865F2; padding: 28px 20px; text-align: center;'>
                        <div style='font-size: 52px; font-weight: bold; color: white; margin-bottom: 6px;'>{stats["toplam"]}</div>
                        <div style='font-size: 12px; color: rgba(255,255,255,0.85); font-weight: bold;'>TOPLAM HASTA</div>
                    </td>
                    <td width='50%' style='background-color: #7B68EE; padding: 28px 20px; text-align: center;'>
                        <div style='font-size: 52px; font-weight: bold; color: white; margin-bottom: 6px;'>{stats["dolu"]}</div>
                        <div style='font-size: 12px; color: rgba(255,255,255,0.85); font-weight: bold;'>DOLU ODALAR</div>
                    </td>
                </tr>
                <tr>
                    <td width='50%' style='background-color: #238636; padding: 28px 20px; text-align: center;'>
                        <div style='font-size: 52px; font-weight: bold; color: white; margin-bottom: 6px;'>{stats["bos"]}</div>
                        <div style='font-size: 12px; color: rgba(255,255,255,0.85); font-weight: bold;'>BOŞ ODALAR</div>
                    </td>
                    <td width='50%' style='background-color: #b8860b; padding: 28px 20px; text-align: center;'>
                        <div style='font-size: 52px; font-weight: bold; color: white; margin-bottom: 6px;'>{stats["yuzde"]}%</div>
                        <div style='font-size: 12px; color: rgba(255,255,255,0.85); font-weight: bold;'>DOLULUK</div>
                    </td>
                </tr>
            </table>
        </td></tr>
    </table>
    """


def build_timeline_html(notes):
    """Tedavi günlüğü timeline HTML'i oluştur"""
    if not notes:
        return """
        <table width='100%' cellpadding='0' cellspacing='0'>
            <tr><td style='text-align: center; padding: 32px 20px; color: #72767d;'>
                <div style='font-size: 40px; margin-bottom: 10px;'>📭</div>
                <div style='font-size: 14px; font-weight: bold; color: #b5bac1; margin-bottom: 4px;'>Henüz İşlem Kaydı Yok</div>
                <div style='font-size: 12px; color: #72767d;'>Yapılan işlemler burada görüntülenecek</div>
            </td></tr>
        </table>
        """
    
    timeline_items = []
    for note in reversed(notes):
        note_type = note.get("type", "Diğer")
        note_color = NOTE_COLORS.get(note_type, "#404249")
        safe_text = html.escape(note['text'])
        
        timeline_items.append(f"""
        <tr>
            <td width='6' style='background-color: {note_color};'></td>
            <td style='padding: 14px 16px; background-color: #2b2d31; border-bottom: 2px solid #1e1f22;'>
                <table width='100%' cellpadding='0' cellspacing='0'>
                    <tr>
                        <td>
                            <span style='background-color: {note_color}; color: white; padding: 3px 10px; font-size: 11px; font-weight: bold;'>{note_type}</span>
                            <span style='font-size: 11px; color: #72767d; margin-left: 10px;'>&nbsp;&nbsp;{note['time']}</span>
                        </td>
                    </tr>
                    <tr>
                        <td style='padding-top: 8px; color: #dbdee1; font-size: 13px;'>{safe_text}</td>
                    </tr>
                </table>
            </td>
        </tr>
        """)
    return f"<table width='100%' cellpadding='0' cellspacing='0'>{''.join(timeline_items)}</table>"


def build_alerts_html(p):
    """Hasta uyarı kartı HTML'i oluştur"""
    alerts = get_patient_alerts(p)
    if not alerts:
        return ""
    
    alert_rows = []
    for a in alerts:
        detail = html.escape(a["detail"]) if a["detail"] else ""
        label = html.escape(a["label"])
        if detail:
            text = f"{a['emoji']} <b>{label}:</b> {detail}"
        else:
            text = f"{a['emoji']} <b>{label}</b>"
        alert_rows.append(f"""
            <tr>
                <td style='padding: 6px 12px; color: #ff6b6b; font-size: 13px; border-bottom: 1px solid #3a3c41;'>{text}</td>
            </tr>
        """)
    
    return f"""
    <table width='100%' cellpadding='0' cellspacing='0' style='margin-bottom: 20px;'>
        <tr>
            <td style='background-color: #da3633; width: 5px;'></td>
            <td style='background-color: #2b2d31; padding: 0;'>
                <table width='100%' cellpadding='0' cellspacing='0'>
                    <tr>
                        <td style='padding: 10px 12px 6px 12px; font-size: 11px; font-weight: bold; color: #ff6b6b;'>🚨 AKTİF UYARILAR</td>
                    </tr>
                    {''.join(alert_rows)}
                </table>
            </td>
        </tr>
    </table>
    """


def patient_card_html(p):
    """Hasta detay kartı HTML şablonu"""
    safe_name = html.escape(str(p["name"]))
    safe_doctor = html.escape(str(p.get("doctor", "Belirtilmedi")))
    safe_diagnosis = html.escape(str(p["diagnosis"]))
    safe_anesthesia = html.escape(str(p["anesthesia"]))
    kayit_tarihi = p.get("date", "Bilinmiyor")
    gender_icon = "👨" if p.get("gender") == "Erkek" else "👩"
    note_count = len(p.get("notes", []))
    
    alerts_html = build_alerts_html(p)
    timeline_html = build_timeline_html(p.get("notes", []))
    
    return f"""
    <table width='100%' cellpadding='0' cellspacing='0' style='font-family: Segoe UI, Arial, sans-serif; background-color: #1e1f22;'>
        
        <!-- ═══════ HEADER ═══════ -->
        <tr>
            <td style='background-color: #5865F2; padding: 32px 28px; text-align: center;'>
                <div style='font-size: 36px; font-weight: bold; color: #ffffff; margin-bottom: 4px;'>{safe_name}</div>
                <div style='font-size: 12px; color: rgba(255,255,255,0.75);'>Hasta Kaydı&nbsp;&nbsp;•&nbsp;&nbsp;ID: {p.get("id", "-")[:8]}</div>
            </td>
        </tr>
        
        <!-- ═══════ STAT KARTLARI ═══════ -->
        <tr>
            <td style='padding: 16px 20px 8px 20px;'>
                <table width='100%' cellpadding='0' cellspacing='8'>
                    <tr>
                        <td width='33%' style='background-color: #2b2d31; text-align: center; padding: 18px 10px;'>
                            <div style='font-size: 11px; color: #5865F2; font-weight: bold; margin-bottom: 6px;'>🏥 ODA</div>
                            <div style='font-size: 36px; font-weight: bold; color: #ffffff;'>{p["room"]}</div>
                        </td>
                        <td width='33%' style='background-color: #2b2d31; text-align: center; padding: 18px 10px;'>
                            <div style='font-size: 11px; color: #7B68EE; font-weight: bold; margin-bottom: 6px;'>📅 YAŞ</div>
                            <div style='font-size: 36px; font-weight: bold; color: #ffffff;'>{p["age"]}</div>
                        </td>
                        <td width='33%' style='background-color: #2b2d31; text-align: center; padding: 18px 10px;'>
                            <div style='font-size: 11px; color: #E88D67; font-weight: bold; margin-bottom: 6px;'>{gender_icon} CİNSİYET</div>
                            <div style='font-size: 24px; font-weight: bold; color: #ffffff;'>{p["gender"]}</div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        
        <!-- ═══════ UYARILAR ═══════ -->
        <tr>
            <td style='padding: 8px 20px 0 20px;'>
                {alerts_html}
            </td>
        </tr>
        
        <!-- ═══════ DOKTOR & TARİH ═══════ -->
        <tr>
            <td style='padding: 4px 20px;'>
                <table width='100%' cellpadding='0' cellspacing='8'>
                    <tr>
                        <td width='50%' style='background-color: #2b2d31; padding: 0;'>
                            <table width='100%' cellpadding='0' cellspacing='0'>
                                <tr>
                                    <td width='5' style='background-color: #5865F2;'></td>
                                    <td style='padding: 14px 16px;'>
                                        <div style='font-size: 10px; color: #5865F2; font-weight: bold; margin-bottom: 8px;'>👨‍⚕️ SORUMLU DOKTOR</div>
                                        <div style='font-size: 18px; color: #ffffff; font-weight: bold;'>{safe_doctor}</div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                        <td width='50%' style='background-color: #2b2d31; padding: 0;'>
                            <table width='100%' cellpadding='0' cellspacing='0'>
                                <tr>
                                    <td width='5' style='background-color: #7B68EE;'></td>
                                    <td style='padding: 14px 16px;'>
                                        <div style='font-size: 10px; color: #7B68EE; font-weight: bold; margin-bottom: 8px;'>📅 YATIŞ TARİHİ</div>
                                        <div style='font-size: 15px; color: #ffffff; font-weight: bold;'>{kayit_tarihi}</div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        
        <!-- ═══════ TANI & ANESTEZİ ═══════ -->
        <tr>
            <td style='padding: 4px 20px;'>
                <table width='100%' cellpadding='0' cellspacing='8'>
                    <tr>
                        <td width='50%' style='background-color: #2b2d31; padding: 0;'>
                            <table width='100%' cellpadding='0' cellspacing='0'>
                                <tr>
                                    <td width='5' style='background-color: #E5A00D;'></td>
                                    <td style='padding: 14px 16px;'>
                                        <div style='font-size: 10px; color: #E5A00D; font-weight: bold; margin-bottom: 8px;'>🩺 TANI (TEŞHİS)</div>
                                        <div style='font-size: 14px; color: #dbdee1;'>{safe_diagnosis if safe_diagnosis else '<i style="color:#72767d;">Belirtilmedi</i>'}</div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                        <td width='50%' style='background-color: #2b2d31; padding: 0;'>
                            <table width='100%' cellpadding='0' cellspacing='0'>
                                <tr>
                                    <td width='5' style='background-color: #58D68D;'></td>
                                    <td style='padding: 14px 16px;'>
                                        <div style='font-size: 10px; color: #58D68D; font-weight: bold; margin-bottom: 8px;'>💉 ANESTEZİ TÜRÜ</div>
                                        <div style='font-size: 14px; color: #dbdee1;'>{safe_anesthesia if safe_anesthesia else '<i style="color:#72767d;">Belirtilmedi</i>'}</div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        
        <!-- ═══════ TEDAVİ GÜNLÜĞÜ ═══════ -->
        <tr>
            <td style='padding: 16px 20px 4px 20px;'>
                <table width='100%' cellpadding='0' cellspacing='0'>
                    <tr>
                        <td style='padding: 0 0 12px 0;'>
                            <table width='100%' cellpadding='0' cellspacing='0'>
                                <tr>
                                    <td style='font-size: 11px; font-weight: bold; color: #5865F2;'>📝 TEDAVİ GÜNLÜĞÜ & İŞLEM KAYDI</td>
                                    <td style='text-align: right; font-size: 11px; color: #72767d;'>{note_count} kayıt</td>
                                </tr>
                            </table>
                            <hr style='border: none; border-top: 1px solid #313338; margin-top: 8px;'/>
                        </td>
                    </tr>
                    <tr>
                        <td>{timeline_html}</td>
                    </tr>
                </table>
            </td>
        </tr>
        
        <!-- ═══════ FOOTER ═══════ -->
        <tr>
            <td style='padding: 12px 20px 20px 20px; text-align: center;'>
                <div style='font-size: 10px; color: #4e5058;'>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</div>
                <div style='font-size: 10px; color: #4e5058; margin-top: 4px;'>Hemşire Hasta Takip Sistemi</div>
            </td>
        </tr>
        
    </table>
    """
