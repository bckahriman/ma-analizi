#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 CANLI ORAN İZLEME MODÜLÜ
Reel-time Oran Değişimlerini İzle
"""

import threading
import time
from typing import Dict, List, Callable
from datetime import datetime
import logging

class LiveOddsMonitor:
    """Canlı oranları izleyen sınıf"""
    
    def __init__(self, update_interval: int = 60, logger: logging.Logger = None):
        """
        Args:
            update_interval: Güncelleme süresi (saniye)
            logger: Logger nesnesi
        """
        self.update_interval = update_interval
        self.logger = logger
        self.is_running = False
        self.monitor_thread = None
        self.odds_cache = {}
        self.callbacks = []
    
    def start_monitoring(self, data_fetcher, value_analyzer):
        """Canlı izlemeyi başlat"""
        if self.is_running:
            if self.logger:
                self.logger.warning("⚠️ İzleme zaten çalışıyor")
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(data_fetcher, value_analyzer),
            daemon=True
        )
        self.monitor_thread.start()
        
        if self.logger:
            self.logger.info("✅ Canlı oran izlemesi başladı")
    
    def stop_monitoring(self):
        """Canlı izlemeyi durdur"""
        self.is_running = False
        
        if self.logger:
            self.logger.info("⏹️ Canlı oran izlemesi durduruldu")
    
    def add_callback(self, callback: Callable):
        """Callback fonksiyonu ekle (yeni value bet bulunduğunda çağrılır)"""
        self.callbacks.append(callback)
    
    def _monitor_loop(self, data_fetcher, value_analyzer):
        """Ana izleme döngüsü"""
        while self.is_running:
            try:
                # Günlük maçları çek
                fixtures = data_fetcher.get_daily_fixtures(days_ahead=0)  # Bugünün maçları
                
                # Value bet'leri filtrele
                current_bets = value_analyzer.filter_value_bets(fixtures)
                
                # Yeni value bet'leri bul
                new_bets = self._detect_new_bets(current_bets)
                
                if new_bets:
                    if self.logger:
                        self.logger.info(f"🔥 {len(new_bets)} yeni value bet bulundu!")
                    
                    # Callback'leri çağır
                    for callback in self.callbacks:
                        callback(new_bets)
                
                # Cache'i güncelle
                self.odds_cache = {bet['match_id']: bet for bet in current_bets}
                
                # Bekleme
                time.sleep(self.update_interval)
            
            except Exception as e:
                if self.logger:
                    self.logger.error(f"❌ İzleme döngüsü hatası: {str(e)}")
                time.sleep(self.update_interval)
    
    def _detect_new_bets(self, current_bets: List[Dict]) -> List[Dict]:
        """Yeni value bet'leri tespit et"""
        new_bets = []
        
        for bet in current_bets:
            match_id = bet.get('match_id')
            
            if match_id not in self.odds_cache:
                new_bets.append(bet)
        
        return new_bets
    
    def get_odds_changes(self) -> Dict:
        """Oran değişimlerini getir"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_monitored": len(self.odds_cache),
            "cache": self.odds_cache
        }
