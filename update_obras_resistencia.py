import geopandas as gpd
from ftplib import FTP
import os
import shutil

# Rutas de archivo
input_path = r"C:\Users\fpertile\OneDrive - FDN\Planos y mapas\Obras GeoResistencia multiline.geojson"
output_path = "Obras GeoResistencia.geojson"

# 1. Leer el archivo geopackage y filtrar elementos
# gdf = gpd.read_file(input_path)
# gdf_filtered = gdf[gdf['Obra'].notna()]  # Filtrar filas donde 'obra' no esté vacío

# 2. Convertir el resultado a GeoJSON y guardarlo en un archivo
# gdf_filtered.to_file(output_path, driver="GeoJSON")

shutil.copyfile(input_path, output_path)

# 3. Subir el archivo mediante FTP
ftp_host = os.getenv("FTP_GEORESIS_HOST")
ftp_user = os.getenv("FTP_USER")
ftp_pass = os.getenv("FTP_GEORESIS_PASSWORD")

with FTP(ftp_host) as ftp:
    ftp.login(user=ftp_user, passwd=ftp_pass)
    # Cambiar al directorio public_html
    print('Directorio actual en FTP:', ftp.pwd())
    print('Archivos en el directorio:')
    ftp.retrlines('LIST')
    with open(output_path, "rb") as file:
        ftp.storbinary("STOR /domains/georesistencia.com/public_html/Obras GeoResistencia.geojson", file)

print("Archivo subido exitosamente.")