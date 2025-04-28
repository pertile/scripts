import geopandas as gpd
from ftplib import FTP
import os

# Rutas de archivo
input_path = r"C:\Users\fpertile\OneDrive - FDN\Planos y mapas\highway Resistencia new.gpkg"
output_path = r"C:\Users\fpertile\OneDrive - FDN\Planos y mapas\Obras Resistencia.json"

# 1. Leer el archivo geopackage y filtrar elementos
gdf = gpd.read_file(input_path)
gdf_filtered = gdf[gdf['Obra'].notna()]  # Filtrar filas donde 'obra' no esté vacío

# 2. Convertir el resultado a GeoJSON y guardarlo en un archivo
gdf_filtered.to_file(output_path, driver="GeoJSON")

# 3. Subir el archivo mediante FTP
ftp_host = os.getenv("FTP_REP_HOST")
ftp_user = "fpertile@georesistencia.com"
ftp_pass = os.getenv("FTP_REP_PASSWORD")

with FTP(ftp_host) as ftp:
    ftp.login(user=ftp_user, passwd=ftp_pass)
    with open(output_path, "rb") as file:
        ftp.storbinary("STOR Obras GeoResistencia.geojson", file)

print("Archivo subido exitosamente.")