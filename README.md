# ⚽ Futbol Bahis Analiz Sistemi

Profesyonel Value Bet Analizi ve Yapay Zeka Destekli Tahmin Motoru

## 📋 Özellikler

✅ **Modüler Mimarı** - 7 ana bileşen ile temiz kod yapısı  
✅ **RapidAPI Entegrasyonu** - API-Football ve Boundaries API'ler  
✅ **Matematiksel Filtreleme** - Gelişmiş Value Bet analizi  
✅ **GPT-4 Analitik** - Türkçe raporlama ve yorumlama  
✅ **Üretim Hazır** - Kapsamlı hata yönetimi  
✅ **Merkezi Loglama** - Konsol ve dosya loglama sistemi  
✅ **Coğrafi Konum Verisi** - Boundaries API entegrasyonu  

## 🚀 Kurulum

### 1. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### 2. API Anahtarlarını Ayarla

```bash
# .env dosyası oluştur
export OPENAI_API_KEY="your-openai-api-key-here"
```

Veya `main.py` içindeki `Config` sınıfını düzenle:

```python
RAPIDAPI_KEY = "your-api-key"
RAPIDAPI_HOST = "api-football-v3.p.rapidapi.com"
OPENAI_API_KEY = "your-openai-key"
```

### 3. Programı Çalıştır

```bash
python main.py
```

## 🏗️ Sistem Mimarisi

```
┌──────────────────────────────────────────────────────────────────┐
│         FUTBOL BAHİS ANALİZ SİSTEMİ                        │
└──────────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
    ┌─────┴──────┐  ┌─────┴──────────┐  ┌──┴──────────────────────┐
    │   Veri    │  │  Matematiksel  │  │   AI Analiz  │
    │  Çekme    │  │  Filtreleme    │  │   Motoru     │
    │ (RapidAPI)│  │ (Value Bets)   │  │  (OpenAI)    │
    └─────┬──────┘  └─────┬──────────┘  └──┬──────────────────────┘
          │               │              │
          └───────────────┼──────────────┘
                    │
           ┌────────┴──────────┐
           │ Rapor Oluşturma  │
           │  (Markdown)      │
           └────────┬──────────┘
                 │
        ┌────────┴─────────┐
        │                 │
   ┌────┴──────┐       ┌──┴──────────┐
   │ Ekrana    │       │ Dosyaya    │
   │Yazdır     │       │ Kaydet     │
   └───────────┘       └────────────┘
```

## 📊 Ana Bileşenler

### 1. **Config (Yapılandırma)**
- RapidAPI anahtarları
- OpenAI modeli seçimi
- Oran düşüş eşiği (%10 varsayılan)
- API uç noktaları

### 2. **FootballDataFetcher (Veri Çekme)**
```python
# Günlük maçları çek
fixtures = fetcher.get_daily_fixtures(days_ahead=1)

# Belirli maçın oranlarını çek
odds = fetcher.get_odds_for_fixture(fixture_id)

# Coğrafi konum verileri
boundary = fetcher.get_boundary_data(lat, lon)
```

### 3. **ValueBetAnalyzer (Matematik Motoru)**
```python
# Oran düşüşü hesapla
drop = analyzer.calculate_odds_drop(opening=2.5, current=2.3)  # %8

# Value bet filtrele
value_bets = analyzer.filter_value_bets(fixtures)
```

**Formül:**
```
Düşüş % = ((Açılış Oranı - Güncel Oran) / Açılış Oranı) × 100
```

### 4. **AIAnalysisEngine (Yapay Zeka)**
- GPT-4 Turbo kullanımı
- Türkçe analiz raporu
- Oran düşüşü yorumlaması
- Risk/Reward değerlendirmesi

### 5. **ReportGenerator (Raporlama)**
- Markdown formatında rapor
- Tablo oluşturma
- Dosya kaydetme
- Ekrana yazdırma

## ⚙️ Yapılandırma Seçenekleri

### Oran Düşüş Eşiğini Değiştir
```python
config.ODDS_DROP_THRESHOLD = 0.15  # %15'e yükselt
```

### Farklı Tarihler için Analiz
```python
# 2 gün sonrasını analiz et
orchestrator.run(days_ahead=2)
```

### Log Seviyesi
```python
logger.setLevel(logging.DEBUG)  # Detaylı loglama
```

## 📁 Çıktı Dosyaları

### gunluk_analiz_raporu.md
```markdown
# ⚽ GÜNLÜK FUTBOL BAHİS ANALİZ RAPORU

**Raporun Oluşturulduğu Tarih:** 2024-01-15 14:30:00

## 📊 Özet Bilgiler
- Toplam Analiz Edilen Maç: 5
- Oran Düşüş Eşiği: 10%

## 🎯 Filtrelenmiş Value Bet'ler
| # | Ev Sahibi | Deplasman | Lig | Market | Açılış | Güncel | Düşüş |
|---|-----------|-----------|-----|--------|--------|--------|-------|
| 1 | Barcelona | Real Madrid | La Liga | Ev Sahibi | 2.50 | 2.30 | 8.00% |

## 🤖 YAPAY ZEKA TARAFINDAN OLUŞTURULAN ANALİZ
[AI Analiz Raporu]
```

### sistem.log
```
2024-01-15 14:30:00 - BettingAnalyzer - INFO - 🚀 FUTBOL BAHİS ANALİZ SİSTEMİ BAŞLATILIYOR
2024-01-15 14:30:01 - BettingAnalyzer - INFO - Maçlar çekiliyor: 2024-01-16
2024-01-15 14:30:02 - BettingAnalyzer - INFO - ✅ 245 maç başarıyla çekildi
...
```

## 🔌 API Entegrasyonları

### RapidAPI - API-Football
```bash
curl --request GET \
  --url 'https://api-football-v3.p.rapidapi.com/fixtures?date=2024-01-16' \
  --header 'x-rapidapi-host: api-football-v3.p.rapidapi.com' \
  --header 'x-rapidapi-key: YOUR_KEY'
```

### RapidAPI - Boundaries
```bash
curl --request GET \
  --url 'https://vanitysoft-boundaries-io-v1.p.rapidapi.com/reaperfire/rest/v1/public/boundary/place/within?latitude=45.507&longitude=-122.809' \
  --header 'x-rapidapi-key: YOUR_KEY'
```

## 📈 Örnek Çıktı

```
⚽ FUTBOL BAHİS ANALİZ SİSTEMİ

📋 SİSTEM AYARLARI
  • RapidAPI Host: api-football-v3.p.rapidapi.com
  • OpenAI Model: gpt-4-turbo
  • Oran Düşüş Eşiği: 10%
  • Rapor Dosyası: gunluk_analiz_raporu.md
  • Log Dosyası: sistem.log

ADIM 1/4: Futbol maçları çekiliyor...
✅ 245 maç başarıyla çekildi

ADIM 2/4: Value bet'ler filtreleniyor...
📊 12 value bet filtrelenmiştir

ADIM 3/4: Yapay zeka analizi yapılıyor...
🤖 OpenAI API'ye istek gönderiliyor...
✅ AI analizi başarıyla tamamlandı

ADIM 4/4: Rapor oluşturuluyor...
✅ Rapor başarıyla kaydedildi: gunluk_analiz_raporu.md
✅ Tüm işlemler başarıyla tamamlandı!
```

## ⚠️ Dikkat

Bu sistem **yalnızca analiz amaçlıdır**. Bahis yapma kararlarında:
- Profesyonel danışmanlarla görüşün
- Kendi risk yönetim stratejinizi geliştirin
- Kesin kazanç garantisi olmadığını hatırlayın

## 📝 Lisans

MIT License

## 👨‍💻 Geliştirme

### Gelecek Özellikler
- [ ] Canlı oran izleme
- [ ] Veritabanı entegrasyonu
- [ ] Web dashboard
- [ ] Telegram notifikasyon
- [ ] Historik veri analizi

### Katkıda Bulun
1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit yapın (`git commit -m 'Add AmazingFeature'`)
4. Push yapın (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📞 İletişim

Sorun veya öneriniz için GitHub Issues açın.

---

**Son Güncelleme:** 2024-01-15  
**Versiyon:** 1.0.0
