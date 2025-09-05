"""
Script simplificado para agrupar obras en QGIS
Ejecutar desde la consola de Python de QGIS
"""

def agrupar_obras_por_titulo():
    # Obtener capa activa
    layer = iface.activeLayer()
    
    # Crear diccionario de obras agrupadas
    obras = {}
    
    for feature in layer.getFeatures():
        titulo = feature['title'] or feature['Obra']
        tipo = feature['TipoObra']
        clave = f"{titulo}_{tipo}"
        
        if clave not in obras:
            obras[clave] = []
        obras[clave].append(feature)
    
    # Mostrar estadísticas
    total_features = layer.featureCount()
    obras_unicas = len(obras)
    
    print(f"Features totales: {total_features}")
    print(f"Obras únicas: {obras_unicas}")
    print(f"Promedio segmentos por obra: {total_features/obras_unicas:.1f}")
    
    # Listar obras con más segmentos
    obras_multiples = [(k,len(v)) for k,v in obras.items() if len(v) > 1]
    obras_multiples.sort(key=lambda x: x[1], reverse=True)
    
    print("\nObras con múltiples segmentos:")
    for obra, segmentos in obras_multiples[:10]:
        print(f"- {obra}: {segmentos} segmentos")

# Ejecutar
agrupar_obras_por_titulo()
