"""
PCAP StoryTeller - System Configuration
--------------------------------------
This module holds global settings like which file types are allowed 
and where specific folders are located on your computer.
"""

import os
import sys

# 1. File Upload Rules - We only want network capture formats
ALLOWED_EXTENSIONS = {'pcap', 'pcapng', 'cap'}

# 2. Path Setup: Find the absolute path to the 'backend' folder
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 3. Upload Folder: Where we save PCAPs for analysis
UPLOAD_FOLDER = os.path.join(ROOT_DIR, '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Create it if it doesn't exist yet

# 4. Frontend Paths: Tell Flask where to find the HTML and CSS
TEMPLATE_FOLDER = os.path.join(ROOT_DIR, '..', '..', 'frontend', 'templates')
STATIC_FOLDER = os.path.join(ROOT_DIR, '..', '..', 'frontend', 'static')

# 5. Dependency Check: Make sure the Scapy library is available for packet parsing
try:
    import scapy
    SCAPY_INSTALLED = True
except ImportError:
    SCAPY_INSTALLED = False
    print("❌ ERROR: Scapy is not installed! Run: pip install scapy", file=sys.stderr)
