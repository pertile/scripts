#!/usr/bin/env python3
"""
Script para procesar colectivos.geojson y extraer solo los highways de rutas de colectivos.

Este script:
1. Filtra solo features que tengan la propiedad "highway"
2. De esos, mantiene solo los que tengan relaciones con "route": "bus"
3. Simplifica las propiedades manteniendo solo: highway, surface, name, ref
4. Para el ref, usa el valor de ref de la relación, o name si ref no existe
5. Agrupa los segmentos por ref para generar rutas completas
"""

import json
import sys
import os
from collections import defaultdict

def normalize_surface(surface_value):
    """
    Normaliza los valores de superficie a solo 'paved' o 'unpaved'
    """
    if not surface_value:
        return 'unpaved'  # Por defecto, sin dato = no pavimentado
    
    surface_lower = surface_value.lower().strip()
    
    # Superficies no pavimentadas
    unpaved_surfaces = {
        'unpaved', 'dirt', 'gravel', 'earth', 'ground', 
        'sand', 'grass', 'mud', 'soil', 'track'
    }
    
    # Si está en la lista de no pavimentadas
    if surface_lower in unpaved_surfaces:
        return 'unpaved'
    
    # Todo lo demás se considera pavimentado
    # (asphalt, concrete, paved, paving_stones, etc.)
    return 'paved'

def calculate_linestring_length(coordinates):
    """
    Calcula la longitud aproximada de una LineString en kilómetros
    usando la fórmula de Haversine para distancia entre puntos
    """
    import math
    
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Distancia entre dos puntos en km usando fórmula de Haversine"""
        R = 6371  # Radio de la Tierra en km
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    total_length = 0
    for i in range(len(coordinates) - 1):
        lon1, lat1 = coordinates[i]
        lon2, lat2 = coordinates[i + 1]
        total_length += haversine_distance(lat1, lon1, lat2, lon2)
    
    return total_length

def process_buses_geojson(input_file, output_file):
    """
    Procesa el archivo de colectivos y genera una versión simplificada
    """
    print(f"🚌 Procesando {input_file}...")
    
    try:
        # Leer archivo de entrada
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📁 Archivo cargado. Total features: {len(data['features'])}")
        
        # Contenedores para los datos procesados
        highway_features = []
        bus_routes_info = {}
        
        stats = {
            'total_features': len(data['features']),
            'features_with_bus_relations': 0,
            'unique_bus_routes': 0,
            'total_km_paved': 0,
            'total_km_unpaved': 0
        }
        
        for feature in data['features']:
            properties = feature.get('properties', {})
            
            # Verificar si tiene relaciones con rutas de colectivos
            relations = properties.get('@relations', [])
            bus_relations = []
            
            for relation in relations:
                reltags = relation.get('reltags', {})
                if reltags.get('route') == 'bus':
                    bus_relations.append(relation)
            
            # Si no tiene relaciones de bus, saltar
            if not bus_relations:
                continue
                
            stats['features_with_bus_relations'] += 1
            
            # Crear nueva feature simplificada
            normalized_surface = normalize_surface(properties.get('surface'))
            
            # Calcular longitud del segmento
            segment_length = 0
            if feature['geometry']['type'] == 'LineString':
                segment_length = calculate_linestring_length(feature['geometry']['coordinates'])
            
            # Actualizar estadísticas de kilometraje
            if normalized_surface == 'paved':
                stats['total_km_paved'] += segment_length
            else:
                stats['total_km_unpaved'] += segment_length
            
            new_feature = {
                "type": "Feature",
                "properties": {
                    "highway": properties.get('highway'),
                    "surface": normalized_surface,
                    "name": properties.get('name'),
                    "length_km": round(segment_length, 3)
                },
                "geometry": feature['geometry'],
                "id": feature.get('id')
            }
            
            # Lista para recopilar todas las líneas de este segmento
            bus_line_refs = []
            
            # Procesar cada relación de bus
            for relation in bus_relations:
                reltags = relation.get('reltags', {})
                
                # Determinar ref: usar ref si existe, sino name
                ref = reltags.get('ref') or reltags.get('name') or f"sin_ref_{relation.get('rel', 'unknown')}"
                
                bus_line_refs.append(ref)
            
            # Agregar el campo bus_lines como concatenación de todos los refs
            new_feature['properties']['bus_lines'] = ','.join(bus_line_refs)
            
            # Guardar información de todas las rutas para estadísticas
            for ref in bus_line_refs:
                if ref not in bus_routes_info:
                    # Buscar el nombre y route_id de la primera aparición de esta línea
                    route_name = None
                    route_id = None
                    for relation in bus_relations:
                        reltags = relation.get('reltags', {})
                        relation_ref = reltags.get('ref') or reltags.get('name') or f"sin_ref_{relation.get('rel', 'unknown')}"
                        if relation_ref == ref:
                            route_name = reltags.get('name')
                            route_id = relation.get('rel')
                            break
                    
                    bus_routes_info[ref] = {
                        "name": route_name,
                        "segments": 0,
                        "route_id": route_id
                    }
                bus_routes_info[ref]['segments'] += 1
            
            highway_features.append(new_feature)
        
        stats['unique_bus_routes'] = len(bus_routes_info)
        
        # Crear nuevo GeoJSON
        output_data = {
            "type": "FeatureCollection",
            "generator": "colectivos-processor",
            "description": "Features de rutas de colectivos - Versión simplificada",
            "timestamp": data.get('timestamp'),
            "processing_stats": stats,
            "bus_routes_summary": dict(sorted(bus_routes_info.items())),
            "features": highway_features
        }
        
        # Guardar archivo de salida
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        # Mostrar estadísticas
        print("\n📊 Estadísticas del procesamiento:")
        print(f"   • Features totales: {stats['total_features']:,}")
        print(f"   • Features con rutas de colectivos: {stats['features_with_bus_relations']:,}")
        print(f"   • Rutas de colectivos únicas: {stats['unique_bus_routes']}")
        print(f"   • Vías pavimentadas: {stats['total_km_paved']:.1f} km")
        print(f"   • Vías sin pavimentar: {stats['total_km_unpaved']:.1f} km")
        print(f"   • Total de vías: {stats['total_km_paved'] + stats['total_km_unpaved']:.1f} km")
        
        print("\n🚌 Rutas de colectivos encontradas:")
        for ref, info in sorted(bus_routes_info.items()):
            name_display = f" - {info['name']}" if info['name'] and info['name'] != ref else ""
            print(f"   • {ref}{name_display} ({info['segments']} segmentos)")
        
        # Información del archivo de salida
        input_size = os.path.getsize(input_file) / (1024 * 1024)  # MB
        output_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        reduction = ((input_size - output_size) / input_size) * 100
        
        print(f"\n💾 Archivos:")
        print(f"   • Entrada: {input_file} ({input_size:.1f} MB)")
        print(f"   • Salida: {output_file} ({output_size:.1f} MB)")
        print(f"   • Reducción: {reduction:.1f}%")
        
        print(f"\n✅ Procesamiento completado. Archivo guardado: {output_file}")
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {input_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error al leer JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

def main():
    """Función principal"""
    input_file = "colectivos.geojson"
    output_file = "colectivos-simplificado.geojson"
    
    # Verificar que existe el archivo de entrada
    if not os.path.exists(input_file):
        print(f"❌ Error: No se encontró {input_file}")
        print("   Asegúrate de que el archivo esté en el directorio actual")
        sys.exit(1)
    
    print("🚌 Procesador de rutas de colectivos")
    print("=" * 40)
    
    process_buses_geojson(input_file, output_file)

if __name__ == "__main__":
    main()
