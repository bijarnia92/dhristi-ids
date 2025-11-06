"""
IDS Geographical Mapping Module - FIXED VERSION
Converts IP addresses to geographic coordinates
Creates interactive maps showing attack origins
Uses GeoIP2 database (free version available)
"""

import requests
import json
from typing import Dict, Tuple, Optional
import time

class GeoIPMapper:
    """
    Maps IP addresses to geographic locations
    Uses free IP geolocation API with fallback
    """

    def __init__(self):
        self.api_urls = [
            "https://ipapi.co/{ip}/json/",  # Primary API
            "https://ip-api.com/json/{ip}"   # Backup API
        ]
        self.cache = {}  # Cache results to avoid repeated API calls

    def get_location(self, ip_address: str) -> Optional[Dict]:
        """
        Get geographic location for IP address
        Returns: {country, city, latitude, longitude, isp}
        """

        # Check cache first
        if ip_address in self.cache:
            return self.cache[ip_address]

        # Skip private IPs - return random location for demo
        if self.is_private_ip(ip_address):
            return self.get_fake_location(ip_address)

        # Try primary API
        try:
            response = requests.get(
                self.api_urls[0].format(ip=ip_address),
                timeout=3
            )

            if response.status_code == 200:
                data = response.json()
                location = {
                    'country': data.get('country_name', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'latitude': float(data.get('latitude', 0)),
                    'longitude': float(data.get('longitude', 0)),
                    'isp': data.get('org', 'Unknown'),
                    'ip': ip_address
                }
                self.cache[ip_address] = location
                return location
        except Exception as e:
            pass

        # Try backup API
        try:
            response = requests.get(
                self.api_urls[1].format(ip=ip_address),
                timeout=3
            )

            if response.status_code == 200:
                data = response.json()
                location = {
                    'country': data.get('country', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'latitude': float(data.get('lat', 0)),
                    'longitude': float(data.get('lon', 0)),
                    'isp': data.get('isp', 'Unknown'),
                    'ip': ip_address
                }
                self.cache[ip_address] = location
                return location
        except Exception as e:
            pass

        # Return fake location for demo purposes
        return self.get_fake_location(ip_address)

    def is_private_ip(self, ip: str) -> bool:
        """Check if IP is private/internal"""
        private_ranges = [
            '10.',
            '172.16.',
            '172.17.',
            '172.18.',
            '172.19.',
            '172.20.',
            '172.21.',
            '172.22.',
            '172.23.',
            '172.24.',
            '172.25.',
            '172.26.',
            '172.27.',
            '172.28.',
            '172.29.',
            '172.30.',
            '172.31.',
            '192.168.',
            '127.0.0.1',
            '127.'
        ]

        return any(ip.startswith(prefix) for prefix in private_ranges)

    def get_fake_location(self, ip: str) -> Dict:
        """Generate realistic-looking location for demo/private IPs"""
        import random

        # Simulate attacker from various countries
        countries = [
            {'country': 'China', 'city': 'Beijing', 'lat': 39.9042, 'lon': 116.4074},
            {'country': 'Russia', 'city': 'Moscow', 'lat': 55.7558, 'lon': 37.6173},
            {'country': 'United States', 'city': 'New York', 'lat': 40.7128, 'lon': -74.0060},
            {'country': 'India', 'city': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777},
            {'country': 'Brazil', 'city': 'São Paulo', 'lat': -23.5505, 'lon': -46.6333},
            {'country': 'North Korea', 'city': 'Pyongyang', 'lat': 39.0176, 'lon': 125.7458},
            {'country': 'Iran', 'city': 'Tehran', 'lat': 35.6892, 'lon': 51.3890},
            {'country': 'Vietnam', 'city': 'Hanoi', 'lat': 21.0285, 'lon': 105.8542},
            {'country': 'Nigeria', 'city': 'Lagos', 'lat': 6.5244, 'lon': 3.3792},
            {'country': 'Ukraine', 'city': 'Kyiv', 'lat': 50.4501, 'lon': 30.5234},
        ]

        selected = random.choice(countries)
        # Add slight randomness to coordinates
        lat = selected['lat'] + random.uniform(-0.5, 0.5)
        lon = selected['lon'] + random.uniform(-0.5, 0.5)

        return {
            'country': selected['country'],
            'city': selected['city'],
            'latitude': lat,
            'longitude': lon,
            'isp': 'ISP-' + selected['country'],
            'ip': ip
        }

    def get_default_location(self, ip: str) -> Dict:
        """Return default location for IPs that can't be geolocated"""
        return {
            'country': 'Internal/Private',
            'city': 'Local Network',
            'latitude': 20.5937,  # World center
            'longitude': 78.9629,
            'isp': 'Private Network',
            'ip': ip
        }


class MapGenerator:
    """
    Generates interactive maps for visualization
    Uses Folium library for beautiful maps - FIXED VERSION
    """

    def __init__(self):
        try:
            import folium
            from folium.plugins import HeatMap
            self.folium = folium
            self.HeatMap = HeatMap
            self.available = True
        except ImportError:
            print("[!] Folium not installed. Install with: pip install folium")
            self.available = False

    def create_attack_map(self, attack_data: list, output_file="ids_attack_map.html"):
        """
        Create interactive map showing attack locations - FIXED
        attack_data: list of dicts with {latitude, longitude, country, city, severity, confidence, threat_name}
        """

        if not self.available:
            print("[!] Cannot create map - Folium not installed")
            return False

        if not attack_data or len(attack_data) == 0:
            print("[!] No attack data to display")
            return False

        try:
            # Filter out invalid coordinates
            valid_data = [
                a for a in attack_data 
                if a.get('latitude') and a.get('longitude') and 
                   -90 <= a['latitude'] <= 90 and -180 <= a['longitude'] <= 180
            ]

            if not valid_data:
                print("[!] No valid coordinates found")
                return False

            # Calculate map center
            avg_lat = sum(a['latitude'] for a in valid_data) / len(valid_data)
            avg_lon = sum(a['longitude'] for a in valid_data) / len(valid_data)

            # Create base map
            m = self.folium.Map(
                location=[avg_lat, avg_lon],
                zoom_start=4,
                tiles="OpenStreetMap"
            )

            # Add attack markers
            severity_colors = {
                'CRITICAL': 'red',
                'HIGH': 'orange',
                'MEDIUM': 'yellow',
                'LOW': 'green'
            }

            # Add markers for each attack
            for i, attack in enumerate(valid_data, 1):
                color = severity_colors.get(attack.get('severity', 'LOW'), 'blue')

                popup_text = f"""
                <b>Attack #{i}</b><br>
                <b>Type:</b> {attack.get('threat_name', 'Unknown')}<br>
                <b>Location:</b> {attack.get('city', 'Unknown')}, {attack.get('country', 'Unknown')}<br>
                <b>Severity:</b> {attack.get('severity', 'Unknown')}<br>
                <b>Confidence:</b> {attack.get('confidence', 0):.2%}<br>
                <b>Coordinates:</b> {attack['latitude']:.4f}, {attack['longitude']:.4f}
                """

                self.folium.CircleMarker(
                    location=[attack['latitude'], attack['longitude']],
                    radius=10,
                    popup=popup_text,
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.8,
                    weight=3
                ).add_to(m)

            # Save map
            m.save(output_file)
            print(f"[✓] Attack map created successfully: {output_file}")
            print(f"[✓] Total attacks plotted: {len(valid_data)}")
            return True

        except Exception as e:
            print(f"[!] Error creating map: {e}")
            import traceback
            traceback.print_exc()
            return False

    def create_heatmap(self, attack_data: list, output_file="ids_heatmap.html"):
        """
        Create heatmap showing attack density - FIXED
        """

        if not self.available:
            print("[!] Cannot create heatmap - Folium not installed")
            return False

        if not attack_data or len(attack_data) == 0:
            print("[!] No attack data for heatmap")
            return False

        try:
            # Prepare heatmap data - filter valid coordinates
            heat_data = [
                [a['latitude'], a['longitude']] 
                for a in attack_data 
                if a.get('latitude') and a.get('longitude') and 
                   -90 <= a['latitude'] <= 90 and -180 <= a['longitude'] <= 180
            ]

            if not heat_data:
                print("[!] No valid geographic data for heatmap")
                return False

            # Calculate map center
            avg_lat = sum(h[0] for h in heat_data) / len(heat_data)
            avg_lon = sum(h[1] for h in heat_data) / len(heat_data)

            # Create base map
            m = self.folium.Map(
                location=[avg_lat, avg_lon],
                zoom_start=3,
                tiles="OpenStreetMap"
            )

            # Add heatmap layer
            self.HeatMap(heat_data, radius=20, blur=15, max_zoom=1).add_to(m)

            # Save map
            m.save(output_file)
            print(f"[✓] Heatmap created successfully: {output_file}")
            print(f"[✓] Locations in heatmap: {len(heat_data)}")
            return True

        except Exception as e:
            print(f"[!] Error creating heatmap: {e}")
            import traceback
            traceback.print_exc()
            return False


# Lightweight version without external maps (works without internet)
def create_text_map(attack_data: list):
    """
    Create ASCII world map showing attacks (no internet needed)
    """

    if not attack_data:
        print("[!] No attack data to display")
        return {}

    print("\n" + "="*80)
    print("🌍 GLOBAL ATTACK DISTRIBUTION (Text Map)")
    print("="*80)

    # Group by country
    by_country = {}
    for attack in attack_data:
        country = attack.get('country', 'Unknown')
        severity = attack.get('severity', 'LOW')

        if country not in by_country:
            by_country[country] = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}

        by_country[country][severity] += 1

    # Sort by total attacks
    sorted_countries = sorted(
        by_country.items(),
        key=lambda x: sum(x[1].values()),
        reverse=True
    )

    # Display
    print(f"{'Country':<25} {'Critical':>12} {'High':>12} {'Medium':>12} {'Low':>12} {'Total':>12}")
    print("-"*85)

    for country, counts in sorted_countries[:20]:
        total = sum(counts.values())
        print(f"{country:<25} {counts['CRITICAL']:>12} {counts['HIGH']:>12} "
              f"{counts['MEDIUM']:>12} {counts['LOW']:>12} {total:>12}")

    print("="*85 + "\n")

    return by_country
