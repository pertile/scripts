"""
Script simplificado para convertir obras a MultiLineString en QGIS
Versión más robusta con mejor manejo de errores
"""

def convertir_obras_simple():
    """
    Versión simplificada que agrupa obras y calcula longitudes totales
    """
    try:
        # Obtener la capa activa
        layer = iface.activeLayer()
        
        if not layer:
            print("ERROR: No hay capa activa seleccionada")
            return
        
        print(f"Procesando capa: {layer.name()}")
        print(f"Total de features: {layer.featureCount()}")
        
        # Analizar campos disponibles
        print(f"\n=== CAMPOS DISPONIBLES ===")
        for field in layer.fields():
            print(f"- {field.name()} ({field.typeName()})")
        
        # Analizar primeros features para entender los datos
        print(f"\n=== MUESTRA DE DATOS ===")
        contador = 0
        for feature in layer.getFeatures():
            if contador >= 3:  # Solo mostrar 3 ejemplos
                break
            obra = feature['Obra'] if 'Obra' in [f.name() for f in feature.fields()] else 'N/A'
            tipo = feature['TipoObra'] if 'TipoObra' in [f.name() for f in feature.fields()] else 'N/A'
            title = feature['title'] if 'title' in [f.name() for f in feature.fields()] else 'N/A'
            print(f"Feature {feature.id()}: Obra='{obra}', TipoObra='{tipo}', title='{title}'")
            contador += 1
        
        # Diccionario para agrupar obras
        obras_agrupadas = {}
        
        # Procesar cada feature
        for feature in layer.getFeatures():
            try:
                # Obtener identificadores de la obra - usar "Obra" como principal
                titulo = None
                if 'Obra' in 
                [f.name() for f in feature.fields()]:
                    titulo = feature['Obra']
                elif 'title' in [f.name() for f in feature.fields()]:
                    titulo = feature['title']
                
                # Verificar si realmente hay valores None en el campo Obra
                if not titulo or str(titulo).strip() == '' or titulo == 'NULL' or str(titulo) == 'None':
                    print(f"ADVERTENCIA: Feature {feature.id()} tiene Obra='{titulo}'")
                    titulo = f"Obra_sin_nombre_{feature.id()}"
                
                tipo_obra = feature['TipoObra'] if 'TipoObra' in [f.name() for f in feature.fields()] else 'Sin_tipo'
                if not tipo_obra or str(tipo_obra).strip() == '' or tipo_obra == 'NULL' or str(tipo_obra) == 'None':
                    tipo_obra = 'Sin_tipo'
                
                # Crear clave única
                clave_obra = f"{titulo}_{tipo_obra}"
                
                if clave_obra not in obras_agrupadas:
                    # Usar la longitud del primer segmento (que es la longitud total de la obra)
                    longitud_obra = 0
                    if 'length' in [f.name() for f in feature.fields()]:
                        longitud_campo = feature['length']
                        if longitud_campo and str(longitud_campo).strip() != '':
                            try:
                                if isinstance(longitud_campo, str):
                                    longitud_campo = float(longitud_campo.replace(',', '.'))
                                longitud_obra = float(longitud_campo)
                            except:
                                pass
                    
                    obras_agrupadas[clave_obra] = {
                        'geometrias': [],
                        'feature_ejemplo': feature,
                        'longitud_total': longitud_obra,  # Longitud total de la obra (no sumar)
                        'cantidad_segmentos': 0
                    }
                
                # Agregar geometría
                obras_agrupadas[clave_obra]['geometrias'].append(feature.geometry())
                obras_agrupadas[clave_obra]['cantidad_segmentos'] += 1
                            
            except Exception as e:
                print(f"Error procesando feature: {e}")
                continue
        
        # Mostrar estadísticas detalladas
        print(f"\n=== ESTADÍSTICAS ===")
        print(f"Features originales: {layer.featureCount()}")
        print(f"Obras únicas detectadas: {len(obras_agrupadas)}")
        
        # Mostrar obras con múltiples segmentos
        obras_multiples = [(k, v['cantidad_segmentos'], v['longitud_total']) 
                          for k, v in obras_agrupadas.items() 
                          if v['cantidad_segmentos'] > 1]
        
        if obras_multiples:
            obras_multiples.sort(key=lambda x: x[1], reverse=True)
            print(f"\n=== OBRAS CON MÚLTIPLES SEGMENTOS ===")
            for obra, segmentos, longitud in obras_multiples[:15]:
                print(f"- {obra}: {segmentos} segmentos, {longitud:.0f}m total")
        
        # Verificar problemas en los datos
        obras_sin_nombre = [k for k in obras_agrupadas.keys() if 'Obra_sin_nombre_' in k]
        if obras_sin_nombre:
            print(f"\n=== ADVERTENCIA: FEATURES CON CAMPO 'Obra' PROBLEMÁTICO ===")
            print(f"Se encontraron {len(obras_sin_nombre)} features con valores None/vacío en 'Obra'")
            
        # Mostrar distribución por tipo de obra
        tipos_obra = {}
        for clave, datos in obras_agrupadas.items():
            tipo = clave.split('_')[-1]  # Último elemento después del _
            tipos_obra[tipo] = tipos_obra.get(tipo, 0) + datos['cantidad_segmentos']
        
        print(f"\n=== DISTRIBUCIÓN POR TIPO DE OBRA ===")
        for tipo, cantidad in sorted(tipos_obra.items(), key=lambda x: x[1], reverse=True):
            print(f"- {tipo}: {cantidad} segmentos")
        
        # Crear automáticamente la capa MultiLineString
        print(f"\n=== CREANDO CAPA MULTILINESTRING ===")
        crear_capa_multiline(layer, obras_agrupadas)
            
    except Exception as e:
        print(f"ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()

def crear_capa_multiline(layer_original, obras_agrupadas):
    """
    Crea una nueva capa con geometrías MultiLineString
    """
    try:
        from qgis.core import QgsVectorLayer, QgsFields, QgsFeature, QgsGeometry, QgsProject
        
        # Crear campos para la nueva capa
        campos = QgsFields()
        for field in layer_original.fields():
            campos.append(field)
        
        # Agregar campo para cantidad de segmentos
        from qgis.core import QgsField
        from qgis.PyQt.QtCore import QVariant  # Usar qgis.PyQt en lugar de PyQt5
        campos.append(QgsField('segmentos_count', QVariant.Int))
        campos.append(QgsField('longitud_total_calc', QVariant.Double))
        
        # Crear nueva capa temporal
        crs = layer_original.crs()
        nueva_capa = QgsVectorLayer(f"MultiLineString?crs={crs.authid()}", 
                                   f"{layer_original.name()}_multiline", "memory")
        nueva_capa.dataProvider().addAttributes(campos)
        nueva_capa.updateFields()
        
        # Crear features con MultiLineString
        features_nuevas = []
        
        for clave_obra, datos in obras_agrupadas.items():
            try:
                # Crear geometría MultiLineString
                geometrias = datos['geometrias']
                
                if len(geometrias) == 1:
                    # Si solo hay una línea, mantenerla
                    geom_final = geometrias[0]
                else:
                    # Crear MultiLineString
                    lineas = []
                    for geom in geometrias:
                        if geom.isMultipart():
                            for parte in geom.asMultiPolyline():
                                lineas.append(parte)
                        else:
                            lineas.append(geom.asPolyline())
                    
                    geom_final = QgsGeometry.fromMultiPolylineXY(lineas)
                
                # Crear nuevo feature
                nuevo_feature = QgsFeature()
                nuevo_feature.setGeometry(geom_final)
                
                # Copiar atributos del feature ejemplo
                feature_ejemplo = datos['feature_ejemplo']
                atributos = list(feature_ejemplo.attributes())
                
                # Agregar campos nuevos
                atributos.append(datos['cantidad_segmentos'])  # segmentos_count
                atributos.append(datos['longitud_total'])      # longitud_total_calc
                
                nuevo_feature.setAttributes(atributos)
                features_nuevas.append(nuevo_feature)
                
            except Exception as e:
                print(f"Error creando feature para {clave_obra}: {e}")
                continue
        
        # Agregar features a la nueva capa
        nueva_capa.dataProvider().addFeatures(features_nuevas)
        nueva_capa.updateExtents()
        
        # Agregar al proyecto
        QgsProject.instance().addMapLayer(nueva_capa)
        
        print(f"\n=== CONVERSIÓN COMPLETADA ===")
        print(f"Nueva capa creada: {nueva_capa.name()}")
        print(f"Features creados: {len(features_nuevas)}")
        
    except Exception as e:
        print(f"ERROR creando nueva capa: {e}")

# Ejecutar
print("Iniciando conversión de obras a MultiLineString...")
convertir_obras_simple()
