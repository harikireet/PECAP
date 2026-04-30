"""
PCAP StoryTeller - Map Generation Service
----------------------------------------
This service uses the Folium library to generate interactive 
OpenStreetMap maps with pins placed at the location of every IP.
"""

import folium
from folium import plugins

class FoliumMapService:
    """
    Expert service for drawing network forensic maps.
    """
    
    def generate_interactive_map(self, location_results):
        """
        Creates an HTML-based map with geographical markers.
        
        Args:
            location_results (list): List of dictionaries containing lat/lon.
            
        Returns:
            str: Raw HTML of the map for the frontend to render.
        """
        # 1. Filter out results that don't have geo-coordinates
        mapped_points = [loc for loc in location_results if loc.get('latitude') and loc.get('longitude')]
        
        # 2. Create the base Map (centered on the world)
        forensic_map = folium.Map(location=[20, 0], zoom_start=2, tiles='OpenStreetMap')
        
        # 3. Add a 'Marker Clusterer' - this groups close-together pins so the map stays clean
        marker_group = plugins.MarkerCluster().add_to(forensic_map)
        
        # 4. Step: Loop through every valid location and place a Pin/Marker
        for point in mapped_points:
            folium.Marker(
                location=[point['latitude'], point['longitude']],
                popup=f"<b>IP:</b> {point['ip']}<br><b>ISP:</b> {point['isp']}",
                tooltip=f"{point['ip']} - {point['city']}, {point['country']}"
            ).add_to(marker_group)
            
        # 5. Smart Zoom: If we have points, zoom the map to fit them perfectly
        if mapped_points:
            coordinates_list = [[point['latitude'], point['longitude']] for point in mapped_points]
            forensic_map.fit_bounds(coordinates_list)
            
        # 6. Return the map as a string of HTML for embedding
        return forensic_map._repr_html_()
