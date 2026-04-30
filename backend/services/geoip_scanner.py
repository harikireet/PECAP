"""
PCAP StoryTeller - GeoIP Scanner Logic
-------------------------------------
This module performs the "Magic" of turning an IP address into a 
physical location on Earth by asking external databases (API lookups).
"""

import time
import requests
import ipaddress

def _is_internal_ip(ip_address):
    """
    Checks if an IP address is private (like your home or local office network).
    Private IPs don't have a physical global location.
    """
    try:
        return ipaddress.ip_address(ip_address).is_private
    except Exception:
        return False

def analyze_geoip_lookup(ip_address, lookup_cache):
    """
    Performs a GeoIP lookup with dual-API redundancy and caching.
    
    Args:
        ip_address (str): The IP to locate.
        lookup_cache (dict): A dictionary to store results so we don't 
                           ask the same IP twice (this saves time/bandwidth).
                           
    Returns:
        dict: Geographic data (city, country, latitude, longitude, etc.)
    """
    # 1. Check if we already know this IP from our memory (Cache)
    if ip_address in lookup_cache:
        return lookup_cache[ip_address]
    
    # 2. Handle private IP addresses (Internal traffic)
    if _is_internal_ip(ip_address):
        internal_result = {
            'ip': ip_address,
            'country': 'Private',
            'city': 'Internal Network',
            'latitude': None,
            'longitude': None,
            'isp': 'Private/Internal',
            'type': 'private',
            'timezone': 'N/A',
            'asn': 'N/A',
            'reverse_dns': 'Local Host'
        }
        lookup_cache[ip_address] = internal_result
        return internal_result
    
    # 3. Attempt Lookup 1: IPInfo.io (Highly accurate)
    try:
        response = requests.get(f"https://ipinfo.io/{ip_address}/json", timeout=5)
        if response.status_code == 200:
            api_data = response.json()
            if 'loc' in api_data:
                latitude, longitude = api_data['loc'].split(',')
                location_result = {
                    'ip': ip_address,
                    'country': api_data.get('country', 'Unknown'),
                    'city': api_data.get('city', 'Unknown'),
                    'latitude': float(latitude),
                    'longitude': float(longitude),
                    'isp': api_data.get('org', 'Unknown'),
                    'type': 'external',
                    'timezone': api_data.get('timezone', ''),
                    'asn': api_data.get('org', '').split()[0] if api_data.get('org') else '',
                    'reverse_dns': api_data.get('hostname', '')
                }
                lookup_cache[ip_address] = location_result
                return location_result
    except Exception as error:
        print(f"[!] IPInfo lookup failed for {ip_address}: {str(error)}")
    
    # 4. Attempt Lookup 2: IP-API.com (Backup redundancy)
    try:
        # We wait a tiny bit (0.2s) to avoid hitting IP-API's rate limits
        time.sleep(0.2)
        response = requests.get(f"https://ip-api.com/json/{ip_address}", timeout=5)
        if response.status_code == 200:
            api_data = response.json()
            if api_data.get('status') == 'success':
                location_result = {
                    'ip': ip_address,
                    'country': api_data.get('country', 'Unknown'),
                    'city': api_data.get('city', 'Unknown'),
                    'latitude': api_data.get('lat'),
                    'longitude': api_data.get('lon'),
                    'isp': api_data.get('isp', 'Unknown'),
                    'type': 'external',
                    'timezone': api_data.get('timezone', ''),
                    'asn': api_data.get('as', '').split()[0] if api_data.get('as') else '',
                    'reverse_dns': api_data.get('reverse', '')
                }
                lookup_cache[ip_address] = location_result
                return location_result
    except Exception as error:
        print(f"[!] IP-API backup failed for {ip_address}: {str(error)}")
    
    # 5. Final Fallback: If both APIs fail, return a generic 'Unknown' result
    fallback_result = {
        'ip': ip_address, 'country': 'Unknown', 'city': 'Unable to Determine',
        'latitude': None, 'longitude': None, 'isp': 'Unknown', 'type': 'external',
        'timezone': '', 'asn': '', 'reverse_dns': ''
    }
    lookup_cache[ip_address] = fallback_result
    return fallback_result
