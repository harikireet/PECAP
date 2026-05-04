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

    # Render (and most PaaS hosts) inject the listening port via the PORT env var.
    # Fall back to 5000 for local development.
    port = int(os.environ.get('PORT', 5000))

    # Disable debug mode in production (when PORT is set by the host).
    is_production = 'PORT' in os.environ

    forensic_app.run(
        debug=not is_production,
        host='0.0.0.0',
        port=port,
        threaded=True,
        use_reloader=False
    )
