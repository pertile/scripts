from datetime import datetime
import math
import pyperclip
import re
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
import json

def to_js_variable(text):
    # Reemplazar caracteres no permitidos por guiones bajos
    text = re.sub(r'\W|^(?=\d)', '_', text)
    
    # Asegurarse de que no sea una palabra reservada
    reserved_words = {
        "abstract", "await", "boolean", "break", "byte", "case", "catch", "char", "class", "const",
        "continue", "debugger", "default", "delete", "do", "double", "else", "enum", "export", "extends",
        "false", "final", "finally", "float", "for", "function", "goto", "if", "implements", "import",
        "in", "instanceof", "int", "interface", "let", "long", "native", "new", "null", "package",
        "private", "protected", "public", "return", "short", "static", "super", "switch", "synchronized",
        "this", "throw", "throws", "transient", "true", "try", "typeof", "var", "void", "volatile", "while", "with", "yield"
    }
    
    if text in reserved_words:
        text = f"_{text}"
    
    return text

# Calcular la distancia entre dos puntos (lat, lon) usando la fórmula de Haversine
def haversine(lon1, lat1, lon2, lat2):
    R = 6371  # Radio de la Tierra en kilómetros
    dlon = math.radians(lon2 - lon1)
    dlat = math.radians(lat2 - lat1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

# URL del archivo GeoJSON
GEOJSON_FILE= "Obras GeoResistencia.geojson"

# Descargar y cargar el archivo GeoJSON
with open(GEOJSON_FILE, "r", encoding="utf-8") as file:
    geojson_data = json.load(file)

# Extraer los valores del atributo "Obra"
obras = [feature["properties"]["Obra"] for feature in geojson_data["features"]]

# Crear un WordCompleter con las obras
obras_completer = WordCompleter(obras, ignore_case=True, match_middle=True, sentence=True)

# Configurar los key bindings para el autocompletado
bindings = KeyBindings()

@bindings.add('tab')
@bindings.add('enter')
def _(event):
    buffer = event.app.current_buffer
    document = buffer.document
    completions = list(buffer.completer.get_completions(document, event.app))
    if completions:
        buffer.delete_before_cursor(len(document.text_before_cursor))
        buffer.insert_text(completions[0].text)
        event.app.exit(result=completions[0].text)

# Preguntar por consola el ingreso del contenido del atributo "Obra" con autocompletado
obra_seleccionada = prompt("Ingrese el nombre de la obra: ", completer=obras_completer, key_bindings=bindings)

name_js = to_js_variable(obra_seleccionada)

# Filtrar las features que tienen el valor de "Obra" seleccionado
selected_features = [feature for feature in geojson_data["features"] if feature["properties"]["Obra"] == obra_seleccionada]

# Extraer las coordenadas de las features seleccionadas
coordinates = []

for feature in selected_features:
    print(feature['geometry']['type'])
    if feature["geometry"]["type"] == "Point":
        coordinates.append(feature["geometry"]["coordinates"])
    elif feature["geometry"]["type"] in ["LineString", "Polygon"]:
        coordinates.extend(feature["geometry"]["coordinates"])
    elif feature["geometry"]["type"] in ["MultiPolygon", "MultiLineString"]:
        for polygon in feature["geometry"]["coordinates"]:
            coordinates.extend(polygon)

center = []
# Calcular el centro de las coordenadas
if coordinates:
    avg_x = sum(coord[0] for coord in coordinates) / len(coordinates)
    avg_y = sum(coord[1] for coord in coordinates) / len(coordinates)
    center = [avg_x, avg_y]
else:
    print("No se encontraron coordenadas para la obra seleccionada.")
    exit
print("center es", center)
osm_url = f"https://api.mapbox.com/styles/v1/mapbox/streets-v12.html?title=true&access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4M29iazA2Z2gycXA4N2pmbDZmangifQ.-g_vE53SD2WrJ6tFX7QHmA#15/{center[1]}/{center[0]}/45"


coord = osm_url.split("/")

lat = center[1]
long = center[0]
zoom = "15"

obra = f"'{obra_seleccionada}'"

# Calcular las distancias desde el centro a cada obra
distances = {}
for feature in geojson_data["features"]:
    obra_name = feature["properties"]["Obra"]
    geom_type = feature["geometry"]["type"]
    coords = feature["geometry"]["coordinates"]
    distance = None
    if geom_type == "Point":
        f_lon, f_lat = coords
        distance = haversine(center[0], center[1], f_lon, f_lat)
    elif geom_type == "LineString":
        distance = min(haversine(center[0], center[1], f_lon, f_lat) for f_lon, f_lat in coords)
    elif geom_type == "MultiLineString":
        # MultiLineString: lista de listas de coordenadas
        distance = min(
            haversine(center[0], center[1], f_lon, f_lat)
            for line in coords for f_lon, f_lat in line
        )
    # Solo almacenar la distancia si no es la obra seleccionada
    if obra_name != obra_seleccionada:
        distances[obra_name] = distance

# Convertir el diccionario a una lista de tuplas y ordenar por distancia
sorted_distances = sorted(distances.items(), key=lambda x: x[1])
closest_obras = sorted_distances[:10]

# Mostrar las 10 obras más cercanas con índices
print("Las 10 obras más cercanas al centro son:")
for i, (obra_name, distance) in enumerate(closest_obras):
    print(f"{i + 1}. {obra_name}: {distance:.2f} km")

# Permitir al usuario seleccionar una o más obras por índice
print("Ingrese los números de otras obras relacionadas, separados por comas:")
selected_indices = input()
otras = ""
if selected_indices != "":
    selected_indices = [int(index.strip()) - 1 for index in selected_indices.split(",")]

    # Guardar las obras seleccionadas en una variable
    otras = [f"'{closest_obras[index][0]}'" for index in selected_indices]

    otras = ",".join(otras)

all = obra

if otras == "":
    otras = "''"
else:
    all = f"{obra}, {otras}"


with open("mapbox-template.txt") as file:
    content = file.read()
    content = content.replace("<NOMBRE>", name_js)
    content = content.replace("<LAT>", str(lat))
    content = content.replace("<LONG>", str(long))
    content = content.replace("<ZOOM>", str(zoom))
    content = content.replace("<OBRA>", obra)
    content = content.replace("<OTRAS OBRAS>", otras)
    content = content.replace("<TODAS>", all)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    pyperclip.copy(content)
    print("****")
    print("¡SE COPIÓ EL CONTENIDO AL PORTAPAPELES!")
    with open(f"c:\\temp\\{obra_seleccionada}.js", "w", encoding="utf-8") as new_file:
        new_file.write(content)
        print(f"¡Se generó el archivo c:\\temp2\\{obra_seleccionada}.js")
