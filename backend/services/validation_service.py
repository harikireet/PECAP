"""
PCAP StoryTeller - Validation Service
------------------------------------
This module contains simple "Gatekeeper" functions that ensure 
the data coming into the system is in the correct format.
"""

class ValidationService:
    """
    A collection of static safety checks for the application.
    """
    
    @staticmethod
    def is_valid_pcap_extension(filename, accepted_extensions):
        """
        Ensures the uploaded file is actually a network capture file.
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in accepted_extensions
    
    @staticmethod
    def is_valid_port_number(port_candidate):
        """
        Checks if a number is a valid network port (between 0 and 65535).
        """
        try: 
            # Convert to integer and check the legal networking range
            port_integer = int(port_candidate)
            return 0 <= port_integer <= 65535
        except (ValueError, TypeError): 
            # If it's not a number at all, it's definitely not a valid port!
            return False
