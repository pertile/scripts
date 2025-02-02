import requests
import json
import subprocess

# Define the Overpass API endpoint and query
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json];
relation["network"~"^AR"]->.searchRelations;
way(r.searchRelations)(-55,-73.5,-21,-53.5);
out geom; 
"""

# Send the request to the Overpass API
response = requests.get(overpass_url, params={'data': overpass_query})
data = response.json()

# Save the GeoJSON to a file
json_path = r'c:\temp\rutas_argentina.json'
with open(json_path, 'w') as f:
    json.dump(data, f)

# Load the JSON data from the file
# json_path = r'c:\temp\rutas_argentina.json'
# with open(json_path, 'r') as f:
#     data = json.load(f)

# Convert the Overpass JSON response to GeoJSON format
features = []
for element in data['elements']:
    if 'geometry' in element:
        coordinates = [(point['lon'], point['lat']) for point in element['geometry']]
        if element['type'] == 'way':
            geometry = {
                "type": "LineString",
                "coordinates": coordinates
            }


        # Filter tags to include only ref, surface, and motorroad
        tags = element.get('tags', {})
        properties = {key: tags.get(key) for key in ['ref', 'surface', 'motorroad', 'highway']}
        highway = tags.get('highway')
        is_proposal = False
        if highway and highway == 'proposal':
            is_proposal = True
        if properties and not is_proposal:
            features.append({
                "type": "Feature",
                "geometry": geometry,
                "properties": properties
            })

geojson = {
    "type": "FeatureCollection",
    "features": features
}

# Save the GeoJSON to a file
geojson_path = r'c:\temp\rutas_argentina.geojson'
with open(geojson_path, 'w') as f:
    json.dump(geojson, f)



# Convert the GeoJSON file to GPKG using ogr2ogr
gpkg_path = r'C:\Users\fpertile\OneDrive - FDN\Planos y mapas\rutas_argentina.gpkg'
ogr2ogr_path = r'C:\Program Files\QGIS 3.36.0\bin\ogr2ogr'

subprocess.run([ogr2ogr_path, '-f', 'GeoJSON', '-F', 'GPKG', gpkg_path, geojson_path])