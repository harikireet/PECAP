"""
PCAP StoryTeller - Routes Registration

This module acts as the central point for registering all application routes
organized by Flask Blueprints.
"""

from api.page_routes import pages_bp # frontend
from api.api_routes import api_bp    # backend

def register_routes(app):
    """
    Register all application Blueprints with the Flask app instance.
    """
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp)
