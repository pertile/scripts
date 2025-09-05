"""
Script para convertir obras individuales a MultiLineString en QGIS
Agrupa las líneas por obra y crea una geometría MultiLineString por cada obra única
"""

from qgis.core import *
from qgis.utils import iface
import processing

def convertir_obras_a_multiline():
    """
    Convierte las obras de líneas individuales a MultiLineString
    """
    # Obtener la capa activa
    layer = iface.activeLayer()
    
    if not layer:
        print("No hay capa activa seleccionada")
        return
    
    if layer.geometryType() != QgsWkbTypes.LineGeometry:
        print("La capa debe contener geometrías de línea")
        return
    
    # Campos que identifican una obra única (ajustar según tus datos)
    # Puedes usar combinaciones como: title + TipoObra, o un ID único si lo tienes
    campos_identificadores = ['title', 'TipoObra']  # Ajustar según tus campos
    
    # Diccionario para agrupar geometrías por obra
    obras_agrupadas = {}
    
    # Procesar cada feature
    for feature in layer.getFeatures():
        # Crear clave única para la obra
        clave_obra = ""
        for campo in campos_identificadores:
            valor = feature[campo] if feature[campo] else ""
            clave_obra += str(valor) + "_"
        
        clave_obra = clave_obra.rstrip("_")
        
        if clave_obra not in obras_agrupadas:
            # Crear diccionario de propiedades correctamente
            propiedades = {}
            for i, field in enumerate(feature.fields()):
                propiedades[field.name()] = feature.attributes()[i]
            
            obras_agrupadas[clave_obra] = {
                'geometrias': [],
                'propiedades': propiedades,
                'campos': [field.name() for field in feature.fields()]
            }
        
        # Agregar geometría al grupo
        obras_agrupadas[clave_obra]['geometrias'].append(feature.geometry())
    
    # Crear nueva capa con MultiLineString
    # Obtener CRS de la capa original
    crs = layer.crs()
    
    # Crear campos para la nueva capa
    campos = QgsFields()
    for field in layer.fields():
        campos.append(field)
    
    # Crear capa temporal
    nueva_capa = QgsVectorLayer(f"MultiLineString?crs={crs.authid()}", 
                               f"{layer.name()}_multiline", "memory")
    nueva_capa.dataProvider().addAttributes(campos)
    nueva_capa.updateFields()
    
    # Crear features con MultiLineString
    features_nuevas = []
    
    for clave_obra, datos in obras_agrupadas.items():
        # Crear MultiLineString
        if len(datos['geometrias']) == 1:
            # Si solo hay una línea, mantenerla como LineString
            geom_multiline = datos['geometrias'][0]
        else:
            # Crear MultiLineString con todas las líneas de la obra
            lineas = []
            for geom in datos['geometrias']:
                if geom.isMultipart():
                    # Si ya es multipart, obtener todas las partes
                    for parte in geom.asMultiPolyline():
                        lineas.append(parte)
                else:
                    # Si es una sola línea
                    lineas.append(geom.asPolyline())
            
            geom_multiline = QgsGeometry.fromMultiPolylineXY(lineas)
        
        # Crear nuevo feature
        nuevo_feature = QgsFeature()
        nuevo_feature.setGeometry(geom_multiline)
        
        # Establecer atributos usando el diccionario de propiedades
        atributos = []
        for campo in campos:
            nombre_campo = campo.name()
            valor = datos['propiedades'].get(nombre_campo, None)
            atributos.append(valor)
        
        nuevo_feature.setAttributes(atributos)
        features_nuevas.append(nuevo_feature)
    
    # Agregar features a la nueva capa
    nueva_capa.dataProvider().addFeatures(features_nuevas)
    nueva_capa.updateExtents()
    
    # Agregar la nueva capa al proyecto
    QgsProject.instance().addMapLayer(nueva_capa)
    
    print(f"Conversión completada:")
    print(f"- Features originales: {layer.featureCount()}")
    print(f"- Obras únicas creadas: {len(features_nuevas)}")
    print(f"- Nueva capa: {nueva_capa.name()}")

# Ejecutar la función
convertir_obras_a_multiline()
