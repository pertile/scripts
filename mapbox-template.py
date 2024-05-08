from datetime import datetime
import math
import pyperclip

print(
    "Ingrese nombre mapa (sin espacios ni caracteres raros, y que no empiece por un número):"
)
name = input()
print(
    "Ingrese la URL del mapa centrado ej. https://openstreetmap.org.ar/#12.83/-27.44896/-58.98099/45:"
)
print(
    "https://api.mapbox.com/styles/v1/mapbox/streets-v12.html?title=true&access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4M29iazA2Z2gycXA4N2pmbDZmangifQ.-g_vE53SD2WrJ6tFX7QHmA#14.7/-27.48362/-58.94215/45"
)
coord = input().split("/")
lat = coord[-3]
long = coord[-2]
zoom = math.trunc(float(coord[-4].split("#")[1]))
print(
    "Ingrese obra como aparece en http://georesistencia.com/Obras%20GeoResistencia.geojson:"
)
obra_sin_comilla = input()
obra = f"'{obra_sin_comilla}'"
print("Ingrese otras obras separadas por coma:")
otras = input()
otras = ",".join([f"'{x.strip()}'" for x in otras.split(",")])

all = obra

if otras == "":
    otras = "''"
else:
    all = f"{obra}, {otras}"
with open("mapbox-template.txt") as file:
    content = file.read()
    content = content.replace("<NOMBRE>", name)
    content = content.replace("<LAT>", lat)
    content = content.replace("<LONG>", long)
    content = content.replace("<ZOOM>", str(zoom))
    content = content.replace("<OBRA>", obra)
    content = content.replace("<OTRAS OBRAS>", otras)
    content = content.replace("<TODAS>", all)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    pyperclip.copy(content)
    print("****")
    print("¡SE COPIÓ EL CONTENIDO AL PORTAPAPELES!")
    with open(f"c:\\temp2\\{obra_sin_comilla}.js", "w", encoding="utf-8") as new_file:
        new_file.write(content)
        print(f"¡Se generó el archivo c:\\temp2\\{obra_sin_comilla}.js")
