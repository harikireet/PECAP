"""
PCAP StoryTeller - Protocol Experts (Handlers)
---------------------------------------------
This module contains the "Expert" logic for different network protocols.
When the main parser finds a packet, it sends it here to figure out 
exactly what is happening (DNS query, HTTP request, etc.).
"""

# Protocol Availability Checks:
# We attempt to import specialized Scapy layers. If they aren't installed on the 
# system, we gracefully disable those features instead of crashing.

HAS_HTTP = False
try:
    from scapy.layers.http import HTTPRequest, HTTPResponse
    HAS_HTTP = True
except ImportError:
    pass

HAS_TLS = False
try:
    from scapy.layers.tls.all import TLS, TLSClientHello
    HAS_TLS = True
except ImportError:
    pass

class ProtocolHandlers:
    """
    A collection of static methods, each acting as a forensic expert for a protocol.
    """

    @staticmethod
    def parse_dns(packet, parser, timestamp, source_ip, dest_ip):
        """
        Parses Domain Name System (DNS) packets.
        DNS is the "Phonebook" that turns names like google.com into IP addresses.
        """
        if packet.haslayer('DNS'):
            # 1. Handle DNS Queries (The Question: "Where is google.com?")
            if packet.haslayer('DNSQR') and not packet.haslayer('DNSRR'):
                query_name = packet['DNSQR'].qname.decode(errors='ignore').rstrip('.')
                event_id = parser._add_event(
                    'DNS Query', 
                    timestamp, source_ip, dest_ip, 
                    {'query': query_name}, 
                    f"DNS Question: What is the IP for {query_name}?"
                )
                # Store the query ID so we can link the response to it later
                parser.dns_map[query_name].append(event_id)
            
            # 2. Handle DNS Responses (The Answer: "google.com is at 1.2.3.4")
            elif packet.haslayer('DNSRR'):
                for i in range(packet['DNS'].ancount):
                    resource_record = packet['DNS'].an[i]
                    if resource_record.type == 1: # Type 1 is an 'A record' (IPv4 address)
                        domain_name = resource_record.rrname.decode(errors='ignore').rstrip('.')
                        resolved_ip = str(resource_record.rdata)
                        
                        event_id = parser._add_event(
                            'DNS Response', 
                            timestamp, source_ip, dest_ip, 
                            {'domain': domain_name, 'ip': resolved_ip}, 
                            f"DNS Answer: {domain_name} is at {resolved_ip}"
                        )
                        
                        # Use our map to connect this answer back to the original question
                        if domain_name in parser.dns_map:
                            for question_id in parser.dns_map[domain_name]:
                                parser._add_link(question_id, event_id, 'answers')

    @staticmethod
    def parse_http(packet, parser, timestamp, source_ip, dest_ip, flow_key):
        """
        Parses HyperText Transfer Protocol (HTTP) packets.
        HTTP is the standard language for unencrypted web browsers.
        """
        if HAS_HTTP and packet.haslayer('HTTPRequest'):
            http_layer = packet['HTTPRequest']
            method = http_layer.Method.decode(errors='ignore') if http_layer.Method else 'UNKNOWN'
            uri_path = http_layer.Path.decode(errors='ignore') if http_layer.Path else '/'
            
            event_id = parser._add_event(
                'HTTP Request', 
                timestamp, source_ip, dest_ip, 
                {'method': method, 'uri': uri_path}, 
                f"Web Request: {method} {uri_path}"
            )
            
            # Link the web request to the underlying TCP connection that is carrying it
            if flow_key in parser.flows: 
                parser._add_link(parser.flows[flow_key], event_id, 'carries')

    @staticmethod
    def parse_tls(packet, parser, timestamp, source_ip, dest_ip, flow_key):
        """
        Parses Transport Layer Security (TLS) packets.
        Used for encrypted (HTTPS) traffic. We can often find the website 
        name by looking for the 'SNI' (Server Name Indication) field.
        """
        if HAS_TLS and packet.haslayer('TLSClientHello'):
            try:
                # SNI is located inside the ClientHello extensions
                for extension in packet['TLSClientHello'].ext:
                    if extension.type == 0: # Type 0 is the SNI extension
                        server_name = extension.server_names[0].decode(errors='ignore')
                        
                        event_id = parser._add_event(
                            'TLS SNI', 
                            timestamp, source_ip, dest_ip, 
                            {'sni': server_name}, 
                            f"Encrypted Connection to: {server_name}"
                        )
                        
                        # Link this encrypted activity to its underlying TCP flow
                        if flow_key in parser.flows: 
                            parser._add_link(parser.flows[flow_key], event_id, 'carries')
            except Exception:
                pass # Silently skip malformed TLS packets

    @staticmethod
    def parse_icmp(packet, parser, timestamp, source_ip, dest_ip):
        """
        Parses Internet Control Message Protocol (ICMP).
        Mostly used for 'Pings' to see if a system is online.
        """
        if packet.haslayer('ICMP'):
            icmp_type = packet['ICMP'].type
            type_label = "Ping Request" if icmp_type == 8 else "Ping Reply" if icmp_type == 0 else f"Type {icmp_type}"
            
            parser._add_event(
                'ICMP', 
                timestamp, source_ip, dest_ip, 
                {'type': icmp_type}, 
                f"ICMP {type_label} Message"
            )
