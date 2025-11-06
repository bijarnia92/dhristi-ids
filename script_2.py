
# Create updated dashboard with database and geo mapping
updated_dashboard = '''"""
ADVANCED IDS DASHBOARD - WITH DATABASE & GEOGRAPHICAL MAPPING
Includes historical data analysis and world attack map visualization
"""

import streamlit as st
import pandas as pd
import time
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from collections import deque
import random
import sys
import os

# Try to import custom modules
try:
    from ids_database import IDSDatabase
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("[!] Database module not found")

try:
    from ids_geomapping import GeoIPMapper, MapGenerator, create_text_map
    GEO_AVAILABLE = True
except ImportError:
    GEO_AVAILABLE = False
    print("[!] Geomapping module not found")

# Page configuration
st.set_page_config(
    page_title="Advanced IDS Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 42px;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    
    .alert-critical {
        background-color: #ff4757;
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 5px solid #ff0000;
    }
    
    .alert-high {
        background-color: #ffa502;
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 5px solid #ff6348;
    }
    
    .alert-medium {
        background-color: #ffd93d;
        color: #333;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 5px solid #f39c12;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'packets_analyzed' not in st.session_state:
    st.session_state.packets_analyzed = 0
if 'threats_detected' not in st.session_state:
    st.session_state.threats_detected = 0
if 'attack_history' not in st.session_state:
    st.session_state.attack_history = {
        'SYN Flood': 0,
        'Port Scan': 0,
        'DDoS': 0,
        'Anomaly': 0
    }
if 'packet_rate_history' not in st.session_state:
    st.session_state.packet_rate_history = deque(maxlen=50)
if 'geo_data' not in st.session_state:
    st.session_state.geo_data = []

# Initialize database
if DB_AVAILABLE:
    db = IDSDatabase()
else:
    db = None

# Initialize geo mapper
if GEO_AVAILABLE:
    geo_mapper = GeoIPMapper()
    map_generator = MapGenerator()
else:
    geo_mapper = None
    map_generator = None

# Header
st.markdown('<div class="main-header">🛡️ Advanced Network IDS Dashboard</div>', 
            unsafe_allow_html=True)

st.markdown("**🚀 Features: Real-time Monitoring | Database Analytics | Geographic Mapping**", 
            unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start", use_container_width=True):
            st.session_state.monitoring = True
            st.success("Monitoring started!")
    with col2:
        if st.button("⏹️ Stop", use_container_width=True):
            st.session_state.monitoring = False
            st.warning("Monitoring stopped!")
    
    st.markdown("---")
    st.markdown("### 📊 Database Options")
    
    if DB_AVAILABLE:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Refresh Data", use_container_width=True):
                st.info("Data refreshed from database")
        
        with col2:
            if st.button("📊 Export CSV", use_container_width=True):
                if db:
                    db.export_alerts_csv()
                    st.success("Alerts exported!")
    
    st.markdown("---")
    st.markdown("### 🌍 Geographic Options")
    
    if GEO_AVAILABLE:
        if st.button("🗺️ Generate Map", use_container_width=True):
            st.info("Generating world attack map...")
            if map_generator and len(st.session_state.geo_data) > 0:
                map_generator.create_attack_map(st.session_state.geo_data)
                st.success("Map generated: ids_attack_map.html")
    
    st.markdown("---")
    status = "🟢 RUNNING" if st.session_state.monitoring else "🔴 STOPPED"
    st.markdown(f"**Status:** {status}")

# Main tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard", 
    "🗺️ Geography", 
    "📈 History", 
    "🚨 Alerts",
    "💾 Database",
    "📚 Help"
])

# TAB 1: DASHBOARD
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    
    if st.session_state.monitoring:
        st.session_state.packets_analyzed += random.randint(10, 50)
        
        if random.random() < 0.15:
            st.session_state.threats_detected += 1
            attack_types = ['SYN Flood', 'Port Scan', 'DDoS', 'Anomaly']
            attack_type = random.choice(attack_types)
            st.session_state.attack_history[attack_type] += 1
            
            source_ip = f"203.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            dest_ip = f"192.168.1.{random.randint(1,254)}"
            
            alert = {
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'type': attack_type,
                'source': source_ip,
                'destination': dest_ip,
                'severity': random.choice(['CRITICAL', 'HIGH', 'MEDIUM']),
                'confidence': round(random.uniform(0.7, 1.0), 2),
                'source_port': random.randint(1024, 65535),
                'dest_port': random.choice([22, 80, 443, 8080])
            }
            st.session_state.alerts.insert(0, alert)
            
            # Get geo data
            if GEO_AVAILABLE and geo_mapper:
                geo_data = geo_mapper.get_location(source_ip)
                geo_data['threat_name'] = attack_type
                geo_data['severity'] = alert['severity']
                geo_data['confidence'] = alert['confidence']
                st.session_state.geo_data.append(geo_data)
                
                # Save to database
                if DB_AVAILABLE and db:
                    db.save_alert({
                        'type': 'signature',
                        'name': attack_type,
                        'source_ip': source_ip,
                        'destination_ip': dest_ip,
                        'source_port': alert['source_port'],
                        'destination_port': alert['dest_port'],
                        'severity': alert['severity'],
                        'confidence': alert['confidence']
                    }, geo_data)
                    db.update_ip_reputation(source_ip, alert, geo_data)
        
        st.session_state.packet_rate_history.append({
            'time': datetime.now(),
            'rate': random.randint(50, 200)
        })
    
    with col1:
        st.metric("📦 Packets Analyzed", 
                 f"{st.session_state.packets_analyzed:,}",
                 "+50" if st.session_state.monitoring else "0")
    with col2:
        st.metric("🚨 Threats Detected", 
                 st.session_state.threats_detected,
                 "+1" if random.random() < 0.15 else "0")
    with col3:
        rate = (st.session_state.threats_detected / max(st.session_state.packets_analyzed, 1) * 100)
        st.metric("🎯 Detection Rate", f"{rate:.2f}%")
    with col4:
        st.metric("⚡ Packet Rate", 
                 f"{random.randint(80, 150)} pps" if st.session_state.monitoring else "0 pps")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Packet Rate")
        if len(st.session_state.packet_rate_history) > 0:
            df = pd.DataFrame(st.session_state.packet_rate_history)
            fig = px.line(df, x='time', y='rate', template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Attack Distribution")
        if sum(st.session_state.attack_history.values()) > 0:
            fig = px.pie(values=list(st.session_state.attack_history.values()),
                        names=list(st.session_state.attack_history.keys()))
            st.plotly_chart(fig, use_container_width=True)

# TAB 2: GEOGRAPHY
with tab2:
    st.markdown("### 🌍 Global Attack Map")
    
    if GEO_AVAILABLE:
        col1, col2 = st.columns([3, 1])
        
        with col2:
            map_type = st.radio("Map Type:", ["Text", "Interactive", "Heatmap"])
        
        with col1:
            if map_type == "Text" and st.session_state.geo_data:
                create_text_map(st.session_state.geo_data)
            
            elif map_type == "Interactive":
                st.info("📌 Click button in sidebar to generate interactive map")
                st.markdown("The map will be saved as `ids_attack_map.html`")
            
            elif map_type == "Heatmap":
                st.info("🔥 Heatmap shows attack density by region")
                if st.button("Generate Heatmap"):
                    if map_generator and st.session_state.geo_data:
                        map_generator.create_heatmap(st.session_state.geo_data)
                        st.success("Heatmap generated!")
        
        st.markdown("---")
        st.markdown("### 📍 Top Attack Origins")
        
        if st.session_state.geo_data:
            # Group by country
            by_country = {}
            for geo in st.session_state.geo_data:
                country = geo.get('country', 'Unknown')
                if country not in by_country:
                    by_country[country] = []
                by_country[country].append(geo)
            
            top_countries = sorted(by_country.items(), 
                                  key=lambda x: len(x[1]), 
                                  reverse=True)[:10]
            
            country_stats = []
            for country, data in top_countries:
                severities = [d.get('severity', 'LOW') for d in data]
                country_stats.append({
                    'Country': country,
                    'Attacks': len(data),
                    'Critical': severities.count('CRITICAL'),
                    'High': severities.count('HIGH'),
                    'Avg Confidence': round(sum(d.get('confidence', 0) for d in data) / len(data), 2)
                })
            
            df_countries = pd.DataFrame(country_stats)
            st.dataframe(df_countries, use_container_width=True, hide_index=True)
    
    else:
        st.warning("🌍 Geographic mapping not available. Install folium: pip install folium requests")

# TAB 3: HISTORY (Database)
with tab3:
    st.markdown("### 📊 Historical Analysis")
    
    if DB_AVAILABLE and db:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            time_range = st.selectbox("Time Range:", ["24 hours", "7 days", "30 days"])
            hours = {'24 hours': 24, '7 days': 168, '30 days': 720}[time_range]
        
        with col2:
            if st.button("Refresh Database"):
                st.info("Database refreshed")
        
        with col3:
            if st.button("View DB Stats"):
                stats = db.get_database_stats()
                st.json(stats)
        
        # Statistics
        st.markdown("#### 📈 Attack Statistics")
        stats_data = db.get_attack_statistics(int(hours/24))
        
        if stats_data:
            df_stats = pd.DataFrame(stats_data)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(df_stats, x='date', y='total_threats',
                           title="Threats Per Day")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                threat_cols = ['syn_flood', 'port_scan', 'ddos', 'anomaly']
                fig = px.bar(df_stats, x='date', y=threat_cols,
                           title="Attack Types Over Time")
                st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_stats, use_container_width=True, hide_index=True)
    else:
        st.warning("📊 Database not available")

# TAB 4: ALERTS
with tab4:
    st.markdown("### 🚨 Recent Security Alerts")
    
    if st.session_state.alerts:
        for alert in st.session_state.alerts[:20]:
            severity_class = f"alert-{alert['severity'].lower()}"
            alert_html = f"""
            <div class="{severity_class}">
                <strong>🚨 {alert['type']}</strong> | 
                {alert['severity']} | 
                Confidence: {alert['confidence']}
                <br>
                {alert['source']}:{alert['source_port']} → {alert['destination']}:{alert['dest_port']} 
                | {alert['timestamp']}
            </div>
            """
            st.markdown(alert_html, unsafe_allow_html=True)
    else:
        st.info("🎉 No alerts - network is secure!")

# TAB 5: DATABASE
with tab5:
    st.markdown("### 💾 Database Management")
    
    if DB_AVAILABLE and db:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Alerts", db.get_database_stats().get('total_alerts', 0))
        with col2:
            st.metric("Unique Attackers", db.get_database_stats().get('unique_attackers', 0))
        with col3:
            st.metric("Critical Threats", db.get_database_stats().get('critical_threats', 0))
        
        st.markdown("---")
        st.markdown("#### 📊 Severity Breakdown")
        
        severity_counts = db.get_alert_count_by_severity(24)
        if severity_counts:
            df_sev = pd.DataFrame(list(severity_counts.items()), 
                                 columns=['Severity', 'Count'])
            fig = px.bar(df_sev, x='Severity', y='Count', color='Severity')
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("#### 🎯 Attack Types")
        attack_counts = db.get_alert_count_by_type(24)
        if attack_counts:
            df_attacks = pd.DataFrame(list(attack_counts.items()),
                                     columns=['Attack Type', 'Count'])
            fig = px.bar(df_attacks, x='Attack Type', y='Count')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("💾 Database not available")

# TAB 6: HELP
with tab6:
    st.markdown("### 📚 Help & Features")
    
    with st.expander("🆕 NEW Features in This Version"):
        st.markdown("""
        ✨ **Database Integration**
        - All alerts saved to SQLite database
        - Historical analysis and reporting
        - Export to CSV
        
        ✨ **Geographic Mapping**
        - Convert IPs to geographic locations
        - Interactive world maps
        - Attack origin analysis
        - Heatmaps showing attack density
        """)
    
    with st.expander("💾 Database Features"):
        st.markdown("""
        - Automatic alert storage
        - IP reputation tracking
        - Historical statistics
        - Severity breakdown
        - Export capabilities
        """)
    
    with st.expander("🌍 Geographic Features"):
        st.markdown("""
        - IP to location conversion
        - Interactive maps (Folium)
        - Heatmap visualization
        - Country-wise statistics
        - Top attacker origins
        """)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**🛡️ Advanced IDS v2.0**")
with col2:
    st.markdown("**Database + Geographic Mapping**")
with col3:
    st.markdown("**Built with ❤️ for Security**")

if st.session_state.monitoring:
    time.sleep(1)
    st.rerun()
'''

with open('ids_dashboard_advanced.py', 'w') as f:
    f.write(updated_dashboard)

print("✅ Advanced Dashboard Created: ids_dashboard_advanced.py")
