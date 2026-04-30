"""
PCAP StoryTeller - Core Logic: Packet Parser
-------------------------------------------
This module is the heart of the backend. It uses the Scapy library to read 
raw network packets (.pcap files) and convert them into a structured "Story" 
of events and links that the frontend can display.
"""

import sys
import os
import json
from collections import defaultdict
from scapy.all import rdpcap
from parser_utils import EnhancedJSONEncoder, get_flow_key
from protocol_handlers import ProtocolHandlers

# path-discovery: Add the parent directory (backend) to the system path 
# so we can find sibling packages like 'data', 'core', and 'services'.
current_file_path = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.abspath(os.path.join(current_file_path, '..'))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

class PCAPParser:
    """
    Main parser class that handles the lifecycle of a PCAP analysis.
    It reads raw packets, runs them through protocol experts (Handlers), 
    and links related activities together for the StoryTeller.
    """
    def __init__(self, pcap_file):
        """
        Initializes the parser by loading the PCAP file into memory.
        
        Args:
            pcap_file (str): Absolute path to the .pcap file.
        """
        print(f"[*] Loading network capture: {pcap_file}")
        
        # rdpcap loads every packet from the file into an addressable list
        self.packets = rdpcap(pcap_file)
        
        # Final containers for our processed forensic data
        self.events = []
        self.links = []
        
        # State tracking for linking activities across the capture
        self.flows = {}        # Maps FlowKeys (IP/Port pairs) to Event IDs
        self.dns_map = defaultdict(list) # Connects DNS queries to the IP they resolved to
        self.event_counter = 1 # Ensures every forensic event has a unique ID
 
    def _add_event(self, event_type, timestamp, source, destination, details, description):
        """
        Saves a structured event to the dashboard's event list.
        
        Args:
            event_type (str): Category (e.g., DNS, TCP, HTTP)
            timestamp (float): UNIX timestamp from packet.time
            source (str): Source IP address
            destination (str): Destination IP address
            details (dict): Protocol-specific key-value pairs
            description (str): Human-readable summary for students
        """
        event = {
            'id': self.event_counter,
            'timestamp': float(timestamp),
            'type': event_type,
            'source_ip': source,
            'dest_ip': destination,
            'details': details,
            'description': description
        }
        self.events.append(event)
        self.event_counter += 1
        return event['id']

    def _add_link(self, source_id, target_id, label):
        """
        Draws an arrow (link) between two related events in the Story Graph.
        
        Args:
            source_id (int): ID of the starting event
            target_id (int): ID of the connected event
            label (str): Text explaining the relationship
        """
        self.links.append({
            'source': source_id, 
            'target': target_id, 
            'label': label
        })

    def parse(self):
        """
        The main analysis loop. We scan the packet list twice to build 
        a complete contextual story of the network activity.
        """
        
        # --- PASS 1: Identify TCP Connections (Conversations) ---
        # We look for the "SYN" flag which indicates a request to open a connection.
        for packet in self.packets:
            if packet.haslayer('TCP') and (packet['TCP'].flags & 0x02): # 0x02 is the SYN flag
                flow_key = get_flow_key(packet)
                
                # If we haven't tracked this specific conversation yet
                if flow_key and flow_key not in self.flows:
                    event_id = self._add_event(
                        'TCP Connection', 
                        packet.time, 
                        packet['IP'].src, 
                        packet['IP'].dst, 
                        {'sport': packet['TCP'].sport, 'dport': packet['TCP'].dport},
                        f"TCP Connection Started: {packet['IP'].src}:{packet['TCP'].sport} -> {packet['IP'].dst}:{packet['TCP'].dport}"
                    )
                    self.flows[flow_key] = event_id

        # --- PASS 2: Detailed Protocol Analysis ---
        # We search inside each packet for high-level data (DNS, HTTP, etc.)
        for packet in self.packets:
            if not packet.haslayer('IP'): 
                continue # Skip non-IP traffic like ARP/Spanning Tree
                
            timestamp = float(packet.time)
            source_ip = packet['IP'].src
            dest_ip = packet['IP'].dst
            flow_key = get_flow_key(packet)
            
            # Delegate parsing to specialized protocol experts (the Handlers)
            ProtocolHandlers.parse_dns(packet, self, timestamp, source_ip, dest_ip)
            ProtocolHandlers.parse_http(packet, self, timestamp, source_ip, dest_ip, flow_key)
            ProtocolHandlers.parse_tls(packet, self, timestamp, source_ip, dest_ip, flow_key)
            ProtocolHandlers.parse_icmp(packet, self, timestamp, source_ip, dest_ip)

        return self.events, self.links

def main(pcap_path):
    """
    Script entry point. Can be called manually for testing or as a backend process.
    """
    # Step: We import DataManager here (locally) to ensure 
    # the sys.path fix above has taken effect.
    from data.data_manager import DataManager
    
    # 1. Initialize and run the parser
    # Think of the 'parser' as an investigator reading a log of everything 
    # that happened on a network.
    parser = PCAPParser(pcap_path)
    forensic_events, story_links = parser.parse()
    
    # 2. Package the findings for the dashboard
    analysis_result = {
        'events': forensic_events, 
        'links': story_links,
        'metadata': {
            'file_name': os.path.basename(pcap_path),
            'extraction_date': __import__('datetime').datetime.now().isoformat()
        }
    }
    
    # 3. Save findings to the Data Manager ("Brain")
    # Using the DataManager ensures the results are saved correctly for the dashboard.
    if DataManager.save_findings(analysis_result):
        print(f"[+] Successfully extracted {len(forensic_events)} forensic events.")
        print(f"[*] Findings stored in the forensic database.")
    else:
        print("[!] Error: Failed to save forensic findings.")

if __name__ == '__main__':
    # Usage: python pcap_parser.py <path_to_file.pcap>
    if len(sys.argv) < 2:
        print("Error: Please provide a PCAP file path.")
    else:
        main(sys.argv[1])
