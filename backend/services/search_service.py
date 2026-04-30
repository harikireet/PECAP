"""
PCAP StoryTeller - Incident Search Service
-----------------------------------------
This service allows users to filter through thousands of network events 
to find specific indicators (like a suspicious IP or a specific domain).
"""

class SearchService:
    """
    Search engine that performs case-insensitive filtering across the forensic dataset.
    """
    def __init__(self, event_list):
        """
        Initializes with the full list of analyzed events.
        """
        self.event_list = event_list
    
    def execute_search(self, search_query, search_field='all'):
        """
        Filters the events based on the user's criteria.
        
        Args:
            search_query (str): The text or IP to look for.
            search_field (str): The category to search within (e.g., 'ip', 'domain', 'all').
            
        Returns:
            list: A subset of matching events.
        """
        search_query = search_query.lower()
        matching_results = []
        
        for event in self.event_list:
            is_match = False
            
            # Step: Determine if this event matches based on the selected field
            if search_field == 'all':
                # 'all' searches the entire event data converted to a string
                is_match = search_query in str(event).lower()
                
            elif search_field == 'ip':
                # Search only within source and destination IP addresses
                source_and_dest = (event.get('source_ip', '') + event.get('dest_ip', '')).lower()
                is_match = search_query in source_and_dest
                
            elif search_field == 'domain':
                # Search for DNS query names or TLS website names (SNI)
                details = event.get('details', {})
                domain_data = (details.get('query', '') + details.get('sni', '')).lower()
                is_match = search_query in domain_data
                
            elif search_field == 'type':
                # Search for the event category (e.g., 'DNS Query' or 'TCP Connection')
                is_match = search_query in event.get('type', '').lower()
                
            elif search_field == 'port':
                # Search for specific connection port numbers (sender and receiver)
                details = event.get('details', {})
                ports = (str(details.get('sport', '')) + str(details.get('dport', '')))
                is_match = search_query in ports
                
            # If we found a match, we include it in our final result list
            if is_match:
                matching_results.append(self._format_event_for_ui(event))
        
        return matching_results

    def _format_event_for_ui(self, event):
        """
        Internal cleaner that ensures the search result contains all UI fields.
        """
        return {
            'id': event['id'],
            'type': event.get('type'),
            'timestamp': event.get('timestamp'),
            'source_ip': event.get('source_ip'),
            'dest_ip': event.get('dest_ip'),
            'description': event.get('description'),
            'details': event.get('details', {})
        }
