
// TODO: pop up y lista de enlaces link_finished o link_progress
// TODO: revisar filtro de tipo de obra, hay obras que no están bien categorizadas
// TODO: totalizador de length por municipio y año

mapboxgl.accessToken = 'pk.eyJ1IjoicGVydGlsZSIsImEiOiJjaWhqa2Fya2gwbmhtdGNsemtuaW14YmNlIn0.67aoJXemP7021X6XxsF71g';

// Agregar CSS para el panel de filtros
(function(){
  const style = document.createElement('style');
  style.innerHTML = `
    #filters-panel {
      position: fixed;
      top: 80px;
      right: 0;
      width: 320px;
      background: #fff;
      border-left: 2px solid #eee;
      box-shadow: -2px 0 8px #0001;
      z-index: 9999;
      max-height: 80vh;
      overflow-y: auto;
      padding: 1em;
    }
    #filters-panel h3 { cursor: pointer; margin: 1em 0 0.5em 0; }
    .filters-section { margin-bottom: 1em; }
    .filters-options { display: none; margin-left: 1em; }
    .filters-section.open .filters-options { display: block; }
    .filters-options label { display: block; margin-bottom: 0.2em; }
  `;
  document.head.appendChild(style);
})();

// Crear panel de filtros
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
document.body.appendChild(filtersPanel);

// Desplegables
Array.from(filtersPanel.querySelectorAll('h3')).forEach(h3 => {
  h3.addEventListener('click', () => {
    h3.parentElement.classList.toggle('open');
  });
});

// Crear el mapa
var mapGranResistencia = new mapboxgl.Map({
  container: 'mapGranResistencia',
  center: [-59.0058,-27.4348],
  zoom: 11.5,
  bearing: 45,
  style: '/Resistencia.json'
});

// Cargar datos y preparar filtros
fetch('/Obras GeoResistencia.geojson')
  .then(r => r.json())
  .then(data => {
    // Extraer valores únicos
    // DEBUG extra: mostrar features con municipio Resistencia
    const allFeatures = data.features;
    const features = data.features.filter(f => f.properties.FechaPavimento);
    features.forEach(f => {
      f.properties.pavementYear = (new Date(f.properties.FechaPavimento)).getFullYear();
    });

    const years = [...new Set(features.map(f => f.properties.pavementYear))].sort((a,b) => b-a);
    const types = [...new Set(features.map(f => f.properties.TipoObra))].sort();
    // Municipios dinámicos desde los datos
    let municipalities = [...new Set(data.features.map(f => {
      let m = f.properties.municipality;
      if (!m || m.trim() === '') return 'Sin municipio';
      return m.trim();
    }))].sort();
    if (!municipalities.includes('Sin municipio')) municipalities.push('Sin municipio');
    // Debug: mostrar municipios detectados y ejemplos
    const muniCounts = {};
    data.features.forEach(f => {
      let m = f.properties.municipality;
      if (!m || m.trim() === '') m = 'Sin municipio';
      else m = m.trim();
      muniCounts[m] = (muniCounts[m] || 0) + 1;
    });
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

    // Capa de obras
    let layerId = 'works-pavimeter';
    mapGranResistencia.on('load', function () {
      mapGranResistencia.addLayer({
        id: layerId,
        type: 'line',
        source: {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: []
          }
        },
        layout: { "line-join": "round", "line-cap": "round" },
        paint: { 'line-color': '#ff0000', 'line-width': 4 }
      });
      updateView();
    });

    // Actualizar mapa y lista
    function updateView() {
      // Filtrar features (sin opción "En curso")
      const filtered = features.filter(f => {
        let muni = f.properties.municipality;
        if (!muni || muni.trim() === '') muni = 'Sin municipio';
        else muni = muni.trim();
        return filterYears.has(f.properties.pavementYear) &&
               filterTypes.has(f.properties.TipoObra) &&
               filterMunicipalities.has(muni);
      });
      const filteredResis = filtered.filter(f => {
        let m = f.properties.municipality;
        if (!m || m.trim() === '') m = 'Sin municipio';
        else m = m.trim();
        return m === 'Resistencia';
      });
      console.log('Features filtrados con municipio=Resistencia:', filteredResis);
      console.log('Títulos filtrados Resistencia:', filteredResis.map(f => f.properties.title || f.properties.Obra));
      // Actualizar capa
      if (mapGranResistencia.getSource(layerId)) {
        mapGranResistencia.getSource(layerId).setData({
          type: 'FeatureCollection',
          features: filtered
        });
      }
      // Actualizar lista
      renderList(filtered);
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
          return `<li style="margin-bottom:1em;">
            <h3>${d.TipoObra}: ${d.title || d.Obra}</h3>
            <div><strong>Municipio:</strong> ${muni}</div>
            ${isInProgress ? '<div><strong>Estado:</strong> En curso</div>' : `<div><strong>Año de pavimento:</strong> ${d.pavementYear}</div>`}
            <div><strong>Descripción:</strong> ${d.short_description || ''}</div>
            <div><strong>Fecha de pavimento:</strong> ${d.FechaPavimento ? (new Date(d.FechaPavimento).toLocaleDateString('es-ES')) : ''}</div>
          </li>`;
        }).join('') + '</ol>';
    }

  });
