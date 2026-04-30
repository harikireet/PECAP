"""
PCAP StoryTeller - Threat Heuristics
-----------------------------------
This module contains the "Rules of Thumb" (Heuristics) used to detect 
suspicious network behavior. Instead of looking for known viruses, 
we look for "weird patterns" like scanning ports or tunneling data.
"""

from collections import defaultdict

# A dictionary of ports that are commonly targets for hackers.
# We map the port number to a friendly name for the dashboard.
SUSPICIOUS_PORTS = {
    445: 'SMB (File sharing)', 
    139: 'NetBIOS', 
    3389: 'Remote Desktop (RDP)', 
    22: 'Secure Shell (SSH)', 
    23: 'Telnet (Unsecure)',
    21: 'FTP (File Transfer)', 
    5900: 'VNC (Screen Sharing)', 
    3306: 'MySQL Database', 
    5432: 'PostgreSQL Database',
    27017: 'MongoDB', 
    6379: 'Redis Cache', 
    9200: 'Elasticsearch'
}

# A set of standard ports that are often scanned by bots or discovery tools.
SCAN_PORTS = {80, 443, 8080, 8443, 22, 3389, 445, 139, 21, 25, 53, 123}

class ThreatHeuristics:
    """
    Expert system that scans for attack patterns in the network story.
    """

    @staticmethod
    def detect_port_scanning(event_list):
        """
        Looks for one computer trying to open many different doors (ports) on others.
        
        Args:
            event_list (list): The list of forensic events to analyze.
            
        Returns:
            list: A list of detected 'port_scanning' patterns.
        """
        # Filter for only TCP Connection attempts (conversations)
        connection_attempts = [event for event in event_list if event['type'] == 'TCP Connection']
        detected_patterns = []
        
        if len(connection_attempts) > 5:
            # Map of SourceIP -> Set of unique ports visited
            source_ip_port_map = defaultdict(set)
            
            for event in connection_attempts:
                source_ip = event.get('source_ip')
                dest_port = event.get('details', {}).get('dport')
                
                if source_ip and dest_port:
                    source_ip_port_map[source_ip].add(dest_port)
            
            # Check: Did any single computer touch more than 10 unique ports?
            for source_ip, unique_ports in source_ip_port_map.items():
                if len(unique_ports) > 10:
                    detected_patterns.append({
                        'type': 'port_scanning',
                        'severity': 'HIGH',
                        'source': source_ip,
                        'description': f"Port scanning detected from {source_ip} ({len(unique_ports)} unique 'doors' probed)",
                        'indicators': list(unique_ports)[:5] # Show students a few of the ports found
                    })
        
        return detected_patterns

    @staticmethod
    def detect_dns_tunnels(event_list, link_list):
        """
        Looks for a common trick: asking a DNS question and then 
        immediately using the resolved IP to connect to a new server.
        
        Args:
            event_list (list): The forensic events found.
            link_list (list): The connections/relationships between events.
        """
        # Identify all DNS Query events by their ID
        dns_events = {event['id']: event for event in event_list if event['type'] == 'DNS Query'}
        detected_patterns = []
        
        # Step: Check if a DNS query led directly to another network activity
        for dns_id, dns_event in dns_events.items():
            query_domain = dns_event['details'].get('query', '')
            
            # Find all links where THIS DNS query was the starting point of an activity
            related_links = [link for link in link_list if link['source'] == dns_id]
            
            if related_links:
                detected_patterns.append({
                    'type': 'dns_to_connection',
                    'severity': 'MEDIUM',
                    'domain': query_domain,
                    'description': f"Possible DNS Tunnel or Payload: Query for {query_domain} was followed by a server connection.",
                    'dns_id': dns_id
                })
        
        return detected_patterns
