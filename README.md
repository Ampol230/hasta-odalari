# 🏥 Hemşire Hasta Takip Sistemi

Hastanede hasta kayıtlarını ve oda yönetimini kolaylaştıran profesyonel bir masaüstü uygulaması.

## 📋 Özellikler

✅ **Hasta Yönetimi**
- Yeni hasta kaydı ekle
- Hasta bilgilerini düzenle
- Hasta taburcu etme
- Arama ve filtreleme

✅ **Oda Yönetimi**
- 16 odaya kadar hasta atama
- Oda kapasite kontrol (Maksimum 2 hasta/oda)
- Oda durumu görüntüleme (Boş/Dolu)
- Oda haritası (Krokisi)

✅ **Tedavi Takibi**
- Tedavi günlüğü (İşlem/Not)
- 5 farklı işlem türü:
  - Muayene
  - İlaç
  - Ameliyat Öncesi Hazırlık
  - Tıbbi İşlem
  - Diğer

✅ **Uyarı Sistemi**
- Alerji bildirimi
- Aç Kalma (NPO) belirtmesi
- Düşme riski uyarısı

✅ **Raporlama**
- Word (DOCX) formatında rapor oluşturma
- Yazıcıya gönderme
- Otomatik tarihli rapor dosyaları

✅ **Veri Güvenliği**
- Otomatik günlük yedekleme
- JSON tabanlı veri depolama
- Detaylı uygulamaa günlüğü (log)

## 🚀 Kurulum

### 1. Python Ortamı Hazırlama

```bash
# Proje klasörüne gir
cd "Hasta odaları"

# Virtual environment oluştur
python -m venv .venv

# Virtual environment'i aktive et
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# Windows (CMD):
.\.venv\Scripts\activate.bat

# macOS/Linux:
source .venv/bin/activate
```

### 2. Gerekli Kütüphaneleri Yükle

```bash
pip install -r requirements.txt
```

### 3. Uygulamayı Çalıştır

```bash
python Hastaodaları.py
```

## 💾 Dosya Yapısı

```
Hasta odaları/
├── Hastaodaları.py          # Ana uygulama dosyası
├── config.py                # Yapılandırma ayarları
├── requirements.txt         # Bağımlılıklar
├── README.md               # Bu dosya
├── hastalar.json           # Hasta veritabanı
├── hastaodasi.log          # Uygulamaa günlüğü
├── ÇALIŞTIR.bat           # Hızlı başlatma (Windows)
├── .venv/                 # Virtual environment
└── Yedekler/              # Otomatik yedeklemeler
    ├── yedek_27_03_2026.json
    ├── yedek_28_03_2026.json
    └── yedek_29_03_2026.json
```

## 📖 Kullanım Rehberi

### Yeni Hasta Kaydı

1. **➕ Yeni Kayıt** butonuna tıkla
2. Hasta bilgilerini doldur:
   - Ad Soyad (Zorunlu)
   - Yaş (Zorunlu)
   - Cinsiyet
   - Oda No (1-16)
   - Doktor Adı
   - Tanı (Teşhis)
   - Anestezi Türü
3. Uyarıları işaretле (varsa):
   - 🩸 Alerjisi Var (Alerji türünü belirt)
   - 🛑 Aç Kalacak (Ameliyat/Tahlil Öncesi)
   - ⚠️ Düşme Riski Yüksek
4. **💾 Kaydet** butonuna tıkla

### Hasta Bilgilerini Düzenle

1. Hasta listesinden hasta seçinсе İsminize tıkla
2. **✏ Düzenle** butonuna tıkla
3. Bilgileri güncelle
4. **💾 Kaydet** butonuna tıkla

### İşlem/Not Ekle

1. Hasta listesinden hasta seçinisе İsmine tıkla
2. **📝 İşlem/Not Ekle** butonuna tıkla
3. İşlem türünü seçer:
   - Muayene
   - İlaç
   - Ameliyat Öncesi Hazırlık
   - Tıbbi İşlem
   - Diğer
4. İşlem detaylarını yazrу
5. **Tamam** butonuna tıkla

### Taburcu İşlemi

1. Hasta listesinden hasta seçin
2. **👋 Taburcu Et** butonuna tıkla
3. Onayı verrę hasta sistemden kaldırılır

### Oda Haritasını Görüntüle

1. **🏥 Oda Krokisi** butonuna tıkla
2. Odaların durumunu gör:
   - 🟢 Yeşil: Boş oda
   - 🟡 Sarı: 1 hastaya sahip oda
   - 🔴 Kırmızı: Dolu oda (2 hasta)

### Word Raporu Oluşturma

1. **📄 Word Kaydet** butonuna tıkla
2. Otomatik olarak:
   - Rapor dosyası oluşturulur
   - Yazıcıya gönderilir
   - Tarihli dosya adı verilir (Hasta_Raporu_29_03_2026_14_30_15.docx)

## ⚙️ Yapılandırma

`config.py` dosyasında aşağıdaki ayarları değiştirebilirsin:

```python
TOTAL_ROOMS = 16              # Toplam oda sayısı
MAX_PATIENTS_PER_ROOM = 2    # Oda başına maksimum hasta sayısı
COLORS = {...}               # Tema renkleri
```

## 🔧 Sistem Gereksinimleri

- **Python**: 3.8 veya üstü
- **İşletim Sistemi**: Windows / macOS / Linux
- **RAM**: Minimum 2 GB
- **Disk**: ~500 MB (virtual environment dahil)

## 📦 Bağımlılıklar

| Paket | Sürüm | Açıklama |
|-------|-------|----------|
| PySide6 | 6.11.0 | Qt tabanlı GUI kütüphane sitesi |
| python-docx | 1.2.0 | Word DOCX dosyası oluşturma |

## 🐛 Sorun Giderme

### Problem: "PySide6" modülü bulunamadı

```bash
pip install PySide6==6.11.0
```

### Problem: "python-docx" modülü bulunamadı

```bash
pip install python-docx==1.2.0
```

### Problem: PowerShell'de aktivasyon hataı

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Ardından:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Problem: Veriler kaydolmadivak

1. `hastalar.json` dosyasının yazma izni olduğundan emin ol
2. `hastaodasi.log` dosyasını kontrol et (hata mesajları içerir)

## 📊 Veri Yedekleme

Uygulama her açılışında otomatik yedek oluşturur:
- Yedekler `Yedekler/` klasörü altında saklanır
- Dosya adı: `yedek_GÜN_AY_YIL.json`
- Eski sürüm dosyaları silinmez (manuel silme gerekir)

### Veri Geri Yükleme

1. `Yedekler/` klasöründen istediğin yedek dosyasını seç
2. Dosyayı kopyala ve `hastalar.json` adıyla ana klasöre yapıştır
3. Uygulamayı yeniden başlat

## 👨‍⚕️ Desteklenen İşlem Türleri

| İkon | İşlem Türü | Açıklama | Renk |
|------|----------|----------|------|
| 🔵 | Muayene | Doktor / Hemşire muayeneleri | Mavi |
| 🟢 | İlaç | İlaç uygulamaları | Yeşil |
| 🟠 | Ameliyat Öncesi | Ameliyat hazırlık işlemleri | Turuncu |
| 🟡 | Tıbbi İşlem | Kan alma, tahlil v.b. | Sarı |
| ⚫ | Diğer | Diğer önemli olaylar | Gri |

## 📝 Lisans

Bu yazılım öğrenme ve eğitim amaçlı geliştirilmiştir.

## 📞 İletişim

Sorular veya öneriler için lütfen iletişime geç.

---

**Versiyon**: 1.0.0  
**Son Güncelleme**: 29 Mart 2026  
**Geliştirici**: Sağlık Bilişimi Ekibi
