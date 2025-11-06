"""
IDS Database Module
Handles all database operations - storing alerts, retrieving history, analytics
Uses SQLite for easy deployment without external database servers
"""

import sqlite3
import json
from datetime import datetime, timedelta
import os

class IDSDatabase:
    """
    SQLite database handler for IDS alerts and historical data
    Automatically creates database schema on first run
    """

    def __init__(self, db_name="ids_alerts.db"):
        self.db_name = db_name
        self.connection = None
        self.initialize_database()

    def initialize_database(self):
        """Create database and tables if they don't exist"""
        try:
            self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()

            # Create alerts table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                threat_type TEXT NOT NULL,
                threat_name TEXT NOT NULL,
                source_ip TEXT NOT NULL,
                destination_ip TEXT NOT NULL,
                source_port INTEGER,
                destination_port INTEGER,
                severity TEXT,
                confidence REAL,
                country TEXT,
                city TEXT,
                latitude REAL,
                longitude REAL,
                details TEXT
            )
            """)

            # Create statistics table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE DEFAULT CURRENT_DATE,
                total_packets INTEGER DEFAULT 0,
                total_threats INTEGER DEFAULT 0,
                syn_flood_count INTEGER DEFAULT 0,
                port_scan_count INTEGER DEFAULT 0,
                ddos_count INTEGER DEFAULT 0,
                anomaly_count INTEGER DEFAULT 0,
                avg_packet_rate REAL DEFAULT 0,
                avg_confidence REAL DEFAULT 0
            )
            """)

            # Create IP reputation table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ip_reputation (
                ip_address TEXT PRIMARY KEY,
                threat_count INTEGER DEFAULT 0,
                first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                severity_level TEXT DEFAULT 'LOW',
                country TEXT,
                city TEXT,
                latitude REAL,
                longitude REAL
            )
            """)

            self.connection.commit()
            print("[✓] Database initialized successfully")

        except Exception as e:
            print(f"[!] Database initialization error: {e}")

    def save_alert(self, alert_data, geo_data=None):
        """Save alert to database"""
        try:
            cursor = self.connection.cursor()

            geo_data = geo_data or {}

            cursor.execute("""
            INSERT INTO alerts 
            (threat_type, threat_name, source_ip, destination_ip, source_port, 
             destination_port, severity, confidence, country, city, latitude, longitude, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert_data.get('type'),
                alert_data.get('name'),
                alert_data.get('source_ip'),
                alert_data.get('destination_ip'),
                alert_data.get('source_port'),
                alert_data.get('destination_port'),
                alert_data.get('severity'),
                alert_data.get('confidence', 0.0),
                geo_data.get('country', 'Unknown'),
                geo_data.get('city', 'Unknown'),
                geo_data.get('latitude'),
                geo_data.get('longitude'),
                json.dumps(alert_data)
            ))

            self.connection.commit()
            return True

        except Exception as e:
            print(f"[!] Error saving alert: {e}")
            return False

    def update_ip_reputation(self, ip_address, threat_info, geo_data=None):
        """Update or create IP reputation record"""
        try:
            cursor = self.connection.cursor()
            geo_data = geo_data or {}

            # Check if IP exists
            cursor.execute("SELECT * FROM ip_reputation WHERE ip_address = ?", (ip_address,))
            existing = cursor.fetchone()

            if existing:
                # Update existing record
                cursor.execute("""
                UPDATE ip_reputation 
                SET threat_count = threat_count + 1,
                    last_seen = CURRENT_TIMESTAMP,
                    severity_level = ?
                WHERE ip_address = ?
                """, (threat_info.get('severity', 'LOW'), ip_address))
            else:
                # Create new record
                cursor.execute("""
                INSERT INTO ip_reputation 
                (ip_address, threat_count, severity_level, country, city, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    ip_address,
                    1,
                    threat_info.get('severity', 'LOW'),
                    geo_data.get('country', 'Unknown'),
                    geo_data.get('city', 'Unknown'),
                    geo_data.get('latitude'),
                    geo_data.get('longitude')
                ))

            self.connection.commit()
            return True

        except Exception as e:
            print(f"[!] Error updating IP reputation: {e}")
            return False

    def get_alerts_by_timeframe(self, hours=24):
        """Get alerts from last N hours"""
        try:
            cursor = self.connection.cursor()
            time_threshold = datetime.now() - timedelta(hours=hours)

            cursor.execute("""
            SELECT * FROM alerts 
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            """, (time_threshold,))

            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            print(f"[!] Error fetching alerts: {e}")
            return []

    def get_top_attacker_ips(self, limit=10):
        """Get most active attacker IPs"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
            SELECT source_ip, country, city, latitude, longitude, COUNT(*) as attack_count,
                   MAX(severity) as max_severity
            FROM alerts
            GROUP BY source_ip
            ORDER BY attack_count DESC
            LIMIT ?
            """, (limit,))

            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            print(f"[!] Error fetching attacker IPs: {e}")
            return []

    def get_attack_statistics(self, days=7):
        """Get attack statistics for past N days"""
        try:
            cursor = self.connection.cursor()

            cursor.execute("""
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as total_threats,
                COUNT(CASE WHEN threat_name = 'SYN Flood Attack' THEN 1 END) as syn_flood,
                COUNT(CASE WHEN threat_name = 'Port Scanning' THEN 1 END) as port_scan,
                COUNT(CASE WHEN threat_name = 'DDoS Attack' THEN 1 END) as ddos,
                COUNT(CASE WHEN threat_type = 'anomaly' THEN 1 END) as anomaly,
                AVG(confidence) as avg_confidence,
                MAX(severity) as max_severity
            FROM alerts
            WHERE timestamp > datetime('now', '-' || ? || ' days')
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            """, (days,))

            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            print(f"[!] Error fetching statistics: {e}")
            return []

    def get_alert_count_by_severity(self, hours=24):
        """Get count of alerts by severity"""
        try:
            cursor = self.connection.cursor()
            time_threshold = datetime.now() - timedelta(hours=hours)

            cursor.execute("""
            SELECT severity, COUNT(*) as count
            FROM alerts
            WHERE timestamp > ?
            GROUP BY severity
            """, (time_threshold,))

            return {dict(row)['severity']: dict(row)['count'] for row in cursor.fetchall()}

        except Exception as e:
            print(f"[!] Error fetching severity counts: {e}")
            return {}

    def get_alert_count_by_type(self, hours=24):
        """Get count of alerts by attack type"""
        try:
            cursor = self.connection.cursor()
            time_threshold = datetime.now() - timedelta(hours=hours)

            cursor.execute("""
            SELECT threat_name, COUNT(*) as count
            FROM alerts
            WHERE timestamp > ?
            GROUP BY threat_name
            ORDER BY count DESC
            """, (time_threshold,))

            return {dict(row)['threat_name']: dict(row)['count'] for row in cursor.fetchall()}

        except Exception as e:
            print(f"[!] Error fetching type counts: {e}")
            return {}

    def get_geographic_heatmap_data(self, hours=24):
        """Get geographic data for heatmap visualization"""
        try:
            cursor = self.connection.cursor()
            time_threshold = datetime.now() - timedelta(hours=hours)

            cursor.execute("""
            SELECT 
                country, city, latitude, longitude,
                COUNT(*) as attack_count,
                MAX(severity) as max_severity,
                AVG(confidence) as avg_confidence
            FROM alerts
            WHERE timestamp > ? AND latitude IS NOT NULL AND longitude IS NOT NULL
            GROUP BY country, city, latitude, longitude
            ORDER BY attack_count DESC
            """, (time_threshold,))

            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            print(f"[!] Error fetching heatmap data: {e}")
            return []

    def export_alerts_csv(self, filename="ids_alerts_export.csv", hours=24):
        """Export alerts to CSV file"""
        try:
            import csv

            alerts = self.get_alerts_by_timeframe(hours)

            if not alerts:
                print("[!] No alerts to export")
                return False

            with open(filename, 'w', newline='') as csvfile:
                fieldnames = list(alerts[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                writer.writerows(alerts)

            print(f"[✓] Alerts exported to {filename}")
            return True

        except Exception as e:
            print(f"[!] Error exporting CSV: {e}")
            return False

    def get_database_stats(self):
        """Get overall database statistics"""
        try:
            cursor = self.connection.cursor()

            stats = {}

            # Total alerts
            cursor.execute("SELECT COUNT(*) as count FROM alerts")
            stats['total_alerts'] = cursor.fetchone()['count']

            # Total unique source IPs
            cursor.execute("SELECT COUNT(DISTINCT source_ip) as count FROM alerts")
            stats['unique_attackers'] = cursor.fetchone()['count']

            # Critical threats
            cursor.execute("SELECT COUNT(*) as count FROM alerts WHERE severity = 'CRITICAL'")
            stats['critical_threats'] = cursor.fetchone()['count']

            # High severity threats
            cursor.execute("SELECT COUNT(*) as count FROM alerts WHERE severity = 'HIGH'")
            stats['high_threats'] = cursor.fetchone()['count']

            return stats

        except Exception as e:
            print(f"[!] Error getting database stats: {e}")
            return {}

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("[✓] Database connection closed")
