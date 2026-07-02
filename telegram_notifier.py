#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 TELEGRAM BOT MODÜLÜ
Telegram Bildirimleri ve Entegrasyonu
"""

import requests
from typing import List, Dict
import logging
from datetime import datetime

class TelegramNotifier:
    """Telegram üzerinden bildirim gönderen sınıf"""
    
    def __init__(self, bot_token: str, chat_id: str, logger: logging.Logger = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.logger = logger
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_value_bets_notification(self, value_bets: List[Dict]) -> bool:
        """Value bet'leri Telegram'a gönder"""
        try:
            if not value_bets:
                return self._send_message("📭 Bugün için value bet bulunmamaktadır.")
            
            message = self._format_value_bets(value_bets)
            return self._send_message(message)
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Telegram bildirim gönderme hatası: {str(e)}")
            return False
    
    def send_alert(self, title: str, content: str, emoji: str = "🚨") -> bool:
        """Acil uyarı gönder"""
        message = f"{emoji} **{title}**\n\n{content}"
        return self._send_message(message)
    
    def _format_value_bets(self, value_bets: List[Dict]) -> str:
        """Value bet'leri Markdown formatında düzenle"""
        message = "⚽ **GÜNLÜK VALUE BET ANALİZİ**\n"
        message += "=" * 50 + "\n\n"
        
        for i, bet in enumerate(value_bets[:10], 1):  # Max 10 maç
            message += f"**{i}. {bet['home_team']} vs {bet['away_team']}**\n"
            message += f"📍 *Lig:* {bet['league']}\n"
            message += f"🎯 *Market:* {bet['market_type_name']}\n"
            message += f"📊 *Oranlar:* {bet['opening_odds']:.2f} → {bet['current_odds']:.2f}\n"
            message += f"📉 *Düşüş:* `{bet['odds_drop_percentage']:.2f}%`\n"
            message += f"🕐 *Tarih:* {bet['match_date']}\n\n"
        
        if len(value_bets) > 10:
            message += f"... ve {len(value_bets) - 10} maç daha\n"
        
        return message
    
    def _send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Telegram'a mesaj gönder"""
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                if self.logger:
                    self.logger.info("✅ Telegram mesajı başarıyla gönderildi")
                return True
            else:
                if self.logger:
                    self.logger.warning(f"⚠️ Telegram gönderimi başarısız: {response.status_code}")
                return False
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Telegram gönderimi hatası: {str(e)}")
            return False
