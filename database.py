#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💾 VERITABANI MODÜLÜ
SQLite/PostgreSQL Entegrasyonu
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import asdict
import logging

class BettingDatabase:
    """Bahis verilerini saklayan veritabanı sınıfı"""
    
    def __init__(self, db_path: str = "betting_data.db", logger: logging.Logger = None):
        self.db_path = db_path
        self.logger = logger
        self.init_database()
    
    def init_database(self):
        """Veritabanı tablolarını oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Value Bet'ler tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS value_bets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    league TEXT NOT NULL,
                    match_date TEXT NOT NULL,
                    market_type TEXT NOT NULL,
                    opening_odds REAL NOT NULL,
                    current_odds REAL NOT NULL,
                    odds_drop_percentage REAL NOT NULL,
                    market_type_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Maç Sonuçları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS match_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL UNIQUE,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    final_score TEXT,
                    result_status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Telegram Notifikasyonları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS telegram_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    message TEXT,
                    status TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # İstatistikler tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    total_matches_analyzed INTEGER,
                    value_bets_found INTEGER,
                    ai_analysis_success BOOLEAN,
                    data JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            if self.logger:
                self.logger.info("✅ Veritabanı başarıyla başlatıldı")
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Veritabanı başlatma hatası: {str(e)}")
    
    def save_value_bet(self, value_bet: Dict) -> bool:
        """Value bet'i veritabanına kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO value_bets 
                (match_id, home_team, away_team, league, match_date, market_type, 
                 opening_odds, current_odds, odds_drop_percentage, market_type_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                value_bet['match_id'],
                value_bet['home_team'],
                value_bet['away_team'],
                value_bet['league'],
                value_bet['match_date'],
                value_bet['market_type'],
                value_bet['opening_odds'],
                value_bet['current_odds'],
                value_bet['odds_drop_percentage'],
                value_bet['market_type_name']
            ))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Value bet kaydetme hatası: {str(e)}")
            return False
    
    def get_today_value_bets(self) -> List[Dict]:
        """Bugünün value bet'lerini getir"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("""
                SELECT * FROM value_bets 
                WHERE DATE(match_date) = ?
                ORDER BY created_at DESC
            """, (today,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Bugünün value bet'leri çekilirken hata: {str(e)}")
            return []
    
    def get_statistics(self, days: int = 7) -> Dict:
        """Son N gün istatistiklerini getir"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_bets,
                    AVG(odds_drop_percentage) as avg_drop,
                    MAX(odds_drop_percentage) as max_drop,
                    MIN(odds_drop_percentage) as min_drop
                FROM value_bets
                WHERE created_at > datetime('now', '-' || ? || ' days')
            """, (days,))
            
            stats = dict(cursor.fetchone())
            conn.close()
            
            return stats
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ İstatistik çekimi hatası: {str(e)}")
            return {}
    
    def save_telegram_log(self, user_id: str, message: str, status: str) -> bool:
        """Telegram log'u kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO telegram_logs (user_id, message, status)
                VALUES (?, ?, ?)
            """, (user_id, message, status))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Telegram log kaydetme hatası: {str(e)}")
            return False
