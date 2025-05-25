from datetime import datetime
import math
import pyperclip
import re
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
import json

class Project:
    def __init__(self, id, name, color=None, lat=None, long=None):
        self.id = id
        self.name = name
        self.color = color
        self.lat = lat
        self.long = long

    def __repr__(self):
        return f"Project(id={self.id}, name={self.name}, color={self.color}, lat={self.lat}, long={self.long})"

def extract_coordinates(features):
    coordinates = []
    print(features)
    for feature in features:
        if feature["geometry"]["type"] == "Point":
            coordinates.append(feature["geometry"]["coordinates"])
        elif feature["geometry"]["type"] in ["LineString", "Polygon"]:
            coordinates.extend(feature["geometry"]["coordinates"])
        elif feature["geometry"]["type"] == "MultiPolygon":
            for polygon in feature["geometry"]["coordinates"]:
                coordinates.extend(polygon)

    # Calcular el centro de las coordenadas
    if coordinates:
        avg_x = sum(coord[0] for coord in coordinates) / len(coordinates)
        avg_y = sum(coord[1] for coord in coordinates) / len(coordinates)
    return avg_y, avg_x

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
GEOJSON_FILE= r"C:\Users\fpertile\OneDrive - FDN\Planos y mapas\viable.geojson"

# Descargar y cargar el archivo GeoJSON
with open(GEOJSON_FILE, "r", encoding="utf-8") as file:
    geojson_data = json.load(file)

# Extraer los valores del atributo "Obra"
obras = [feature["properties"]["Clave"] for feature in geojson_data["features"] if feature["properties"]["Clave"] is not None]
# print(obras)

# Crear un WordCompleter con las obras
obras_completer = WordCompleter(obras)

# Configurar los key bindings para el autocompletado
bindings = KeyBindings()

COLORS = ['#ff0000', '#008000', '#B695C0']
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
obra_seleccionada = prompt("Ingrese la clave de la obra: ", completer=obras_completer)

name_js = to_js_variable(obra_seleccionada)

# Filtrar las features que tienen el valor de "Obra" seleccionado
selected_features = [feature for feature in geojson_data["features"] if feature["properties"]["Clave"] == obra_seleccionada]


# Extraer las coordenadas de las features seleccionadas
lat, long = extract_coordinates(selected_features)

projects = []
feature = selected_features[0]
projects.append(Project(id=obra_seleccionada, name=feature['properties']['Nombre'], lat=lat, long=long))

zoom = "10"

obra = f"'{obra_seleccionada}'"

# Calcular las distancias desde el centro a cada obra
distances = {}
for feature in geojson_data["features"]:
    obra_name = feature["properties"]["Clave"]
    if feature["geometry"]["type"] == "Point":
        f_lon, f_lat = feature["geometry"]["coordinates"]
        distance = haversine(lat, long, f_lon, f_lat)
    elif feature["geometry"]["type"] == "LineString":
        min_distance = float('inf')
        for f_lon, f_lat in feature["geometry"]["coordinates"]:
            distance = haversine(lat, long, f_lon, f_lat)
            if distance < min_distance:
                min_distance = distance
    
    # Solo almacenar la distancia mínima para cada obra
    if obra_name not in distances or distance < distances[obra_name] and obra_name != obra_seleccionada:
        distances[obra_name] = distance

# Convertir el diccionario a una lista de tuplas y ordenar por distancia
sorted_distances = sorted(distances.items(), key=lambda x: x[1])
closest_obras = sorted_distances[:10]

# Mostrar las 10 obras más cercanas con índices
print("Las 10 obras más cercanas al centro son:")
for i, (obra_name, distance) in enumerate(closest_obras):
    print(f"{i + 1}. {obra_name}: {distance:.2f} km")

# Permitir al usuario seleccionar una o más obras por índice
print("Ingrese las claves de otras obras, separados por comas:")
selected_keys = input()
otras = ""
if selected_keys != "":
    selected_keys = selected_keys.split(",")
    for key in selected_keys:
        features = [feature for feature in geojson_data["features"] if feature["properties"]["Clave"] == key]
        lat, long = extract_coordinates(features)
        feature = features[0]
        projects.append(Project(id=feature['properties']["Clave"], name=feature['properties']["Nombre"], lat=lat, long=long))

for i, project in enumerate(projects):
    projects[i].color = COLORS[i % len(COLORS)]

print("PROJECTS", projects)
lines = [project.__dict__ for project in projects]
lines_str = ", ".join([json.dumps(line) for line in lines])
# Calcular el centro de todas las coordenadas dentro de projects
if projects:
    avg_lat = sum(project.lat for project in projects) / len(projects)
    avg_long = sum(project.long for project in projects) / len(projects)
    lat = avg_lat
    long = avg_long

# const lines = [
#     { id: 'A27', name: 'RN51 - Salar de Pocitos', color: '#ff0000' },
#     { id: 'A27-2', name: 'Salar de Pocitos - Los Colorados', color: '#008000' },
#     { id: 'A27-3', name: 'Los Colorados - Tolar Grande', color: '#B695C0' },
# ]

with open("viable-mapbox.txt") as file:
    content = file.read()
    content = content.replace("<NOMBRE>", name_js)
    content = content.replace("<LAT>", str(lat))
    content = content.replace("<LONG>", str(long))
    content = content.replace("<ZOOM>", str(zoom))
    content = content.replace("<OBRA>", obra)
    content = content.replace("<OBRAS>", lines_str)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    pyperclip.copy(content)
    print("****")
    print("¡SE COPIÓ EL CONTENIDO AL PORTAPAPELES!")
    with open(f"c:\\viable\\{obra_seleccionada}.js", "w", encoding="utf-8") as new_file:
        new_file.write(content)
        print(f"¡Se generó el archivo c:\\temp2\\{obra_seleccionada}.js")
