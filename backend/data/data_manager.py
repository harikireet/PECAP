"""
PCAP StoryTeller - Forensic Data Manager
---------------------------------------
This is the "Brain" of the application. It handles the loading, 
saving, and clearing of analyzed findings in our 'events.json' 
database.
"""

import json
import os
from core.logger import logger

# Find the absolute path to where we store the analysis results
STORAGE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
FORENSIC_DATABASE_FILE = os.path.join(STORAGE_DIRECTORY, 'events.json')

class DataManager:
    """
    Manages the lifecycle of forensic records on the hard drive.
    """

    @staticmethod
    def load_findings():
        """
        Loads the forensic results from the storage file.
        
        Returns:
            dict: The analyzed data or None if no file exists.
        """
        # Step: Check if we have an existing database file
        if not os.path.exists(FORENSIC_DATABASE_FILE):
            logger.warning(f"Forensic database not found at: {FORENSIC_DATABASE_FILE}")
            return None
            
        try:
            with open(FORENSIC_DATABASE_FILE, 'r') as file_handle:
                analyzed_findings = json.load(file_handle)
            
            logger.info(f"Successfully loaded {len(analyzed_findings.get('events', []))} forensic events.")
            return analyzed_findings
        except Exception as error:
            logger.error(f"Failed to read forensic file: {error}")
            return None

    @staticmethod
    def save_findings(forensic_data_object):
        """
        Saves the analysis results to a JSON file so they persist 
        even if the server restarts.
        
        Args:
            forensic_data_object (dict): The data dictionary to save.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with open(FORENSIC_DATABASE_FILE, 'w') as file_handle:
                json.dump(forensic_data_object, file_handle, indent=2)
            
            logger.info("Forensic findings successfully saved to the 'Brain'.")
            return True
        except Exception as error:
            logger.error(f"Failed to save forensic data: {error}")
            return False

    @staticmethod
    def clear_database():
        """
        Wipes the database file to start a fresh investigation.
        """
        try:
            if os.path.exists(FORENSIC_DATABASE_FILE):
                os.remove(FORENSIC_DATABASE_FILE)
            logger.info("Forensic database cleared - Ready for new PCAP.")
            return True
        except Exception as error:
            logger.error(f"Failed to clear database: {error}")
            return False

    @staticmethod
    def extract_unique_ips(forensic_data):
        """
        Scans through all events to find every unique computer (IP) involved.
        
        Args:
            forensic_data (dict): The main data dictionary.
            
        Returns:
            set: A collection of unique IP address strings.
        """
        unique_ips = set()
        for event in forensic_data.get('events', []):
            # Check both the sender (source) and receiver (destination) IPs
            if event.get('source_ip'): 
                unique_ips.add(event['source_ip'])
            if event.get('dest_ip'): 
                unique_ips.add(event['dest_ip'])
        return unique_ips
