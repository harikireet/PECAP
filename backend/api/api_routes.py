"""
PCAP StoryTeller - API Core Routes
---------------------------------
This module defines the "Web Doors" (Endpoints) that the frontend 
website uses to talk to the Python backend. Each route handles a 
specific request like "Analyze Threats" or "Get Analytics".
"""

import os
from flask import Blueprint, request, jsonify, send_from_directory
from core.logger import logger
from core.config import ALLOWED_EXTENSIONS
from data.data_manager import DataManager # brain
from services.services import (
    AnalyticsService, ThreatService, SearchService, 
    GeolocationService, FoliumMapService
)
from utils.file_handler import handle_file_upload
from services.report_generator import generate_pdf_report, generate_docx_report

# Create the Blueprint - this allows us to group our API routes together
api_bp = Blueprint('api', __name__)

@api_bp.route('/api/analytics')
def api_analytics():
    """
    Endpoint: /api/analytics
    Purpose: Provides statistical data (Top IPs, Protocols, Ports) for the Dashboard charts.
    """
    # 1. Load the analyzed findings from the JSON database
    analyzed_data = DataManager.load_findings()
    if not analyzed_data: 
        return jsonify({'error': 'No forensic data available.'}), 400
    
    # 2. Run the analytics engine on the stored events
    analytics_report = AnalyticsService.analyze_events(analyzed_data.get('events', []))
    return jsonify(analytics_report)

@api_bp.route('/api/threats')
def api_threats():
    """
    Endpoint: /api/threats
    Purpose: Evaluates security risks and detects attack patterns.
    """
    analyzed_data = DataManager.load_findings()
    if not analyzed_data: 
        return jsonify({'error': 'No forensic data available.'}), 400
    
    # Instantiate the Threat Service to scan for hacker patterns
    security_expert = ThreatService(analyzed_data.get('events', []), analyzed_data.get('links', []))
    
    # Perform the full security scan and return findings
    return jsonify(security_expert.perform_full_security_scan())

@api_bp.route('/api/search')
def api_search():
    """
    Endpoint: /api/search
    Purpose: Allows the user to filter the thousands of forensic events.
    """
    # Get parameters from the URL (e.g., ?q=192.168.1.1&field=ip)
    search_query = request.args.get('q', '')
    search_field = request.args.get('field', 'all')
    
    analyzed_data = DataManager.load_findings()
    if not analyzed_data: 
        return jsonify({'error': 'No forensic data available.'}), 400
    
    # Use the Search Service to filter the event list
    search_engine = SearchService(analyzed_data.get('events', []))
    filtered_results = search_engine.execute_search(search_query, search_field)
    
    return jsonify({
        'results': filtered_results, 
        'count': len(filtered_results)
    })

@api_bp.route('/api/geoip/<ip>')
def api_geoip(ip):
    """
    Endpoint: /api/geoip/<ip>
    Purpose: Converts a single IP address into a city and country.
    """
    geo_orchestrator = GeolocationService()
    return jsonify(geo_orchestrator.analyze_ip(ip))

@api_bp.route('/api/geoips')
def api_geoips():
    """
    Endpoint: /api/geoips
    Purpose: Locates every unique IP address found in the forensic capture.
    """
    analyzed_data = DataManager.load_findings()
    if not analyzed_data: 
        return jsonify({'error': 'No forensic data available.'}), 400
    
    # Extract unique IPs and run a batch geolocation lookup
    unique_ips = DataManager.extract_unique_ips(analyzed_data)
    geo_orchestrator = GeolocationService()
    return jsonify({'locations': geo_orchestrator.analyze_batch(unique_ips)})

@api_bp.route('/api/geomap')
def api_geomap():
    """
    Endpoint: /api/geomap
    Purpose: Generates the interactive HTML map showing traffic flow globally.
    """
    analyzed_data = DataManager.load_findings()
    if not analyzed_data: 
        return jsonify({'error': 'No forensic data available.'}), 400
    
    # 1. Get the Locations
    unique_ips = DataManager.extract_unique_ips(analyzed_data)
    geo_orchestrator = GeolocationService()
    location_list = geo_orchestrator.analyze_batch(unique_ips)
    
    # 2. Feed the locations into the Map service to get a Folium HTML map
    forensic_mapper = FoliumMapService()
    return forensic_mapper.generate_interactive_map(location_list)

@api_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Endpoint: /upload
    Purpose: Accepts a PCAP file from the user and starts the analysis process.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part found in request.'}), 400
    
    uploaded_pcap_file = request.files['file']
    
    # Delegate the heavy file handling to the utility module
    upload_result, status_code = handle_file_upload(uploaded_pcap_file, ALLOWED_EXTENSIONS)
    
    if status_code == 200:
        return jsonify(upload_result), 200
    return upload_result, status_code

@api_bp.route('/report/pdf')
def report_pdf():
    """
    Endpoint: /report/pdf
    Purpose: Triggers the generation of a professional forensic PDF report.
    """
    return generate_pdf_report()

@api_bp.route('/report/docx')
def report_docx():
    """
    Endpoint: /report/docx
    Purpose: Triggers the generation of a professional forensic Word (.docx) report.
    """
    return generate_docx_report()

@api_bp.route('/api/clear', methods=['POST'])
def clear_session():
    """
    Endpoint: /api/clear
    Purpose: Resets the "Brain" (DataManager) so a new investigation can start.
    """
    DataManager.clear_database()
    return jsonify({'status': 'Session forensic data cleared.'}), 200

@api_bp.route('/events.json')
def get_events():
    """
    Endpoint: /events.json
    Purpose: Provides direct access to the raw forensic output file.
    """
    data_directory = os.path.join(os.path.dirname(__file__), '..', 'data')
    return send_from_directory(data_directory, 'events.json')
