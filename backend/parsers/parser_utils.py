"""
PCAP StoryTeller - Parser Utilities
-----------------------------------
This module provides small helper tools that help the main parser 
clean up data and track network conversations.
"""

import json

class EnhancedJSONEncoder(json.JSONEncoder):
    """
    A custom "Translator" for JSON. 
    By default, Python's JSON library doesn't know how to handle 'bytes' 
    (raw binary data). This class teaches it to convert bytes into 
    readable text/strings.
    """
    def default(self, object_to_encode):
        # Check if the data is in 'bytes' format
        if isinstance(object_to_encode, bytes):
            # Convert bytes to a UTF-8 string and ignore any messy characters
            return object_to_encode.decode('utf-8', errors='ignore')
        
        # Otherwise, use the standard JSON behavior
        return super().default(object_to_encode)

def get_flow_key(packet):
    """
    Generates a unique "ID CARD" for a network conversation (a Flow).
    
    In networking, a 'Flow' is uniquely identified by 4 pieces of info:
    1. Source IP Address
    2. Source Port Number
    3. Destination IP Address
    4. Destination Port Number
    
    Args:
        packet: The Scapy packet object to identify.
        
    Returns:
        tuple: A unique (SrcIP, SrcPort, DstIP, DstPort) key.
    """
    # Check if the packet has an IP layer (needed for IP addresses)
    if packet.haslayer('IP'):
        ip_layer = packet['IP']
        
        # We focus on tracking TCP (Transmission Control Protocol) conversations
        if packet.haslayer('TCP'):
            tcp_layer = packet['TCP']
            # Return the 4-tuple that identifies this specific 'conversation'
            return (ip_layer.src, tcp_layer.sport, ip_layer.dst, tcp_layer.dport)
            
    return None
