import subprocess
import json
import os

def extract_gps_metadata(video_path):
    # Ejecutar ffprobe para extraer los metadatos del video
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-print_format', 'json', '-show_entries', 'frame_tags=location', video_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Parsear la salida JSON
    metadata = json.loads(result.stdout)

    # Extraer las coordenadas GPS
    gps_data = []
    for frame in metadata.get('frames', []):
        location = frame.get('tags', {}).get('location')
        if location:
            # Parsear la ubicación en formato "latitude,longitude,altitude"
            lat, lon, alt = map(float, location.split(','))
            gps_data.append((lat, lon, alt))

    return gps_data

# Ruta al archivo de video
video_path = os.path.abspath('fontana.mp4')
print(video_path)
# Extraer los datos GPS
gps_data = extract_gps_metadata(video_path)

# Mostrar los datos GPS
for lat, lon, alt in gps_data:
    print(f"Latitud: {lat}, Longitud: {lon}, Altitud: {alt}")