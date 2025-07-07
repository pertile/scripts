import os
from PIL import Image

# it's not a good idea to work on svg files because it is vectorial and I am 
# working with raster images. I should convert the svg to png and then work with
# import cairosvg

from pyproj import Transformer
import subprocess
import gpxpy
from datetime import datetime, timedelta
import math
from moviepy.editor import VideoFileClip
import glob
import json


def get_video_metadata(video_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', video_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return json.loads(result.stdout)

def get_video_timestamps(video_path):
    metadata = get_video_metadata(video_path)
    print(video_path)
    creation_time_str = metadata['format']['tags'].get('creation_time')
    duration = float(metadata['format']['duration'])

    # creation time of video is when you finish recording, so is end timestamp
    if creation_time_str:
        end_timestamp = datetime.fromisoformat(creation_time_str.replace('Z', '+00:00'))

    start_timestamp = end_timestamp - timedelta(seconds=duration)
    return start_timestamp, end_timestamp

# Define file paths
CAR_SIZE = 200
FOLDER_PATH = r"c:\temp2"



image_path = glob.glob(os.path.join(FOLDER_PATH, "*.tiff"))
image_files = glob.glob(os.path.join(FOLDER_PATH, "*.tiff"))
if not image_files:
    raise FileNotFoundError("No se encontraron archivos TIFF en la carpeta especificada.")
image_path = max(image_files, key=os.path.getmtime)

filename = image_path.split("\\")[-1].split(".")[0]

gpx_files = glob.glob(os.path.join(FOLDER_PATH, "*.gpx"))
if not gpx_files:
    raise FileNotFoundError("No se encontraron archivos GPX en la carpeta especificada.")
gpx_path = max(gpx_files, key=os.path.getmtime)

mp4_path = os.path.join(FOLDER_PATH, filename + ".mp4")
if not os.path.exists(mp4_path):
    mp4_files = glob.glob(os.path.join(FOLDER_PATH, "*.mp4"))
    if mp4_files:
        latest_mp4 = max(mp4_files, key=os.path.getmtime)
        latest_mp4_name = os.path.basename(latest_mp4)
        if latest_mp4_name.startswith("VID_"):
            os.rename(latest_mp4, mp4_path)
        else:
            raise FileNotFoundError(f"El último archivo .mp4 debe llamarse {mp4_path} o comenzar con 'VID_'")
    else:
        raise FileNotFoundError("No se encontró ningún archivo MP4.")

print(f"Se iniciará el proceso con los siguientes archivos:\n{image_path}\n{gpx_path}\n{mp4_path}")
respuesta = input("¿Desea continuar? (s/n): ")
if respuesta.lower() != 's':
    print("Proceso cancelado por el usuario.")
    exit()

png_path = os.path.join(FOLDER_PATH, "coche.png")
gif_path = os.path.join(FOLDER_PATH, filename + ".gif")
tfw_path = os.path.join(FOLDER_PATH, filename + ".tfw")

start_timestamp, end_timestamp = get_video_timestamps(mp4_path)

# Open the georeferenced image
image = Image.open(image_path)

# Load the coordinates from the geojson file
with open(gpx_path) as f:
    gpx = gpxpy.parse(f)

# Get the points from the GPX file
points = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            if start_timestamp - timedelta(seconds=1) <= point.time <= end_timestamp + timedelta(seconds=1):
                points.append((point.latitude, point.longitude, point.time))

frames = []

INTERVAL = 4
coordinates = [points[0][:2]]
previous_time = points[0][2]
for pos, coord in enumerate(points):
    # print("coord[2]", coord[2], "previous_time", previous_time, "cálculo", (coord[2] - previous_time).seconds)
    if (coord[2] - previous_time).seconds >= INTERVAL:
        coordinates.append(coord[:2])
        previous_time = previous_time + timedelta(seconds=INTERVAL)

print("Total de puntos:", len(coordinates))
print(coordinates)

background = Image.new("RGBA", image.size)
background.paste(image)

# Now open the PNG image
car_image = Image.open(png_path)
car_image = car_image.resize((CAR_SIZE, CAR_SIZE))  # Resize the SVG image to 200x200 pixels

if car_image.mode in ('RGBA', 'LA') or (car_image.mode == 'P' and 'transparency' in car_image.info):
    # Use the alpha channel as the mask
    mask = car_image.split()[3]
else:
    # No transparency - use a solid mask
    mask = Image.new("L", car_image.size, 255)

# Create a transformer
transformer = Transformer.from_crs("EPSG:4326", "EPSG:5347", always_xy=True)

# Read the TFW file
with open(tfw_path, 'r') as f:
    lines = f.readlines()

# Get the rotation values
rotation_x = float(lines[2])
rotation_y = float(lines[3])

# Calculate the angle in radians
angle_radians = math.atan2(rotation_y, rotation_x)

# Convert the angle to degrees
# add 180 because result is -135 and it should be 45
image_rotation = math.degrees(angle_radians) + 180
print("image rotation", image_rotation)

previous_angle = 0
angle_degrees = 0
for pos, coord in enumerate(coordinates):
    # Create a new image with the same size as the georeferenced image

    # Transform the coordinates
    x, y = transformer.transform(coord[1], coord[0])
    if pos < len(coordinates) - 1:
        next_x, next_y = transformer.transform(coordinates[pos + 1][1], coordinates[pos + 1][0])
        # Calculate the difference between the coordinates
        dx = next_x - x
        dy = next_y - y

        # Calculate the angle in radians
        angle_radians = math.atan2(dy, dx)

        # Convert the angle to degrees
        angle_degrees = math.degrees(angle_radians)
    else:
        angle_degrees = previous_angle

    
    # print("coord[0], coord[1]", coord[0], coord[1])
    # print("Coordenadas en metros:", x, y)

    command = ['gdaltransform', image_path, '-i']
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    output, _ = process.communicate(input=f'{x} {y}\n'.encode())
    output = output.decode().strip()
    col, row, _ = output.split()
    col = round(float(col)) - CAR_SIZE * 0.67
    row = round(float(row)) - CAR_SIZE * 0.67

    # print("el siguiente valor debaría ser 3000,500")
    print("Coordenadas transformadas:", col, row)
    
    # TODO: por la rotación a 45° primero tengo que sumar 45° al ángulo de rotación
    # de esta manera un ángulo de 315° (9 de Julio sentido ascendente) se convierte en 0°
    # y un ángulo de 135° (25 de Mayo sentido ascendente) se convierta en 180°
    # si el ángulo está entre 90 y 270 grados, el coche debería estar volteado verticalmente antes de hacer la rotación

    frame = background.copy()
    rotation_angle = angle_degrees + image_rotation
    rotated_car = car_image
    if rotation_angle > 90 and rotation_angle < 270:
        rotated_car = rotated_car.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    rotated_car = rotated_car.rotate(rotation_angle, expand=True)
    # print("angle_degrees", angle_degrees, "image_rotation", image_rotation, "calc", angle_degrees + image_rotation + 180)   
    rotated_mask =rotated_car.convert('RGBA').split()[3]
    frame.paste(rotated_car, (int(col), int(row)), rotated_mask)

    frames.append(frame)
    temp = car_image.copy()
    previous_angle = angle_degrees


# Crear el video directamente desde los frames usando MoviePy

import numpy as np
from moviepy.editor import ImageSequenceClip
output_mp4 = os.path.join(FOLDER_PATH, f"{filename}_esquema.mp4")
clip = ImageSequenceClip([np.array(frame.convert('RGB')) for frame in frames], fps=1/INTERVAL)
clip.write_videofile(output_mp4, codec='libx264')

new_mp4_path = os.path.join(FOLDER_PATH, filename + ".mp4")
os.rename(mp4_path, new_mp4_path)
new_gpx_path = os.path.join(FOLDER_PATH, filename + ".gpx")
os.rename(gpx_path, new_gpx_path)
