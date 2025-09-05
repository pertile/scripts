
// TODO: pop up y lista de enlaces link_finished o link_progress
// TODO: revisar filtro de tipo de obra, hay obras que no están bien categorizadas
// TODO: totalizador de length por municipio y año

// Token de Mapbox para cargar el estilo personalizado local
mapboxgl.accessToken = 'pk.eyJ1IjoicGVydGlsZSIsImEiOiJjaWhqa2Fya2gwbmhtdGNsemtuaW14YmNlIn0.67aoJXemP7021X6XxsF71g';

// Agregar CSS para el panel de filtros
const style = document.createElement('style');
style.innerHTML = `
  #filters-panel {
    position: absolute;
    top: 20px;
    left: 20px;
    width: 280px;
    background: rgba(30,30,30,0.7);
    border: 2px solid #eee;
    box-shadow: 0 2px 12px #0002;
    z-index: 10000;
    max-height: 70vh;
    overflow-y: auto;
    padding: 0.7em 1em;
    color: #fff;
  }
  #filters-panel h2, #filters-panel h3, #filters-panel label {
    color: #fff;
    text-shadow: 0 1px 4px #000a;
    background: none;
    font-weight: 400;
    -webkit-text-stroke: 0;
    text-stroke: 0;
  }
  #filters-panel h2 {
    font-size: 1.1em;
    margin-bottom: 0.7em;
  }
  #filters-panel h3 {
    font-size: 1em;
    cursor: pointer;
    margin: 0.7em 0 0.3em 0;
  }
  .filters-section { margin-bottom: 0.7em; }
  .filters-options { display: none; margin-left: 0.7em; }
  .filters-section.open .filters-options { display: block; }
  .filters-options label { display: block; margin-bottom: 0.15em; font-size: 0.95em; }
`;
document.head.appendChild(style);

// Indicador de total pavimentado (ahora será una tabla)
const totalPavDiv = document.createElement('div');
totalPavDiv.id = 'total-pavimentado';
totalPavDiv.style.background = 'rgba(255,255,255,0.95)';
totalPavDiv.style.color = '#333';
totalPavDiv.style.fontSize = '0.9em';
totalPavDiv.style.padding = '1em';
totalPavDiv.style.borderRadius = '8px';
totalPavDiv.style.boxShadow = '0 2px 12px #0002';
totalPavDiv.style.border = '1px solid #ddd';
totalPavDiv.innerHTML = '<h2>Cargando datos...</h2>';

(function(){
  const style = document.createElement('style');
  style.innerHTML = `
    #filters-panel {
      position: absolute;
      top: 20px;
      left: 20px;
      width: 280px;
      background: rgba(30,30,30,0.7);
      border: 2px solid #eee;
      box-shadow: 0 2px 12px #0002;
      z-index: 10000;
      max-height: 70vh;
      overflow-y: auto;
      padding: 0.7em 1em;
      color: #fff;
    }
    #filters-panel h2, #filters-panel h3, #filters-panel label {
      color: #fff;
      text-shadow: 0 1px 4px #000a;
      background: none;
      font-weight: 400;
      -webkit-text-stroke: 0;
      text-stroke: 0;
    }
    #filters-panel h2 {
      font-size: 1.1em;
      margin-bottom: 0.7em;
    }
    #filters-panel h3 {
      font-size: 1em;
      cursor: pointer;
      margin: 0.7em 0 0.3em 0;
    }
    .filters-section { margin-bottom: 0.7em; }
    .filters-options { display: none; margin-left: 0.7em; }
    .filters-section.open .filters-options { display: block; }
    .filters-options label { display: block; margin-bottom: 0.15em; font-size: 0.95em; }
  `;
  document.head.appendChild(style);
})();

// Agregar elementos al DOM cuando esté listo
window.addEventListener('DOMContentLoaded', function() {
  const mapDiv = document.getElementById('mapGranResistencia');
  if (mapDiv) {
    // Hacer que el div del mapa tenga position relative
    mapDiv.style.position = 'relative';
    // Agregar el panel de filtros directamente al div del mapa
    mapDiv.appendChild(filtersPanel);
    filtersPanel.style.position = 'absolute';
    filtersPanel.style.top = '20px';
    filtersPanel.style.left = '20px';
    filtersPanel.style.zIndex = '10002';
  } else {
    document.body.appendChild(filtersPanel);
  }
  
  // Insertar el indicador de total antes del mapa como HTML simple
  if (mapDiv) {
    mapDiv.parentNode.insertBefore(totalPavDiv, mapDiv);
    // Resetear estilos para que sea HTML simple
    totalPavDiv.style.position = 'static';
    totalPavDiv.style.top = 'auto';
    totalPavDiv.style.left = 'auto';
    totalPavDiv.style.zIndex = 'auto';
    totalPavDiv.style.marginBottom = '1em';
  } else {
    document.body.insertBefore(totalPavDiv, document.body.firstChild);
  }
});

// Crear panel de filtros (debe estar antes del evento DOMContentLoaded)
const filtersPanel = document.createElement('div');
filtersPanel.id = 'filters-panel';
filtersPanel.innerHTML = `
  <h2>Filtros</h2>
  <div class="filters-section" id="filter-year">
    <h3>Año de pavimento</h3>
    <div class="filters-options"></div>
  </div>
  <div class="filters-section" id="filter-type">
    <h3>Tipo de obra</h3>
    <div class="filters-options"></div>
  </div>
  <div class="filters-section" id="filter-muni">
    <h3>Municipio</h3>
    <div class="filters-options"></div>
  </div>
`;
// Ubicar el panel flotante sobre el mapa
// Ya se agrega el panel de filtros y el totalizador en el evento DOMContentLoaded más arriba

// Desplegables
Array.from(filtersPanel.querySelectorAll('h3')).forEach(h3 => {
  h3.addEventListener('click', () => {
    h3.parentElement.classList.toggle('open');
  });
});

// Crear el mapa con Mapbox GL JS usando tu archivo de estilo local
// Primero verificar si WebGL está disponible
function isWebGLSupported() {
  try {
    const canvas = document.createElement('canvas');
    return !!(window.WebGLRenderingContext && 
              (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
  } catch (e) {
    return false;
  }
}

// Mostrar mensaje de error si WebGL no está disponible
if (!isWebGLSupported()) {
  const mapDiv = document.getElementById('mapGranResistencia');
  if (mapDiv) {
    mapDiv.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f5f5f5; border: 1px solid #ddd; color: #666; text-align: center; padding: 2em;">
        <div>
          <h3>⚠️ WebGL no está disponible</h3>
          <p>Su navegador no soporta WebGL o está deshabilitado.</p>
          <p>Para ver el mapa, por favor:</p>
          <ul style="text-align: left; display: inline-block;">
            <li>Actualice su navegador</li>
            <li>Habilite WebGL en la configuración</li>
            <li>Verifique que la aceleración por hardware esté activada</li>
          </ul>
        </div>
      </div>
    `;
  }
  console.error('WebGL no está disponible en este navegador');
  return; // Salir del script
}

var mapGranResistencia = new mapboxgl.Map({
  container: 'mapGranResistencia',
  style: '/Resistencia.json', // Tu archivo de estilo local
  center: [-59.0058, -27.4348],
  zoom: 11,
  bearing: 45, // Rotar el mapa 45 grados
  antialias: true, // Mejorar renderizado
  failIfMajorPerformanceCaveat: false // No fallar si hay problemas de rendimiento
});

// Cargar datos y preparar filtros cuando el mapa esté listo
mapGranResistencia.on('load', function() {
  fetch('/Obras GeoResistencia.geojson')
  .then(r => r.json())
  .then(data => {
    // Agrupar features por obra para evitar duplicados en los cálculos
    const obrasAgrupadas = {};
    const allFeatures = data.features;
    
    allFeatures.forEach(f => {
      // Crear clave única para cada obra (ajustar según tus campos)
      const claveObra = `${f.properties.title || f.properties.Obra}_${f.properties.TipoObra}`;
      
      if (!obrasAgrupadas[claveObra]) {
        obrasAgrupadas[claveObra] = {
          features: [],
          propiedades: f.properties,
          longitudTotal: 0
        };
      }
      
      obrasAgrupadas[claveObra].features.push(f);
      
      // Sumar longitud de este segmento
      let len = f.properties.length;
      if (typeof len === 'string') len = parseFloat(len.replace(',', '.'));
      if (!isNaN(len)) obrasAgrupadas[claveObra].longitudTotal += len;
    });
    
    // Crear array de obras únicas para los filtros
    const obrasUnicas = Object.values(obrasAgrupadas).map(obra => {
      // Crear un feature representativo con la longitud total
      const featureRepresentativo = {
        ...obra.features[0], // Tomar el primer feature como base
        properties: {
          ...obra.propiedades,
          length: obra.longitudTotal, // Longitud total de la obra
          segmentCount: obra.features.length // Cantidad de segmentos
        }
      };
      return featureRepresentativo;
    });
    
    // Filtrar solo obras con fecha de pavimento para los cálculos
    const features = obrasUnicas.filter(f => f.properties.FechaPavimento);
    features.forEach(f => {
      f.properties.pavementYear = (new Date(f.properties.FechaPavimento)).getFullYear();
    });

    const years = [...new Set(features.map(f => f.properties.pavementYear))].sort((a,b) => b-a);
    const types = [...new Set(features.map(f => f.properties.TipoObra))].sort();
    // Municipios dinámicos desde los datos únicos
    let municipalities = [...new Set(obrasUnicas.map(f => {
      let m = f.properties.municipality;
      if (!m || m.trim() === '') return 'Sin municipio';
      return m.trim();
    }))].sort();
    if (!municipalities.includes('Sin municipio')) municipalities.push('Sin municipio');
    
    // Debug: mostrar estadísticas de agrupación
    console.log(`Total features originales: ${allFeatures.length}`);
    console.log(`Obras únicas detectadas: ${obrasUnicas.length}`);
    console.log(`Obras con fecha de pavimento: ${features.length}`);
    // Opción especial para obras en curso (sin FechaPavimento)
    let showInProgress = true;

    // Filtros por defecto: año actual y anterior
    const today = new Date();
    const currentYear = today.getFullYear();
    const previousYear = currentYear - 1;
    let filterYears = new Set([currentYear, previousYear]);
    let filterTypes = new Set(types);
    let filterMunicipalities = new Set(municipalities);

    // Renderizar checkboxes
    function renderCheckboxes(arr, container, filterSet, type, onChange) {
      container.innerHTML = '';
      arr.forEach(val => {
        const id = 'filter_' + type + '_' + val;
        const checked = filterSet.has(val) ? 'checked' : '';
        container.innerHTML += `<label><input type="checkbox" id="${id}" value="${val}" ${checked}> ${val}</label>`;
      });
      container.querySelectorAll('input[type=checkbox]').forEach(cb => {
        cb.addEventListener('change', e => {
          let value = e.target.value;
          if (type === 'year') value = parseInt(value);
          // Para municipio y tipo de obra queda como string
          if (e.target.checked) filterSet.add(value);
          else filterSet.delete(value);
          updateView();
        });
      });
    }
    renderCheckboxes(years, filtersPanel.querySelector('#filter-year .filters-options'), filterYears, 'year', updateView);
    renderCheckboxes(types, filtersPanel.querySelector('#filter-type .filters-options'), filterTypes, 'type', updateView);
    renderCheckboxes(municipalities, filtersPanel.querySelector('#filter-muni .filters-options'), filterMunicipalities, 'muni', updateView);

    // Función para crear popup de obra
    function createPopupContent(props) {
      let muni = props.municipality;
      if (!muni || muni.trim() === '') muni = 'Sin municipio';
      else muni = muni.trim();
      
      let popupContent = `
        <div style="max-width: 300px;">
          <h3 style="margin-top: 0; color: #333;">${props.TipoObra}: ${props.title || props.Obra}</h3>
          <div style="margin-bottom: 0.5em;"><strong>Municipio:</strong> ${muni}</div>
          <div style="margin-bottom: 0.5em;"><strong>Año de pavimento:</strong> ${props.pavementYear}</div>
          <div style="margin-bottom: 0.5em;"><strong>Descripción:</strong> ${props.short_description || 'No disponible'}</div>
          <div style="margin-bottom: 0.5em;"><strong>Fecha de pavimento:</strong> ${props.FechaPavimento ? (new Date(props.FechaPavimento).toLocaleDateString('es-ES')) : 'No disponible'}</div>
      `;
      
      // Agregar enlaces si están disponibles
      if (props.link_finished) {
        popupContent += `<div style="margin-bottom: 0.5em;"><a href="${props.link_finished}" target="_blank" style="color: #0066cc;">Ver obra finalizada</a></div>`;
      }
      if (props.link_progress) {
        popupContent += `<div style="margin-bottom: 0.5em;"><a href="${props.link_progress}" target="_blank" style="color: #0066cc;">Ver progreso de obra</a></div>`;
      }
      
      popupContent += '</div>';
      return popupContent;
    }

    // Función para hacer zoom a una obra específica
    window.zoomToObra = function(obraTitle, tipoObra, skipZoom = false) {
      const claveObra = `${obraTitle}_${tipoObra}`;
      const obra = obrasAgrupadas[claveObra];
      
      if (obra && obra.features.length > 0) {
        // Remover capa de obra seleccionada anterior si existe
        if (mapGranResistencia.getSource('obra-selected')) {
          mapGranResistencia.removeLayer('obra-selected-layer');
          mapGranResistencia.removeSource('obra-selected');
        }
        
        // Agregar nueva capa para la obra seleccionada
        mapGranResistencia.addSource('obra-selected', {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: obra.features
          }
        });

        mapGranResistencia.addLayer({
          id: 'obra-selected-layer',
          type: 'line',
          source: 'obra-selected',
          paint: {
            'line-color': '#00ff00', // Verde brillante para destacar
            'line-width': 6,
            'line-opacity': 1
          }
        });
        
        // Solo hacer zoom si no se especifica skipZoom
        if (!skipZoom) {
          // Calcular el bbox de todos los segmentos de la obra
          let minLng = Infinity, maxLng = -Infinity;
          let minLat = Infinity, maxLat = -Infinity;
          
          obra.features.forEach(feature => {
            if (feature.geometry.type === 'LineString') {
              feature.geometry.coordinates.forEach(coord => {
                const [lng, lat] = coord;
                minLng = Math.min(minLng, lng);
                maxLng = Math.max(maxLng, lng);
                minLat = Math.min(minLat, lat);
                maxLat = Math.max(maxLat, lat);
              });
            }
          });
          
          // Hacer zoom al área de la obra
          if (minLng !== Infinity) {
            mapGranResistencia.fitBounds([
              [minLng, minLat],
              [maxLng, maxLat]
            ], {
              padding: 50,
              maxZoom: 16,
              bearing: 45,
            });
          }
        }
      }
    };

    // Inicializar después de cargar los datos
    updateView();

    // Actualizar mapa y lista
    function updateView() {
      // Remover capa de obra seleccionada al actualizar filtros
      if (mapGranResistencia.getSource('obra-selected')) {
        mapGranResistencia.removeLayer('obra-selected-layer');
        mapGranResistencia.removeSource('obra-selected');
      }
      
      // Filtrar obras únicas
      const filteredObras = features.filter(f => {
        let muni = f.properties.municipality;
        if (!muni || muni.trim() === '') muni = 'Sin municipio';
        else muni = muni.trim();
        return filterYears.has(f.properties.pavementYear) &&
               filterTypes.has(f.properties.TipoObra) &&
               filterMunicipalities.has(muni);
      });
      
      // Obtener todos los segmentos de las obras filtradas para mostrar en el mapa
      const segmentosFiltrados = [];
      filteredObras.forEach(obra => {
        const claveObra = `${obra.properties.title || obra.properties.Obra}_${obra.properties.TipoObra}`;
        if (obrasAgrupadas[claveObra]) {
          segmentosFiltrados.push(...obrasAgrupadas[claveObra].features);
        }
      });
      
      // Generar tabla de totales por año y municipio (usando obras únicas)
      generateTotalTable(filteredObras);

      // Remover capa anterior si existe
      if (mapGranResistencia.getSource('obras')) {
        mapGranResistencia.removeLayer('obras-layer');
        mapGranResistencia.removeSource('obras');
      }
      
      // Crear nueva fuente y capa con todos los segmentos filtrados
      if (segmentosFiltrados.length > 0) {
        mapGranResistencia.addSource('obras', {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: segmentosFiltrados
          }
        });

        mapGranResistencia.addLayer({
          id: 'obras-layer',
          type: 'line',
          source: 'obras',
          paint: {
            'line-color': '#ff0000',
            'line-width': 4,
            'line-opacity': 0.8
          }
        });

        // Agregar eventos de click y hover
        mapGranResistencia.on('click', 'obras-layer', (e) => {
          const props = e.features[0].properties;
          
          // Seleccionar la obra automáticamente al hacer click (sin zoom)
          const obraTitle = props.title || props.Obra;
          const tipoObra = props.TipoObra;
          zoomToObra(obraTitle, tipoObra, true); // skipZoom = true
          
          // Mostrar popup
          new mapboxgl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(createPopupContent(props))
            .addTo(mapGranResistencia);
        });

        mapGranResistencia.on('mouseenter', 'obras-layer', () => {
          mapGranResistencia.getCanvas().style.cursor = 'pointer';
        });

        mapGranResistencia.on('mouseleave', 'obras-layer', () => {
          mapGranResistencia.getCanvas().style.cursor = '';
        });
      }

      console.log(`Obras filtradas: ${filteredObras.length}, Segmentos mostrados: ${segmentosFiltrados.length}`);
      
      // Actualizar lista (usando obras únicas)
      renderList(filteredObras);
    }

    // Función para generar tabla de totales
    function generateTotalTable(filtered) {
      // Crear estructura de datos para la tabla
      const tableData = {};
      const yearTotals = {};
      const muniTotals = {};
      let grandTotal = 0;

      // Procesar datos filtrados
      filtered.forEach(f => {
        let muni = f.properties.municipality;
        if (!muni || muni.trim() === '') muni = 'Sin municipio';
        else muni = muni.trim();
        
        const year = f.properties.pavementYear;
        let len = f.properties.length;
        if (typeof len === 'string') len = parseFloat(len.replace(',', '.'));
        if (isNaN(len)) len = 0;
        
        const lengthKm = len / 1000;
        
        if (!tableData[year]) tableData[year] = {};
        if (!tableData[year][muni]) tableData[year][muni] = 0;
        
        tableData[year][muni] += lengthKm;
        
        if (!yearTotals[year]) yearTotals[year] = 0;
        yearTotals[year] += lengthKm;
        
        if (!muniTotals[muni]) muniTotals[muni] = 0;
        muniTotals[muni] += lengthKm;
        
        grandTotal += lengthKm;
      });

      // Obtener años y municipios ordenados
      const sortedYears = Object.keys(tableData).sort((a,b) => b-a);
      const sortedMunis = Object.keys(muniTotals).sort();

      // Generar HTML de la tabla
      let tableHTML = '<h2>Total pavimentado por año y municipio</h2>';
      tableHTML += '<table style="border-collapse: collapse; width: 100%; margin-bottom: 1em;">';
      
      // Encabezado
      tableHTML += '<tr style="background: #f5f5f5; font-weight: bold;">';
      tableHTML += '<th style="border: 1px solid #ccc; padding: 8px; text-align: left;">Año</th>';
      sortedMunis.forEach(muni => {
        tableHTML += `<th style="border: 1px solid #ccc; padding: 8px; text-align: center;">${muni}</th>`;
      });
      tableHTML += '<th style="border: 1px solid #ccc; padding: 8px; text-align: center; background: #e0e0e0;">Total por año</th>';
      tableHTML += '</tr>';

      // Filas de datos
      sortedYears.forEach(year => {
        tableHTML += '<tr>';
        tableHTML += `<td style="border: 1px solid #ccc; padding: 8px; font-weight: bold;">${year}</td>`;
        
        sortedMunis.forEach(muni => {
          const value = tableData[year] && tableData[year][muni] ? tableData[year][muni] : 0;
          const displayValue = value > 0 ? value.toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' km' : '-';
          tableHTML += `<td style="border: 1px solid #ccc; padding: 8px; text-align: center;">${displayValue}</td>`;
        });
        
        const yearTotal = yearTotals[year] || 0;
        tableHTML += `<td style="border: 1px solid #ccc; padding: 8px; text-align: center; background: #f0f0f0; font-weight: bold;">${yearTotal.toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})} km</td>`;
        tableHTML += '</tr>';
      });

      // Fila de totales por municipio
      tableHTML += '<tr style="background: #e0e0e0; font-weight: bold;">';
      tableHTML += '<td style="border: 1px solid #ccc; padding: 8px;">Total por municipio</td>';
      
      sortedMunis.forEach(muni => {
        const muniTotal = muniTotals[muni] || 0;
        tableHTML += `<td style="border: 1px solid #ccc; padding: 8px; text-align: center;">${muniTotal.toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}&nbsp;km</td>`;
      });
      
      tableHTML += `<td style="border: 1px solid #ccc; padding: 8px; text-align: center; background: #d0d0d0; font-weight: bold;">${grandTotal.toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})} km</td>`;
      tableHTML += '</tr>';
      
      tableHTML += '</table>';

      // Actualizar el contenido del div
      totalPavDiv.innerHTML = tableHTML;
    }

    // Renderizar lista de obras
    function renderList(filtered) {
      let worksListContainer = document.getElementById('works-list-container');
      if (!worksListContainer) {
        worksListContainer = document.createElement('div');
        worksListContainer.id = 'works-list-container';
        document.body.appendChild(worksListContainer);
      }
      worksListContainer.innerHTML = '<h2>Obras filtradas</h2><ol>' +
        filtered.map(f => {
          const d = f.properties;
          let muni = d.municipality;
          if (!muni || muni.trim() === '') muni = 'Sin municipio';
          else muni = muni.trim();
          const isInProgress = !d.FechaPavimento;
          
          // Crear título con o sin enlace
          let titleHTML;
          if (d.link_finished) {
            titleHTML = `<a href="${d.link_finished}" target="_blank" style="color: #0066cc; text-decoration: none;">${d.TipoObra}: ${d.title || d.Obra}</a>`;
          } else {
            titleHTML = `${d.TipoObra}: ${d.title || d.Obra}`;
          }
          
          // Ícono de mundo/mapa para hacer zoom a la obra
          const mapIcon = `<span onclick="zoomToObra('${(d.title || d.Obra).replace(/'/g, "\\'")}', '${d.TipoObra}')" style="cursor: pointer; margin-left: 8px; color: #007cba; font-size: 1.1em;" title="Hacer zoom a esta obra en el mapa">🌍</span>`;
          
          return `<li style="margin-bottom:1em;">
            ${titleHTML}${mapIcon}
            <div style="font-size:0.8em; margin-bottom:2px;"><strong>Municipio:</strong> ${muni}. <strong>Longitud:</strong> ${d.length}&nbsp;m</div>
            <div style="font-size:0.8em; margin-bottom:2px;"><strong>Descripción:</strong> ${d.short_description || ''}</div>
            <div style="font-size:0.8em; margin-bottom:2px;"><strong>Fecha de pavimento:</strong> ${d.FechaPavimento ? (new Date(d.FechaPavimento).toLocaleDateString('es-ES')) : ''}</div>
          </li>`;
        }).join('') + '</ol>';
    }

  });
});
