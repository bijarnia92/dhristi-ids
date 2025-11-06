"""
Network Intrusion Detection System (IDS)
Built with Machine Learning and Signature-based Detection
Author: AI-Powered IDS Framework
Date: October 2025
"""

from scapy.all import sniff, IP, TCP, UDP
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from collections import defaultdict
import threading
import queue
import logging
import json
import numpy as np
from datetime import datetime
import time

# ==================== PACKET CAPTURE ENGINE ====================
class PacketCapture:
    """
    Captures network packets from specified interface using Scapy.
    Uses threading and queues for efficient real-time processing.
    """
    def __init__(self):
        self.packet_queue = queue.Queue()
        self.stop_capture = threading.Event()
        self.capture_thread = None
        
    def packet_callback(self, packet):
        """Filter and queue packets with IP and TCP/UDP layers"""
        if IP in packet and (TCP in packet or UDP in packet):
            self.packet_queue.put(packet)
    
    def start_capture(self, interface="eth0"):
        """Start packet capture on specified network interface"""
        def capture_thread():
            sniff(
                iface=interface,
                prn=self.packet_callback,
                store=0,
                stop_filter=lambda _: self.stop_capture.is_set()
            )
        
        self.capture_thread = threading.Thread(target=capture_thread, daemon=True)
        self.capture_thread.start()
        print(f"[+] Packet capture started on interface: {interface}")
    
    def stop(self):
        """Stop packet capture gracefully"""
        self.stop_capture.set()
        if self.capture_thread:
            self.capture_thread.join()
        print("[+] Packet capture stopped")


# ==================== TRAFFIC ANALYZER ====================
class TrafficAnalyzer:
    """
    Analyzes captured packets and extracts features for threat detection.
    Tracks flow statistics and calculates network traffic metrics.
    """
    def __init__(self):
        self.connections = defaultdict(list)
        self.flow_stats = defaultdict(lambda: {
            'packet_count': 0,
            'byte_count': 0,
            'start_time': None,
            'last_time': None,
            'syn_count': 0,
            'ack_count': 0,
            'fin_count': 0
        })
        
    def analyze_packet(self, packet):
        """Extract features from packet for threat detection"""
        if IP not in packet:
            return None
            
        try:
            ip_src = packet[IP].src
            ip_dst = packet[IP].dst
            
            # Handle TCP packets
            if TCP in packet:
                port_src = packet[TCP].sport
                port_dst = packet[TCP].dport
                tcp_flags = packet[TCP].flags
                window_size = packet[TCP].window
            # Handle UDP packets
            elif UDP in packet:
                port_src = packet[UDP].sport
                port_dst = packet[UDP].dport
                tcp_flags = 0
                window_size = 0
            else:
                return None
            
            flow_key = (ip_src, ip_dst, port_src, port_dst)
            
            # Update flow statistics
            stats = self.flow_stats[flow_key]
            stats['packet_count'] += 1
            stats['byte_count'] += len(packet)
            
            current_time = float(packet.time)
            if stats['start_time'] is None:
                stats['start_time'] = current_time
            stats['last_time'] = current_time
            
            # Track TCP flags
            if TCP in packet:
                if 'S' in str(tcp_flags):
                    stats['syn_count'] += 1
                if 'A' in str(tcp_flags):
                    stats['ack_count'] += 1
                if 'F' in str(tcp_flags):
                    stats['fin_count'] += 1
            
            return self.extract_features(packet, stats, tcp_flags, window_size)
            
        except Exception as e:
            print(f"[!] Error analyzing packet: {e}")
            return None
    
    def extract_features(self, packet, stats, tcp_flags, window_size):
        """Calculate detailed network traffic features"""
        flow_duration = max(stats['last_time'] - stats['start_time'], 0.001)
        
        return {
            'packet_size': len(packet),
            'flow_duration': flow_duration,
            'packet_rate': stats['packet_count'] / flow_duration,
            'byte_rate': stats['byte_count'] / flow_duration,
            'tcp_flags': int(tcp_flags) if tcp_flags else 0,
            'window_size': window_size,
            'syn_count': stats['syn_count'],
            'ack_count': stats['ack_count'],
            'fin_count': stats['fin_count'],
            'packet_count': stats['packet_count']
        }


# ==================== DETECTION ENGINE ====================
class DetectionEngine:
    """
    Hybrid detection engine combining signature-based and anomaly-based detection.
    Uses Isolation Forest for anomaly detection and custom rules for known attacks.
    """
    def __init__(self):
        # Anomaly detection model (Isolation Forest)
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        
        # Load signature-based detection rules
        self.signature_rules = self.load_signature_rules()
        self.training_data = []
        self.is_trained = False
        
    def load_signature_rules(self):
        """Define signature-based detection rules for known attacks"""
        return {
            'syn_flood': {
                'name': 'SYN Flood Attack',
                'condition': lambda f: (
                    f['syn_count'] > 10 and 
                    f['packet_rate'] > 100 and
                    f['ack_count'] < 2
                )
            },
            'port_scan': {
                'name': 'Port Scanning',
                'condition': lambda f: (
                    f['packet_size'] < 100 and
                    f['packet_rate'] > 50 and
                    f['syn_count'] > 5
                )
            },
            'ddos': {
                'name': 'DDoS Attack',
                'condition': lambda f: (
                    f['packet_rate'] > 200 and
                    f['byte_rate'] > 100000
                )
            },
            'abnormal_traffic': {
                'name': 'Abnormal Traffic Pattern',
                'condition': lambda f: (
                    f['packet_size'] > 1500 or
                    f['window_size'] == 0
                )
            }
        }
    
    def train_anomaly_detector(self, normal_traffic_data):
        """Train anomaly detection model on normal traffic baseline"""
        if len(normal_traffic_data) > 10:
            self.anomaly_detector.fit(normal_traffic_data)
            self.is_trained = True
            print(f"[+] Anomaly detector trained on {len(normal_traffic_data)} samples")
    
    def detect_threats(self, features):
        """
        Detect threats using both signature-based and anomaly-based methods.
        Returns list of detected threats with confidence scores.
        """
        threats = []
        
        # Signature-based detection
        for rule_name, rule in self.signature_rules.items():
            try:
                if rule['condition'](features):
                    threats.append({
                        'type': 'signature',
                        'rule': rule_name,
                        'name': rule['name'],
                        'confidence': 1.0,
                        'severity': 'HIGH'
                    })
            except Exception as e:
                pass  # Skip rule if features missing
        
        # Anomaly-based detection
        if self.is_trained:
            try:
                feature_vector = np.array([[
                    features['packet_size'],
                    features['packet_rate'],
                    features['byte_rate'],
                    features['tcp_flags'],
                    features['window_size']
                ]])
                
                anomaly_score = self.anomaly_detector.score_samples(feature_vector)[0]
                
                # Threshold for anomaly detection
                if anomaly_score < -0.5:
                    confidence = min(1.0, abs(anomaly_score))
                    severity = 'CRITICAL' if confidence > 0.8 else 'MEDIUM'
                    
                    threats.append({
                        'type': 'anomaly',
                        'name': 'Anomalous Network Behavior',
                        'score': float(anomaly_score),
                        'confidence': confidence,
                        'severity': severity
                    })
            except Exception as e:
                print(f"[!] Anomaly detection error: {e}")
        
        return threats


# ==================== ALERT SYSTEM ====================
class AlertSystem:
    """
    Manages threat alerts with logging, escalation, and notification capabilities.
    Logs alerts to file and can be extended for email/Slack notifications.
    """
    def __init__(self, log_file="ids_alerts.log"):
        self.logger = logging.getLogger("IDS_Alerts")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        self.alert_count = 0
        
    def generate_alert(self, threat, packet_info):
        """Generate and log security alert"""
        self.alert_count += 1
        
        alert = {
            'alert_id': self.alert_count,
            'timestamp': datetime.now().isoformat(),
            'threat_type': threat['type'],
            'threat_name': threat.get('name', 'Unknown'),
            'source_ip': packet_info.get('source_ip'),
            'destination_ip': packet_info.get('destination_ip'),
            'source_port': packet_info.get('source_port'),
            'destination_port': packet_info.get('destination_port'),
            'confidence': threat.get('confidence', 0.0),
            'severity': threat.get('severity', 'MEDIUM'),
            'details': threat
        }
        
        # Log based on severity
        if threat.get('severity') == 'CRITICAL':
            self.logger.critical(f"🚨 CRITICAL THREAT: {json.dumps(alert, indent=2)}")
        elif threat.get('severity') == 'HIGH':
            self.logger.error(f"⚠️  HIGH THREAT: {json.dumps(alert, indent=2)}")
        else:
            self.logger.warning(f"ℹ️  THREAT DETECTED: {json.dumps(alert, indent=2)}")
        
        return alert


# ==================== MAIN IDS SYSTEM ====================
class IntrusionDetectionSystem:
    """
    Main IDS coordinator that integrates all components.
    Monitors network traffic in real-time and detects security threats.
    """
    def __init__(self, interface="eth0"):
        self.packet_capture = PacketCapture()
        self.traffic_analyzer = TrafficAnalyzer()
        self.detection_engine = DetectionEngine()
        self.alert_system = AlertSystem()
        self.interface = interface
        self.stats = {
            'packets_analyzed': 0,
            'threats_detected': 0,
            'start_time': None
        }
        
    def train_on_normal_traffic(self, duration=60):
        """
        Train anomaly detector on normal traffic baseline.
        Capture traffic for specified duration (seconds) to establish baseline.
        """
        print(f"[+] Training on normal traffic for {duration} seconds...")
        self.packet_capture.start_capture(self.interface)
        
        training_features = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                packet = self.packet_capture.packet_queue.get(timeout=1)
                features = self.traffic_analyzer.analyze_packet(packet)
                
                if features:
                    feature_vector = [
                        features['packet_size'],
                        features['packet_rate'],
                        features['byte_rate'],
                        features['tcp_flags'],
                        features['window_size']
                    ]
                    training_features.append(feature_vector)
                    
            except queue.Empty:
                continue
        
        self.packet_capture.stop()
        
        if training_features:
            self.detection_engine.train_anomaly_detector(np.array(training_features))
        else:
            print("[!] No training data collected - anomaly detection disabled")
    
    def start(self):
        """Start the IDS monitoring system"""
        print("=" * 70)
        print("  NETWORK INTRUSION DETECTION SYSTEM (IDS)")
        print("  AI-Powered Security Monitoring")
        print("=" * 70)
        print(f"[+] Starting IDS on interface: {self.interface}")
        print("[+] Press Ctrl+C to stop\n")
        
        self.stats['start_time'] = datetime.now()
        self.packet_capture.start_capture(self.interface)
        
        try:
            while True:
                try:
                    packet = self.packet_capture.packet_queue.get(timeout=1)
                    features = self.traffic_analyzer.analyze_packet(packet)
                    
                    if features:
                        self.stats['packets_analyzed'] += 1
                        
                        # Detect threats
                        threats = self.detection_engine.detect_threats(features)
                        
                        # Generate alerts for detected threats
                        for threat in threats:
                            self.stats['threats_detected'] += 1
                            
                            packet_info = {
                                'source_ip': packet[IP].src,
                                'destination_ip': packet[IP].dst,
                            }
                            
                            if TCP in packet:
                                packet_info['source_port'] = packet[TCP].sport
                                packet_info['destination_port'] = packet[TCP].dport
                            elif UDP in packet:
                                packet_info['source_port'] = packet[UDP].sport
                                packet_info['destination_port'] = packet[UDP].dport
                            
                            self.alert_system.generate_alert(threat, packet_info)
                        
                        # Print stats every 100 packets
                        if self.stats['packets_analyzed'] % 100 == 0:
                            self.print_stats()
                            
                except queue.Empty:
                    continue
                    
        except KeyboardInterrupt:
            print("\n[+] Stopping IDS...")
            self.packet_capture.stop()
            self.print_final_stats()
    
    def print_stats(self):
        """Print current IDS statistics"""
        print(f"\r[STATS] Packets: {self.stats['packets_analyzed']} | "
              f"Threats: {self.stats['threats_detected']}", end='')
    
    def print_final_stats(self):
        """Print final statistics on shutdown"""
        runtime = datetime.now() - self.stats['start_time']
        print("\n" + "=" * 70)
        print("  IDS SESSION SUMMARY")
        print("=" * 70)
        print(f"  Runtime: {runtime}")
        print(f"  Packets Analyzed: {self.stats['packets_analyzed']}")
        print(f"  Threats Detected: {self.stats['threats_detected']}")
        print(f"  Detection Rate: {self.stats['threats_detected']/max(self.stats['packets_analyzed'], 1)*100:.2f}%")
        print("=" * 70)


# ==================== TESTING MODULE ====================
def test_ids():
    """
    Test IDS with simulated attack scenarios.
    Creates mock packets representing different attack types.
    """
    print("\n[TEST MODE] Starting IDS Test...\n")
    
    # Initialize IDS
    ids = IntrusionDetectionSystem()
    
    # Create test packets simulating various scenarios
    test_packets = [
        # Normal traffic
        IP(src="192.168.1.10", dst="192.168.1.1") / TCP(sport=1234, dport=80, flags="A"),
        IP(src="192.168.1.11", dst="192.168.1.1") / TCP(sport=1235, dport=443, flags="PA"),
        
        # SYN flood attack simulation
        IP(src="10.0.0.1", dst="192.168.1.100") / TCP(sport=5678, dport=80, flags="S"),
        IP(src="10.0.0.2", dst="192.168.1.100") / TCP(sport=5679, dport=80, flags="S"),
        IP(src="10.0.0.3", dst="192.168.1.100") / TCP(sport=5680, dport=80, flags="S"),
        IP(src="10.0.0.4", dst="192.168.1.100") / TCP(sport=5681, dport=80, flags="S"),
        IP(src="10.0.0.5", dst="192.168.1.100") / TCP(sport=5682, dport=80, flags="S"),
        
        # Port scan simulation
        IP(src="192.168.1.200", dst="192.168.1.100") / TCP(sport=4321, dport=22, flags="S"),
        IP(src="192.168.1.200", dst="192.168.1.100") / TCP(sport=4321, dport=23, flags="S"),
        IP(src="192.168.1.200", dst="192.168.1.100") / TCP(sport=4321, dport=25, flags="S"),
        IP(src="192.168.1.200", dst="192.168.1.100") / TCP(sport=4321, dport=80, flags="S"),
    ]
    
    # Process test packets
    for i, packet in enumerate(test_packets, 1):
        print(f"\n[Packet {i}] {packet.summary()}")
        
        # Analyze packet
        features = ids.traffic_analyzer.analyze_packet(packet)
        
        if features:
            # Detect threats
            threats = ids.detection_engine.detect_threats(features)
            
            if threats:
                print(f"  ⚠️  THREATS DETECTED: {len(threats)}")
                for threat in threats:
                    print(f"    - {threat['name']} ({threat['type']}) - "
                          f"Confidence: {threat['confidence']:.2f}")
            else:
                print("  ✓ No threats detected")
        else:
            print("  ⓘ Packet skipped (no analyzable features)")
    
    print("\n[TEST MODE] IDS Test Completed.\n")


# ==================== MAIN ENTRY POINT ====================
if __name__ == "__main__":
    import sys
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run in test mode
        test_ids()
    else:
        # Run in production mode
        print("""
        NOTE: Running IDS requires root/administrator privileges for packet capture.
        
        Usage:
            sudo python ids.py              # Start IDS monitoring
            python ids.py test              # Run test mode with simulated attacks
            
        Optional: Train on normal traffic first (recommended)
            ids = IntrusionDetectionSystem(interface="eth0")
            ids.train_on_normal_traffic(duration=60)
            ids.start()
        """)
        
        # Uncomment to start IDS (requires root privileges)
        # ids = IntrusionDetectionSystem(interface="eth0")  # Change interface as needed
        # ids.start()
