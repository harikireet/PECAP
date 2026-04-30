"""
PCAP StoryTeller - Main Application Entry Point
----------------------------------------------
This is the "Engine Room" of the backend. It starts the Flask web server, 
configures the upload rules, and registers all the API routes.
"""

from flask import Flask
from core.config import STATIC_FOLDER, TEMPLATE_FOLDER, UPLOAD_FOLDER
from api.routes import register_routes
from core.logger import logger
import sys
import os

# Ensure the 'backend' directory is in the path so we can find our packages
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

def create_application():
    """
    Factory function to create and configure the Flask web app.
    
    Returns:
        Flask: The configured application instance.
    """
    logger.info("=" * 60)
    logger.info("PCAP StoryTeller - Initializing Backend Web Server")
    logger.info("=" * 60)
    
    # 1. Initialize Flask with custom folder locations for HTML and Assets
    app = Flask(__name__, static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
    
    # 2. Configure for large forensic file uploads (1GB max limit)
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024  # 1 Gigabyte
    logger.info("Maximum upload size set to: 1GB")
    
    # 3. Set the directory where uploaded PCAPs are stored temporarily
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    logger.info(f"Temporary upload directory: {UPLOAD_FOLDER}")
    
    # 4. Disable browser caching for static files (helpful during development)
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    # 5. Register the API Routes (The "Web Doors" we defined in api/)
    register_routes(app)
    logger.info("API routes successfully registered.")
    
    return app

# The standard "starting point" for Python scripts
if __name__ == '__main__':
    # Initialize the app using our factory function above
    forensic_app = create_application()
    
    logger.info("Server is starting up at http://127.0.0.1:5000")
    
    # 6. Run the server! 
    # threaded=True allows it to handle multiple requests at once.
    # host='0.0.0.0' makes it accessible on your local network.
    forensic_app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5000, 
        threaded=True, 
        use_reloader=False
    )
