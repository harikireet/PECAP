"""
PCAP StoryTeller - Geolocation Orchestrator
------------------------------------------
This high-level service provides an easy way for the API to request 
geolocation for either a single IP or a large batch of IPs.
"""

from services.geoip_scanner import analyze_geoip_lookup

class GeolocationService:
    """
    Service class that manages IP address tracking and geographical resolution.
    """
    def __init__(self):
        # We keep a service-level cache to remember lookups during the session
        self.session_cache = {}
    
    def analyze_ip(self, ip_address):
        """
        Public method to get location data for one IP.
        
        Args:
            ip_address (str): The IP to investigate.
        """
        # We delegate the heavy lifting to the geoip_scanner utility
        return analyze_geoip_lookup(ip_address, self.session_cache)

    def analyze_batch(self, ip_address_list, limit_count=50):
        """
        Geolocates many IPs at once (Batch Mode).
        
        Args:
            ip_address_list (set/list): Unique IP addresses to look up.
            limit_count (int): Safety limit to prevent getting blocked by APIs.
        """
        return [self.analyze_ip(ip) for ip in list(ip_address_list)[:limit_count]]
