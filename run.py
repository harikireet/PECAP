"""
PCAP StoryTeller - Main Entry Point
Convenience script to run the application from the root directory.
"""
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import create_application

if __name__ == '__main__':
    # Initialize our application using the factory function
    forensic_app = create_application()
    
    # Run the server at http://127.0.0.1:5000
    forensic_app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5000, 
        threaded=True, 
        use_reloader=False
    )
