"""
PCAP StoryTeller - Threat Analyzer
---------------------------------
This is the "Security Officer" of the backend. It looks at every 
network event and assigns it a "Risk Score" based on how suspicious 
it looks to a security forensic expert.
"""

import ipaddress
from services.geoip_scanner import analyze_geoip_lookup
from services.threat_heuristics import ThreatHeuristics, SUSPICIOUS_PORTS, SCAN_PORTS

class ThreatAnalyzer:
    """
    Main engine for security risk calculation and multi-packet pattern detection.
    """
    
    def __init__(self, events, links):
        """
        Initializes with the forensic results from the parser.
        """
        self.events = events
        self.links = links
        self.attack_patterns = []   # List of multi-packet hacker behaviors found
        self.threat_scores = {}     # Cache for individual event risk scores
        self.geoip_cache = {}       # Prevents repeated web lookups for the same IP

    def get_risk_score(self, event_id):
        """
        Calculates a 0-100 risk score for a single network event.
        
        Args:
            event_id (int): The unique forensic ID of the event.
            
        Returns:
            int: A score from 0 (Safe) to 100 (Critical).
        """
        # 1. Use the cached score if we've already calculated it
        if event_id in self.threat_scores:
            return self.threat_scores[event_id]
        
        # 2. Locate the event data in our list
        target_event = next((e for e in self.events if e['id'] == event_id), None)
        if not target_event: 
            return 0
        
        current_risk_score = 0
        event_type = target_event.get('type', '')
        details = target_event.get('details', {})
        source_ip = target_event.get('source_ip', '')

        # 3. Apply Scoring Logic based on the specific Protocol
        if event_type == 'TCP Connection':
            dest_port = details.get('dport', 0)
            # Is this a port that hackers often target (like remote desktop)?
            if dest_port in SUSPICIOUS_PORTS: 
                current_risk_score += 30
            # Is it a system/admin port (0-1024)?
            if dest_port < 1024: 
                current_risk_score += 15
            # Is it a common port used for scanning?
            if dest_port in SCAN_PORTS: 
                current_risk_score += 10
                
        elif event_type == 'DNS Query':
            # Identify suspicious words inside the domain name
            query_text = details.get('query', '').lower()
            if any(evil in query_text for evil in ['malware', 'phishing', 'c2', 'exploit']): 
                current_risk_score += 40
            # Is the query unusually long? (Could be stolen data hidden in DNS)
            if len(query_text) > 50: 
                current_risk_score += 15
                
        elif event_type == 'HTTP Request':
            http_method = details.get('method', '').upper()
            # Uploading data (POST/PUT) is more interesting than just viewing (GET)
            if http_method in ['POST', 'PUT']: 
                current_risk_score += 15
                
        elif event_type == 'TLS SNI':
            website_sni = details.get('sni', '').lower()
            # Connections to dynamic webhook/pastebin sites often signal data theft
            if any(evil_site in website_sni for evil_site in ['dynamic', 'pastebin', 'webhook']): 
                current_risk_score += 25
                
        elif event_type == 'ICMP': 
            # Ping is generally low risk but used for network discovery
            current_risk_score += 5

        # 4. Context Rule: Is this traffic coming from the suspicious outside internet?
        if source_ip and not self._is_internal_ip(source_ip): 
            current_risk_score += 10
            
        # Ensure the score never exceeds 100
        final_score = min(current_risk_score, 100)
        self.threat_scores[event_id] = final_score
        return final_score

    def run_detection_engines(self):
        """
        Orchestrates specialized heuristics to find complex attack patterns.
        """
        patterns_found = []
        
        # Engine 1: Scan for systematic port probing
        patterns_found.extend(ThreatHeuristics.detect_port_scanning(self.events))
        
        # Engine 2: Scan for DNS-to-Server connections (possible data theft)
        patterns_found.extend(ThreatHeuristics.detect_dns_tunnels(self.events, self.links))
        
        # Expert Rule: Too many web requests could mean an automated scraper is at work
        web_requests = [e for e in self.events if e['type'] == 'HTTP Request']
        if len(web_requests) > 3:
            patterns_found.append({
                'type': 'data_exfil_risk',
                'severity': 'MEDIUM',
                'description': f"High volume of web requests ({len(web_requests)}). Potential automated exfiltration."
            })
            
        self.attack_patterns = patterns_found
        return patterns_found

    def get_security_summary(self):
        """
        Generates the overall safety report for the student dashboard.
        """
        if not self.attack_patterns: 
            self.run_detection_engines()
            
        # Calculate scores for every event in the capture
        all_event_scores = [self.get_risk_score(e['id']) for e in self.events]
        average_risk = sum(all_event_scores) / len(all_event_scores) if all_event_scores else 0
        
        # The overall score is either the average OR boosted by specific attack detections
        pattern_impact_score = self._calculate_pattern_severity()
        combined_score = min(100, max(average_risk, pattern_impact_score))
        
        return {
            'overall_score': round(combined_score, 1),
            'threat_level': self._map_score_to_label(combined_score),
            'high_threat_count': len([s for s in all_event_scores if s >= 60]),
            'pattern_count': len(self.attack_patterns),
            'patterns': self.attack_patterns[:5] # Return top findings for the summary list
        }

    def _calculate_pattern_severity(self):
        """
        Calculates how much the overall risk should increase based on detected patterns.
        """
        severity_values = {'CRITICAL': 40, 'HIGH': 25, 'MEDIUM': 12, 'LOW': 5}
        total_pattern_weight = sum(severity_values.get(p.get('severity', '').upper(), 5) for p in self.attack_patterns)
        return min(total_pattern_weight, 100)

    def _map_score_to_label(self, score):
        """
        Categorizes a numerical risk into a friendly text level.
        """
        if score >= 70: return 'CRITICAL'
        if score >= 50: return 'HIGH'
        if score >= 30: return 'MEDIUM'
        return 'LOW'

    def _is_internal_ip(self, ip_string):
        """
        Checks if an IP is part of a private network (like Home or Office WiFi).
        Internal traffic is generally safer than external internet traffic.
        """
        try: 
            return ipaddress.ip_address(ip_string).is_private
        except: 
            return False
            
    def analyze_ip_location(self, ip_address):
        """
        Geolocates an IP to see which country or city it belongs to.
        """
        return analyze_geoip_lookup(ip_address, self.geoip_cache)
