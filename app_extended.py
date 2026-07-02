#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ANA UYGULAMA - GENİŞLETİLMİŞ VERSİYON
Canlı İzleme, Veritabanı, Web Dashboard, Telegram ve Analitik
"""

import os
import sys
import threading
from datetime import datetime
from typing import Dict, List
import logging

# Yerel modülleri içe aktar
from main import (
    Config, setup_logging, FootballDataFetcher, ValueBetAnalyzer,
    AIAnalysisEngine, ReportGenerator, BettingAnalysisOrchestrator
)
from database import BettingDatabase
from telegram_notifier import TelegramNotifier
from live_odds_monitor import LiveOddsMonitor
from analytics import AnalyticsEngine
from dashboard_api import DashboardAPI

class ExtendedBettingSystem:
    """Tüm özellikleri içeren genişletilmiş bahis sistemi"""
    
    def __init__(self):
        self.config = Config()
        self.logger = setup_logging(self.config)
        
        # Bileşenleri başlat
        self.data_fetcher = FootballDataFetcher(self.config, self.logger)
        self.value_analyzer = ValueBetAnalyzer(self.config, self.logger)
        self.ai_engine = AIAnalysisEngine(self.config, self.logger)
        self.report_generator = ReportGenerator(self.config, self.logger)
        
        # Veritabanı
        self.database = BettingDatabase(logger=self.logger)
        
        # Telegram (İsteğe bağlı)
        self.telegram_bot = None
        if os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
            self.telegram_bot = TelegramNotifier(
                bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
                chat_id=os.getenv("TELEGRAM_CHAT_ID"),
                logger=self.logger
            )
            self.logger.info("✅ Telegram Bot bağlandı")
        
        # Canlı İzleme
        self.live_monitor = LiveOddsMonitor(update_interval=60, logger=self.logger)
        self.live_monitor.add_callback(self._on_new_value_bets)
        
        # Analitik
        self.analytics = AnalyticsEngine(self.database, self.logger)
        
        # Web Dashboard
        self.dashboard = DashboardAPI(self.database, self.analytics, port=5000)
    
    def run_full_analysis(self):
        """Tam analiz çalıştır"""
        try:
            self.logger.info("🚀 GENİŞLETİLMİŞ FUTBOL BAHİS ANALİZ SİSTEMİ BAŞLATILIYOR")
            print("\n" + "="*80)
            print("⚽ GENİŞLETİLMİŞ FUTBOL BAHİS ANALİZ SİSTEMİ".center(80))
            print("Özellikler: Canlı İzleme | Veritabanı | Web API | Telegram | Analitik".center(80))
            print("="*80 + "\n")
            
            # 1. Ana Analiz Çalıştır
            print("[1/4] Ana Analiz Çalıştırılıyor...\n")
            orchestrator = BettingAnalysisOrchestrator(self.config, self.logger)
            
            fixtures = self.data_fetcher.get_daily_fixtures(days_ahead=1)
            value_bets = self.value_analyzer.filter_value_bets(fixtures)
            
            # 2. Veritabanına Kaydet
            print("[2/4] Veriler Veritabanına Kaydediliyor...\n")
            for bet in value_bets:
                self.database.save_value_bet(bet.to_dict())
            
            # 3. Telegram Bildirimi Gönder
            if self.telegram_bot and value_bets:
                print("[3/4] Telegram Bildirimi Gönderiliyor...\n")
                self.telegram_bot.send_value_bets_notification(
                    [bet.to_dict() for bet in value_bets]
                )
            
            # 4. AI Analizi Yap ve Raporla
            print("[4/4] AI Analizi Yapılıyor...\n")
            ai_analysis = self.ai_engine.analyze_value_bets(value_bets)
            report = self.report_generator.generate_report(value_bets, ai_analysis)
            self.report_generator.display_report(report)
            self.report_generator.save_report(report)
            
            self.logger.info("✅ Tam analiz başarıyla tamamlandı!")
            
        except Exception as e:
            self.logger.error(f"❌ Analiz hatası: {str(e)}", exc_info=True)
    
    def start_live_monitoring(self):
        """Canlı izlemeyi başlat"""
        self.live_monitor.start_monitoring(self.data_fetcher, self.value_analyzer)
    
    def start_dashboard(self):
        """Web Dashboard'u başlat"""
        dashboard_thread = threading.Thread(
            target=lambda: self.dashboard.run(debug=False),
            daemon=True
        )
        dashboard_thread.start()
        self.logger.info("✅ Web Dashboard başladı: http://localhost:5000")
    
    def _on_new_value_bets(self, new_bets: List[Dict]):
        """Yeni value bet'ler bulunduğunda çağrılır"""
        try:
            # Veritabanına kaydet
            for bet in new_bets:
                self.database.save_value_bet(bet)
            
            # Telegram bildirimi
            if self.telegram_bot:
                self.telegram_bot.send_alert(
                    title="Yeni Value Bet'ler Bulundu!",
                    content=f"{len(new_bets)} yeni value bet analiz edildi."
                )
            
            self.logger.info(f"🔥 {len(new_bets)} yeni value bet bulundu ve kaydedildi")
        
        except Exception as e:
            self.logger.error(f"❌ Yeni bet işleme hatası: {str(e)}")
    
    def get_statistics_report(self):
        """İstatistik raporu getir"""
        return self.analytics.generate_trend_report()

def main():
    """Ana program"""
    try:
        system = ExtendedBettingSystem()
        
        print("\n📋 SİSTEM SEÇENEKLERİ:")
        print("1. Tam Analiz Çalıştır")
        print("2. Canlı İzlemeyi Başlat")
        print("3. Web Dashboard'u Aç")
        print("4. İstatistik Raporu")
        print("5. Hepsini Çalıştır\n")
        
        choice = input("Seçeneği girin (1-5): ").strip()
        
        if choice == "1":
            system.run_full_analysis()
        
        elif choice == "2":
            system.start_live_monitoring()
            print("\n✅ Canlı İzleme Aktif (Durdurmak için Ctrl+C)")
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                system.live_monitor.stop_monitoring()
        
        elif choice == "3":
            system.start_dashboard()
            print("\n✅ Dashboard Açıldı: http://localhost:5000")
            print("(Durdurmak için Ctrl+C)")
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Dashboard kapatılıyor...")
        
        elif choice == "4":
            report = system.get_statistics_report()
            print(report)
        
        elif choice == "5":
            system.run_full_analysis()
            system.start_live_monitoring()
            system.start_dashboard()
            print("\n✅ Tüm Sistemler Aktif")
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Sistem kapatılıyor...")
                system.live_monitor.stop_monitoring()
        
        else:
            print("❌ Geçersiz seçenek")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ KRITIK HATA: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
