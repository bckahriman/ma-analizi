#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚽ FUTBOL BAHİS ANALİZ SİSTEMİ
Profesyonel Value Bet Analizi ve Yapay Zeka Destekli Tahmin Motoru

Author: Betting Analysis AI
Version: 1.0.0
License: MIT
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
from openai import OpenAI

# ============================================================================
# 1. PROJE AYARLARI VE YAPILANDIRMA
# ============================================================================

@dataclass
class Config:
    """Merkezi yapılandırma sınıfı"""
    # RapidAPI Anahtarları
    RAPIDAPI_KEY: str = "78aec092a2msh9b342eed4039318p11aac6jsn5dd4db6da9a7"
    RAPIDAPI_HOST: str = "api-football-v3.p.rapidapi.com"
    
    # OpenAI Yapılandırması
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "sk-your-api-key-here")
    OPENAI_MODEL: str = "gpt-4-turbo"
    
    # Bahis Parametreleri
    ODDS_DROP_THRESHOLD: float = 0.10  # %10 - Düşüş eşiği
    
    # Çıktı Ayarları
    REPORT_FILE: str = "gunluk_analiz_raporu.md"
    LOG_FILE: str = "sistem.log"
    
    # API Uç Noktaları
    FIXTURES_ENDPOINT: str = "https://api-football-v3.p.rapidapi.com/fixtures"
    ODDS_ENDPOINT: str = "https://api-football-v3.p.rapidapi.com/odds"
    BOUNDARIES_ENDPOINT: str = "https://vanitysoft-boundaries-io-v1.p.rapidapi.com/reaperfire/rest/v1/public/boundary/place/within"

# ============================================================================
# 2. LOGLAMA SİSTEMİ
# ============================================================================

def setup_logging(config: Config) -> logging.Logger:
    """Merkezi loglama sistemini konfigure et"""
    logger = logging.getLogger("BettingAnalyzer")
    logger.setLevel(logging.DEBUG)
    
    # Konsol handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Dosya handler
    file_handler = logging.FileHandler(config.LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# ============================================================================
# 3. VERİ ÇEKME MODÜLÜ (RapidAPI ENTEGRASYONU)
# ============================================================================

class FootballDataFetcher:
    """RapidAPI ile futbol verileri çeken sınıf"""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.headers = {
            "x-rapidapi-key": config.RAPIDAPI_KEY,
            "x-rapidapi-host": config.RAPIDAPI_HOST,
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_daily_fixtures(self, days_ahead: int = 1) -> List[Dict]:
        """
        Belirtilen günün futbol maçlarını çek
        
        Args:
            days_ahead: Bugünden kaç gün ileri (0=bugün, 1=yarın)
        
        Returns:
            Maç verilerinin listesi
        """
        try:
            target_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
            params = {
                "date": target_date,
                "league": "-",  # Tüm ligler
                "season": datetime.now().year
            }
            
            self.logger.info(f"Maçlar çekiliyor: {target_date}")
            response = self.session.get(
                self.config.FIXTURES_ENDPOINT,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            fixtures = data.get("response", [])
            
            self.logger.info(f"✅ {len(fixtures)} maç başarıyla çekildi")
            return fixtures
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Maçlar çekilirken hata: {str(e)}")
            return []
    
    def get_odds_for_fixture(self, fixture_id: int, bookmaker: str = "1") -> Optional[Dict]:
        """
        Belirli bir maçın oranlarını çek
        
        Args:
            fixture_id: Maç ID'si
            bookmaker: Bahis şirketi ID'si
        
        Returns:
            Oran verisi veya None
        """
        try:
            params = {
                "fixture": fixture_id,
                "bookmaker": bookmaker
            }
            
            response = self.session.get(
                self.config.ODDS_ENDPOINT,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("response", {})
            
        except requests.exceptions.RequestException as e:
            self.logger.debug(f"⚠️ Oranlar çekilirken hata (Fixture {fixture_id}): {str(e)}")
            return None
    
    def get_boundary_data(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Coğrafi konum verisi çek (İsteğe bağlı genişletme)
        
        Args:
            latitude: Enlem
            longitude: Boylam
        
        Returns:
            Sınır verileri
        """
        try:
            headers = {
                "x-rapidapi-key": self.config.RAPIDAPI_KEY,
                "x-rapidapi-host": "vanitysoft-boundaries-io-v1.p.rapidapi.com",
                "Content-Type": "application/json"
            }
            
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "combine": False
            }
            
            response = requests.get(
                self.config.BOUNDARIES_ENDPOINT,
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.debug(f"⚠️ Boundary verileri çekilirken hata: {str(e)}")
            return None

# ============================================================================
# 4. MATEMATİKSEL VALUE BET FİLTRESİ
# ============================================================================

@dataclass
class ValueBet:
    """Value Bet veri modeli"""
    match_id: int
    home_team: str
    away_team: str
    league: str
    match_date: str
    market_type: str  # "1" (ev sahibi), "X" (beraberlik), "2" (deplasman)
    opening_odds: float
    current_odds: float
    odds_drop_percentage: float
    market_type_name: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ValueBetAnalyzer:
    """Value bet filtreleme ve analiz motoru"""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
    
    def calculate_odds_drop(self, opening: float, current: float) -> float:
        """
        Oran düşüş yüzdesini hesapla
        
        Formül: ((Açılış Oranı - Güncel Oran) / Açılış Oranı) * 100
        
        Args:
            opening: Açılış oranı
            current: Güncel oran
        
        Returns:
            Düşüş yüzdesi (0-100 arası)
        """
        if opening == 0:
            return 0
        
        drop = ((opening - current) / opening) * 100
        return max(0, drop)  # Negatif değerleri 0'a ayarla
    
    def is_value_bet(self, odds_drop: float) -> bool:
        """
        Oran düşüşü belirlenen eşiği aşıyorsa value bet olarak işaretle
        
        Args:
            odds_drop: Düşüş yüzdesi
        
        Returns:
            Value bet mi?
        """
        return odds_drop >= (self.config.ODDS_DROP_THRESHOLD * 100)
    
    def filter_value_bets(self, fixtures: List[Dict]) -> List[ValueBet]:
        """
        Maçları analiz ederek value bet'leri filtrele
        
        Args:
            fixtures: Maçların listesi
        
        Returns:
            Value bet'lerin listesi
        """
        value_bets = []
        
        for fixture in fixtures:
            try:
                fixture_id = fixture.get("fixture", {}).get("id")
                home_team = fixture.get("teams", {}).get("home", {}).get("name", "Bilinmiyor")
                away_team = fixture.get("teams", {}).get("away", {}).get("name", "Bilinmiyor")
                league = fixture.get("league", {}).get("name", "Bilinmiyor")
                match_date = fixture.get("fixture", {}).get("date", "")
                
                # Simüle edilmiş oran verileri (Gerçek uygulamada RapidAPI'den gelir)
                markets = self._get_simulated_odds(fixture_id)
                
                for market_type, odds_data in markets.items():
                    opening_odds = odds_data.get("opening", 0)
                    current_odds = odds_data.get("current", 0)
                    
                    if opening_odds <= 0 or current_odds <= 0:
                        continue
                    
                    odds_drop = self.calculate_odds_drop(opening_odds, current_odds)
                    
                    if self.is_value_bet(odds_drop):
                        market_names = {"1": "Ev Sahibi", "X": "Beraberlik", "2": "Deplasman"}
                        
                        value_bet = ValueBet(
                            match_id=fixture_id,
                            home_team=home_team,
                            away_team=away_team,
                            league=league,
                            match_date=match_date,
                            market_type=market_type,
                            opening_odds=opening_odds,
                            current_odds=current_odds,
                            odds_drop_percentage=odds_drop,
                            market_type_name=market_names.get(market_type, "Bilinmiyor")
                        )
                        value_bets.append(value_bet)
                        
                        self.logger.debug(
                            f"🎯 Value Bet: {home_team} vs {away_team} "
                            f"({market_names.get(market_type)}) - "
                            f"Düşüş: {odds_drop:.2f}%"
                        )
            
            except (KeyError, TypeError) as e:
                self.logger.debug(f"⚠️ Maç işlenirken hata: {str(e)}")
                continue
        
        self.logger.info(f"📊 {len(value_bets)} value bet filtrelenmiştir")
        return value_bets
    
    def _get_simulated_odds(self, fixture_id: int) -> Dict:
        """
        Simüle edilmiş oran verileri
        (Gerçek uygulamada RapidAPI'den API çağrısıyla gelir)
        
        Args:
            fixture_id: Maç ID'si
        
        Returns:
            Oran verisi
        """
        # Gerçek uygulama için RapidAPI çağrısı yapılacak
        import random
        
        base_odds = random.uniform(1.5, 3.5)
        current_odds = base_odds * random.uniform(0.85, 1.10)
        
        return {
            "1": {
                "opening": base_odds,
                "current": current_odds
            },
            "X": {
                "opening": 3.0,
                "current": 2.85
            },
            "2": {
                "opening": 2.5,
                "current": 2.3
            }
        }

# ============================================================================
# 5. YAPAY ZEKA ANALİZ MOTORU
# ============================================================================

class AIAnalysisEngine:
    """OpenAI API ile yapay zeka analizi gerçekleştiren sınıf"""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        
        # OpenAI istemcisi
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    def format_value_bets_for_analysis(self, value_bets: List[ValueBet]) -> str:
        """
        Value bet'leri AI analizine uygun formata dönüştür
        
        Args:
            value_bets: Value bet'lerin listesi
        
        Returns:
            Formatlı metin
        """
        if not value_bets:
            return "Analiz için veri bulunmamaktadır."
        
        formatted = "```\n"
        formatted += f"{'='*80}\n"
        formatted += f"TÜM VALUE BET'LER ({len(value_bets)} maç)\n"
        formatted += f"{'='*80}\n\n"
        
        for i, bet in enumerate(value_bets, 1):
            formatted += f"{i}. {bet.home_team} vs {bet.away_team}\n"
            formatted += f"   Lig: {bet.league}\n"
            formatted += f"   Tarih: {bet.match_date}\n"
            formatted += f"   Market: {bet.market_type_name}\n"
            formatted += f"   Açılış Oranı: {bet.opening_odds:.2f}\n"
            formatted += f"   Güncel Oran: {bet.current_odds:.2f}\n"
            formatted += f"   Düşüş Yüzdesi: {bet.odds_drop_percentage:.2f}%\n"
            formatted += f"   Olasılık Değişimi: {self._calculate_probability_shift(bet.opening_odds, bet.current_odds)}\n"
            formatted += "\n"
        
        formatted += f"{'='*80}\n```\n"
        return formatted
    
    def _calculate_probability_shift(self, opening: float, current: float) -> str:
        """
        Oran değişiminden olasılık değişimini hesapla
        
        Args:
            opening: Açılış oranı
            current: Güncel oran
        
        Returns:
            Olasılık değişimi açıklaması
        """
        if opening <= 0 or current <= 0:
            return "Hesaplanamıyor"
        
        opening_prob = (1 / opening) * 100
        current_prob = (1 / current) * 100
        prob_change = current_prob - opening_prob
        
        return f"{opening_prob:.2f}% → {current_prob:.2f}% ({prob_change:+.2f}%)"
    
    def analyze_value_bets(self, value_bets: List[ValueBet]) -> str:
        """
        OpenAI API'yi kullanarak value bet'leri analiz et
        
        Args:
            value_bets: Analiz edilecek value bet'ler
        
        Returns:
            AI tarafından oluşturulan analiz raporu (Markdown formatı)
        """
        try:
            if not value_bets:
                self.logger.warning("⚠️ Analiz için value bet verisi yok")
                return "## ⚠️ Analiz Yapılamadı\n\nGünümüz için filtrelenmiş value bet bulunmamaktadır."
            
            # Verileri formatlı metin haline getir
            formatted_bets = self.format_value_bets_for_analysis(value_bets)
            
            # System prompt
            system_prompt = """Sen profesyonel bir futbol analisti ve veri odaklı bahis stratejistisin. 
Sana, Python uygulaması tarafından filtrelenmiş ve oranlarında ciddi düşüşler (Value Bet potansiyeli) tespit edilmiş maçların verilerini göndereceğim.

Görevin:
1. Bu oran düşüşlerinin matematiksel olarak ne anlama geldiğini (olasılık değişimini) kısaca açıkla.
2. Ev sahibi veya deplasman takımına yapılan bu aşırı yüklenmenin (drop) arkasındaki olası senaryoları (sakatlık, motivasyon, taktiksel veya finansal durumlar) tahmin et ve yorumla.
3. Bu maçlar arasından en güvenli (Low-Risk Value) ve en yüksek kazanç vadeden (High-Reward) 3 maçı seçerek öne çıkar.

Çıktı Formatı:
Analizini tamamen Türkçe, profesyonel bir dille, başlıklar ve Markdown tabloları kullanarak sun. Kesin kazanç garantisi verme, tamamen veri analitiği odaklı konuş."""
            
            # User prompt
            user_prompt = f"""Lütfen aşağıdaki filtrelenmiş maç verilerini analiz et ve derinlemesine bir rapor hazırla:

{formatted_bets}

Analizi yukarıda belirtilen görev ve format özelliklerine uygun olarak hazırla."""
            
            self.logger.info("🤖 OpenAI API'ye istek gönderiliyor...")
            
            # OpenAI API çağrısı
            response = self.client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                top_p=0.95
            )
            
            analysis = response.choices[0].message.content
            self.logger.info("✅ AI analizi başarıyla tamamlandı")
            
            return analysis
        
        except Exception as e:
            self.logger.error(f"❌ AI analiz sırasında hata: {str(e)}")
            return f"## ❌ Analiz Hatası\n\nAI analizi gerçekleştirilemedi: {str(e)}"

# ============================================================================
# 6. RAPORLAMA SİSTEMİ
# ============================================================================

class ReportGenerator:
    """Raporlar oluşturan ve saklayan sınıf"""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
    
    def generate_report(
        self,
        value_bets: List[ValueBet],
        ai_analysis: str
    ) -> str:
        """
        Tam raporun oluştur
        
        Args:
            value_bets: Analiz edilmiş value bet'ler
            ai_analysis: AI tarafından oluşturulan analiz
        
        Returns:
            Tam rapor metni (Markdown formatı)
        """
        report = f"""# ⚽ GÜNLÜK FUTBOL BAHİS ANALİZ RAPORU

**Raporun Oluşturulduğu Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Özet Bilgiler

- **Toplam Analiz Edilen Maç:** {len(value_bets)}
- **Oran Düşüş Eşiği:** {self.config.ODDS_DROP_THRESHOLD * 100:.0f}%
- **Rapor Türü:** Otomatik AI Analizi + Veri Filtreleme

---

## 🎯 Filtrelenmiş Value Bet'ler

"""
        
        if not value_bets:
            report += "\n> ℹ️ **Bugünü için filtrelenmiş value bet bulunmamaktadır.**\n"
        else:
            report += f"\n| # | Ev Sahibi | Deplasman | Lig | Market | Açılış | Güncel | Düşüş | \n"
            report += f"|---|-----------|-----------|-----|--------|--------|--------|-------|\n"
            
            for i, bet in enumerate(value_bets, 1):
                report += (
                    f"| {i} | {bet.home_team} | {bet.away_team} | "
                    f"{bet.league} | {bet.market_type_name} | "
                    f"{bet.opening_odds:.2f} | {bet.current_odds:.2f} | "
                    f"{bet.odds_drop_percentage:.2f}% |\n"
                )
        
        report += f"""
---

## 🤖 YAPAY ZEKA TARAFINDAN OLUŞTURULAN ANALİZ

{ai_analysis}

---

## ⚠️ DİKKAT

Bu rapor sadece **bilgilendirme ve analiz amaçlı**dur. Bahis yapma kararlarınız için:
- Profesyonel danışmanlarla görüşün
- Kendi risk yönetim stratejinizi geliştirin
- Hiçbir garantisi olmayan bahis işlemlerine katılmakta dikkatli olun

---

*Raporun Oluşturulması: Python Futbol Bahis Analiz Sistemi v1.0*
"""
        
        return report
    
    def save_report(self, report: str) -> bool:
        """
        Raporu dosyaya kaydet
        
        Args:
            report: Kaydedilecek rapor metni
        
        Returns:
            Başarı durumu
        """
        try:
            with open(self.config.REPORT_FILE, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.logger.info(f"✅ Rapor başarıyla kaydedildi: {self.config.REPORT_FILE}")
            return True
        
        except IOError as e:
            self.logger.error(f"❌ Rapor kaydedilirken hata: {str(e)}")
            return False
    
    def display_report(self, report: str) -> None:
        """
        Raporu ekrana yazdır
        
        Args:
            report: Gösterilecek rapor metni
        """
        print("\n" + "="*80)
        print(report)
        print("="*80 + "\n")

# ============================================================================
# 7. ANA ORKESTRASYON MOTORU
# ============================================================================

class BettingAnalysisOrchestrator:
    """Tüm bileşenleri koordine eden ana sınıf"""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        
        # Bileşenleri başlat
        self.data_fetcher = FootballDataFetcher(config, logger)
        self.value_analyzer = ValueBetAnalyzer(config, logger)
        self.ai_engine = AIAnalysisEngine(config, logger)
        self.report_generator = ReportGenerator(config, logger)
    
    def run(self, days_ahead: int = 1) -> bool:
        """
        Ana analiz işlemini çalıştır
        
        Args:
            days_ahead: Kaç gün ileri analiz yapılacağı
        
        Returns:
            Başarı durumu
        """
        try:
            self.logger.info("🚀 FUTBOL BAHİS ANALİZ SİSTEMİ BAŞLATILIYOR")
            print("\n" + "="*80)
            print("⚽ FUTBOL BAHİS ANALİZ SİSTEMİ".center(80))
            print("="*80 + "\n")
            
            # ADIM 1: Verileri çek
            self.logger.info("ADIM 1/4: Futbol maçları çekiliyor...")
            fixtures = self.data_fetcher.get_daily_fixtures(days_ahead=days_ahead)
            
            if not fixtures:
                self.logger.warning("⚠️ Maç verisi çekilemedi")
                return False
            
            # ADIM 2: Value bet'leri filtrele
            self.logger.info("ADIM 2/4: Value bet'ler filtreleniyor...")
            value_bets = self.value_analyzer.filter_value_bets(fixtures)
            
            if not value_bets:
                self.logger.warning("⚠️ Belirlenen eşiği aşan value bet bulunamadı")
            
            # ADIM 3: AI analizi yap
            self.logger.info("ADIM 3/4: Yapay zeka analizi yapılıyor...")
            ai_analysis = self.ai_engine.analyze_value_bets(value_bets)
            
            # ADIM 4: Raporu oluştur ve kaydet
            self.logger.info("ADIM 4/4: Rapor oluşturuluyor...")
            report = self.report_generator.generate_report(value_bets, ai_analysis)
            
            # Raporu göster
            self.report_generator.display_report(report)
            
            # Raporu dosyaya kaydet
            if self.report_generator.save_report(report):
                self.logger.info("✅ Tüm işlemler başarıyla tamamlandı!")
                return True
            else:
                self.logger.error("❌ Rapor kaydedilirken hata oluştu")
                return False
        
        except Exception as e:
            self.logger.error(f"❌ Beklenmeyen hata: {str(e)}", exc_info=True)
            return False

# ============================================================================
# 8. PROGRAM GİRİŞ NOKTASI
# ============================================================================

def main():
    """Ana program fonksiyonu"""
    try:
        # Yapılandırmayı yükle
        config = Config()
        
        # Loglama sistemini konfigure et
        logger = setup_logging(config)
        
        # Sistem bilgilerini göster
        print("\n📋 SİSTEM AYARLARI")
        print(f"  • RapidAPI Host: {config.RAPIDAPI_HOST}")
        print(f"  • OpenAI Model: {config.OPENAI_MODEL}")
        print(f"  • Oran Düşüş Eşiği: {config.ODDS_DROP_THRESHOLD * 100:.0f}%")
        print(f"  • Rapor Dosyası: {config.REPORT_FILE}")
        print(f"  • Log Dosyası: {config.LOG_FILE}\n")
        
        # Ana orkestratörü başlat
        orchestrator = BettingAnalysisOrchestrator(config, logger)
        
        # Analiz işlemini çalıştır
        success = orchestrator.run(days_ahead=1)
        
        if success:
            print("✅ Program başarıyla tamamlandı!")
            sys.exit(0)
        else:
            print("❌ Program bir hata ile sonlandırıldı!")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ KRITIK HATA: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
