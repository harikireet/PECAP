"""
PCAP StoryTeller - Application Logging
-------------------------------------
Think of this as the "Black Box" of the application. It records 
everything that happens in the terminal and saves it to a file.
"""

import os
import logging
from datetime import datetime

def setup_application_logger():
    """
    Configures a professional logging system that outputs to both the 
    terminal (stdout) and a timestamped session file.
    
    Returns:
        logging.Logger: The configured logger instance.
    """
    # 1. Ensure the 'logs' folder exists in the project root
    logs_directory = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
    os.makedirs(logs_directory, exist_ok=True)
    
    # 2. Create the main logger object
    app_logger = logging.getLogger('StoryTeller')
    app_logger.setLevel(logging.DEBUG) # Catch every single detail
    
    # 3. Create a unique filename for this session (e.g., 2026-03-01_1430.log)
    session_file_name = datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"
    log_file_path = os.path.join(logs_directory, session_file_name)
    
    # 4. Define the Log Format: [Time] [Level] Message
    log_layout = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
    
    # 5. Handler A: Write full details (DEBUG level) to the Log File
    file_writer = logging.FileHandler(log_file_path)
    file_writer.setFormatter(log_layout)
    file_writer.setLevel(logging.DEBUG)
    
    # 6. Handler B: Write summary info (INFO level) to your Terminal Window
    terminal_writer = logging.StreamHandler()
    terminal_writer.setFormatter(log_layout)
    terminal_writer.setLevel(logging.INFO)
    
    # Register the handlers with the logger
    if not app_logger.handlers:
        app_logger.addHandler(file_writer)
        app_logger.addHandler(terminal_writer)
        
    app_logger.info(f"Logging initialized - Session file: {session_file_name}")
    return app_logger

# Automatically create the global 'logger' instance for the whole project
logger = setup_application_logger()
