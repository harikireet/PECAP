"""
PCAP StoryTeller - Threat Orchestration Service
----------------------------------------------
This is a high-level service that connects the data from the parser 
to our 'ThreatAnalyzer' expert to produce a full security report.
"""

from services.threat_analyzer import ThreatAnalyzer

class ThreatService:
    """
    Orchestrates the security analysis lifecycle for the forensic dashboard.
    """
    def __init__(self, forensic_events, relationship_links):
        """
        Initializes the service with the raw forensic data.
        """
        self.forensic_events = forensic_events
        self.relationship_links = relationship_links
        # Create an instance of our expert security analyzer
        self.security_analyzer = ThreatAnalyzer(forensic_events, relationship_links)
    
    def perform_full_security_scan(self):
        """
        Runs all heuristics and aggregates the security risk findings.
        
        Returns:
            dict: Comprehensive threat summary and per-event scores.
        """
        # Step 1: Run the detection engines to find multi-packet attack patterns
        self.security_analyzer.run_detection_engines()
        
        # Step 2: Calculate an individual risk score for every event
        risk_scores_map = {
            event['id']: self.security_analyzer.get_risk_score(event['id']) 
            for event in self.forensic_events
        }
        
        # Step 3: Compile the high-level security summary (Overall Score, Trends, etc.)
        security_summary = self.security_analyzer.get_security_summary()
        
        # Return everything needed by the dashboard frontend
        return {
            'summary': security_summary,
            'threat_scores': risk_scores_map,
            'detected_patterns': self.security_analyzer.attack_patterns
        }
