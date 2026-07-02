#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 WEB DASHBOARD API
Flask REST API ve Web Interface
"""

from flask import Flask, jsonify, request
from datetime import datetime
import json
import logging
from typing import Dict

class DashboardAPI:
    """Web Dashboard API sınıfı"""
    
    def __init__(self, database, analytics, port: int = 5000):
        self.app = Flask(__name__)
        self.db = database
        self.analytics = analytics
        self.port = port
        self.logger = logging.getLogger("DashboardAPI")
        
        self._setup_routes()
    
    def _setup_routes(self):
        """API rotalarını konfigure et"""
        
        @self.app.route('/api/health', methods=['GET'])
        def health():
            return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})
        
        @self.app.route('/api/today-bets', methods=['GET'])
        def get_today_bets():
            """Bugünün value bet'lerini getir"""
            try:
                bets = self.db.get_today_value_bets()
                return jsonify({
                    "success": True,
                    "count": len(bets),
                    "data": bets
                })
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/api/statistics', methods=['GET'])
        def get_statistics():
            """İstatistikleri getir"""
            try:
                days = request.args.get('days', 7, type=int)
                stats = self.db.get_statistics(days=days)
                return jsonify({"success": True, "data": stats})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/api/trend-analysis', methods=['GET'])
        def trend_analysis():
            """Trend analizi getir"""
            try:
                analysis = self.analytics.get_historical_statistics(days=30)
                return jsonify({"success": True, "data": analysis})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/api/dashboard', methods=['GET'])
        def dashboard():
            """Ana dashboard verilerini getir"""
            try:
                bets = self.db.get_today_value_bets()
                stats = self.db.get_statistics(days=7)
                
                dashboard_data = {
                    "today": {
                        "bets": bets,
                        "count": len(bets)
                    },
                    "statistics": stats,
                    "timestamp": datetime.now().isoformat()
                }
                
                return jsonify({"success": True, "data": dashboard_data})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
    
    def run(self, debug: bool = False):
        """Dashboard API'yi çalıştır"""
        self.logger.info(f"🚀 Dashboard API başlıyor: http://localhost:{self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=debug)
    
    def get_app(self):
        """Flask uygulamasını getir"""
        return self.app
