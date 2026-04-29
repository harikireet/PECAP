# 06 | 🗺️ Geolocation & Mapping

Where in the world is the traffic coming from? This service finds the physical coordinates of every IP address.

---

## 🌍 The Dual-API Strategy
Because some free APIs have limits, we use two different sources to find the location:
1.  **ipinfo.io**: Our primary source.
2.  **ip-api.com**: Our backup source.

---

## 🗺️ How the Map is Built
We use a library called **Folium** (which uses Leaflet.js) to generate a beautiful interactive map.

```mermaid
graph TD
    A[Unique IP Address] --> B{Check Cache?}
    B -- "Yes" --> C[Return Coordinates]
    B -- "No" --> D[Call Geo-API]
    D --> E[Save to Cache]
    E --> C
    C --> F[Folium Map Marker]
    F --> G[HTML Map Export]
```

---

## 📂 Key Files
- `backend/services/geoip_scanner.py`: Handles the actual API calls and caching.
- `backend/services/geolocation_service.py`: Orchestrates lookups for multiple IPs.
- `backend/services/map_service.py`: The Folium logic for drawing the interactive map.
