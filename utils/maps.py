import requests
import folium
import polyline
from typing import List, Tuple, Optional
from branca.element import MacroElement
from jinja2 import Template

# Local imports
from utils.travel_utils import COUNTRY_CURRENCY_MAP
COUNTRIES = list(COUNTRY_CURRENCY_MAP.keys())

def get_coordinates(place_name: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Fetches latitude and longitude for a given place name using Nominatim (OSM).
    Returns (None, None) if not found.
    """
    url = "https://nominatim.openstreetmap.org/search"
    headers = {'User-Agent': 'TravelPlanner/1.0'}
    params = {'q': place_name, 'format': 'json', 'limit': 1}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print(f"Geocoding error for {place_name}: {e}")
        
    return None, None

def get_osrm_route(coordinates: List[Tuple[float, float]]):
    """
    Fetches driving route from OSRM demo server.
    
    Args:
        coordinates: list of (lat, lon) tuples.
        
    Returns: 
        (decoded_geometry, distance_in_meters, duration_in_seconds)
    """
    if not coordinates or len(coordinates) < 2:
        return None, 0, 0

    # OSRM expects lon,lat;lon,lat
    coord_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
    url = f"http://router.project-osrm.org/route/v1/driving/{coord_str}?overview=full"
    
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None, 0, 0
            
        data = r.json()
        if data.get("code") == "Ok":
            route = data["routes"][0]
            # OSRM returns encoded polyline (google format)
            decoded = polyline.decode(route["geometry"])
            return decoded, route["distance"], route["duration"]
            
    except Exception as e:
        print(f"OSRM Routing Error: {e}")
        
    return None, 0, 0

class ZoomControl(MacroElement):
    """
    Custom Folium Control to display current zoom level on the map.
    Uses Javascript and Leaflet hooks.
    """
    _template = Template("""
        {% macro script(this, kwargs) %}
            L.Control.ZoomDisplay = L.Control.extend({
                onAdd: function(map) {
                    var div = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
                    div.style.backgroundColor = 'white';
                    div.style.padding = '5px 10px';
                    div.style.fontSize = '14px';
                    div.style.fontWeight = 'bold';
                    div.style.border = '2px solid rgba(0,0,0,0.2)';
                    div.style.borderRadius = '4px';
                    div.style.cursor = 'default';
                    
                    var updateZoom = function() {
                        var z = map.getZoom();
                        var p = Math.round((z / 7) * 37);
                        div.innerHTML = 'Zoom ' + p + '%';
                    };
                    
                    updateZoom();
                    map.on('zoomend', updateZoom);
                    return div;
                }
            });
            new L.Control.ZoomDisplay({ position: 'topleft' }).addTo({{this._parent.get_name()}});
        {% endmacro %}
    """)

def create_map(city_name: str, locations: List[str] = None) -> folium.Map:
    """
    Creates a Folium map centered on the destination or specific locations.
    Adds markers, a route line, and a custom info box with stats.
    """
    # 1. Resolve Locations First to determine center
    valid_locations = []
    if locations:
        for loc in locations:
            lat, lon = get_coordinates(loc)
            if lat is not None and lon is not None:
                valid_locations.append({"name": loc, "lat": lat, "lon": lon})

    # 2. Determine Map Center
    if valid_locations:
        # Center on the first location initially
        center_lat = valid_locations[0]["lat"]
        center_lon = valid_locations[0]["lon"]
        initial_zoom = 4 # City level close-up
    else:
        # Fallback to City/Country center
        center_lat, center_lon = get_coordinates(city_name)
        if not center_lat:
            # Absolute fallback (Null Islandish)
            center_lat, center_lon = 20.0, 0.0 
        
        # Fallback zoom for city-level or country-level view
    initial_zoom = 4  # << FIX
        # Check if it's a known country to adjust zoom
        

    m = folium.Map(location=[center_lat, center_lon], zoom_start=initial_zoom, tiles="OpenStreetMap")

    # 3. Add Markers
    coords_list = []
    for i, item in enumerate(valid_locations):
        coords_list.append((item["lat"], item["lon"]))
        
        # Add a nice marker
        folium.Marker(
            [item["lat"], item["lon"]],
            popup=item["name"],
            tooltip=f"{i+1}. {item['name']}",
            icon=folium.Icon(color="red", icon=str(i+1), prefix="fa")
        ).add_to(m)

    # 4. Draw Route & Add Stats
    if len(coords_list) > 1:
        route_geom, dist_meters, duration_sec = get_osrm_route(coords_list)
        
        if route_geom:
            folium.PolyLine(
                route_geom,
                color="blue",
                weight=5,
                opacity=0.7
            ).add_to(m)
            
            # Info Box (Floating overlay)
            dist_km = dist_meters / 1000
            hours = int(duration_sec // 3600)
            mins = int((duration_sec % 3600) // 60)
            
            info_html = f"""
            <div style="position: fixed; 
                        top: 20px; right: 20px; width: 250px; height: auto; 
                        background-color: rgba(255, 255, 255, 0.95); 
                        border: 1px solid #ddd; 
                        z-index:9999; 
                        font-size:14px;
                        font-family: 'Segoe UI', sans-serif;
                        padding: 15px; 
                        border-radius: 8px; 
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="margin-bottom: 5px;"><strong>🚗 Trip Stats</strong></div>
                <div><b>Distance:</b> {dist_km:.1f} km</div>
                <div><b>Est. Time:</b> {hours}h {mins}m</div>
            </div>
            """
            m.get_root().html.add_child(folium.Element(info_html))
            
        # Smart bounds fitting
        m.fit_bounds(coords_list, padding=(50, 50))

    elif not valid_locations:
        # Fallback Marker just to show we found the city
        folium.Marker(
            [center_lat, center_lon],
            popup=city_name,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    # Add custom controls
    m.add_child(ZoomControl())
    
    return m
