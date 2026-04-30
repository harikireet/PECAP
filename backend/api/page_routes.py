from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def index():
    """Home page with upload area and main dashboard."""
    return render_template('index.html')

@pages_bp.route('/timeline')
def timeline():
    """Timeline view of network events."""
    return render_template('timeline.html')

@pages_bp.route('/report')
def report():
    """Report generation and download page."""
    return render_template('report.html')

@pages_bp.route('/analytics')
def analytics():
    """Deep dive analytics and charts."""
    return render_template('analytics.html')

@pages_bp.route('/threats')
def threats():
    """Security threat analysis view."""
    return render_template('threats.html')

@pages_bp.route('/search')
def search_page():
    """Search interface for events."""
    return render_template('search.html')

@pages_bp.route('/geolocation')
def geolocation():
    """Map-based view of traffic sources."""
    return render_template('geolocation.html')
