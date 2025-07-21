// JavaScript code for map and features

mapboxgl.accessToken = 'pk.eyJ1IjoicGVydGlsZSIsImEiOiJjaWhqa2Fya2gwbmhtdGNsemtuaW14YmNlIn0.67aoJXemP7021X6XxsF71g';
// Referencia a la hoja de estilos obras-en-curso.css
const cssLink = document.createElement('link');
cssLink.rel = 'stylesheet';
cssLink.href = '/obras-en-curso.css';
document.head.appendChild(cssLink);

var mapGranResistencia = new mapboxgl.Map({
  container: 'mapGranResistencia',
  center: [-59.0058,-27.4348],
  zoom: 11.5, // default zoom that will be overridden after load
  bearing: 45,
  style: '/Resistencia.json'
});
mapGranResistencia.on('load', function () {
    mapGranResistencia.addLayer({
        id: 'obras',
        type: 'line',
        source: {
            type: 'geojson',
            data: '/Obras GeoResistencia.geojson'
        },
        "layout": {
            "line-join": "round",
            "line-cap": "round"
        },
        'paint': {
            'line-color': '#ff0000',
            'line-width': 4
        },
        "filter": ["==", ["get", "surface"], "construction"]
    });
});

var layers = ['Obra nueva', 'Obra en ejecución', 'Calles pavimentadas', 'Calles de tierra', 'Avenidas pavimentadas', 'Avenidas de tierra'];
var colors = ['#ff0000', '#009900', '#907e7d', '#FFFFFF', '#f3c4aa', '#f3f0b7'];

// Add checkbox controls
fetch('/Obras GeoResistencia.geojson')
    .then(response => response.json())
    .then(data => {
        const constructionFeatures = data.features.filter(f => f.properties.surface === 'construction');
        const groupedByObra = constructionFeatures.reduce((acc, feature) => {
          const obra = feature.properties.Obra;
          if (!acc[obra]) {
            acc[obra] = {
              features: [],
              bounds: new mapboxgl.LngLatBounds()
            };
          }
          acc[obra].features.push({
            coordinates: feature.geometry.coordinates,
            properties: feature.properties
          });

          // Extend bounds for LineString
          if (feature.geometry.type === 'LineString') {
            feature.geometry.coordinates.forEach(coord => {
              acc[obra].bounds.extend(coord);
            });
          }
          // Extend bounds for MultiLineString
          else if (feature.geometry.type === 'MultiLineString') {
            feature.geometry.coordinates.forEach(line => {
              line.forEach(coord => {
                acc[obra].bounds.extend(coord);
              });
            });
          }

          return acc;
        }, {});
        Object.entries(groupedByObra).forEach(([obraName, obraData]) => {
          const center = obraData.bounds.getCenter();
          const el = document.createElement('div');
          const data = obraData.features[0].properties;
          el.className = 'construction-marker';
          el.innerHTML = '<i class="fas fa-person-digging" style="font-size: 24px;"></i>';
          const marker = new mapboxgl.Marker({
              element: el,
              anchor: 'center',
              draggable: false,
          })
            .setLngLat(center)
            .addTo(mapGranResistencia);

          // Create popup with close button enabled
          const popup = new mapboxgl.Popup({
            closeButton: true,
            closeOnClick: true
            }).setHTML(`<h2><a href="${data.link_progress}" target="_blank">${data.type}: ${data.title}</a></h2><h3>${data.municipality}</h3><h3>Longitud: ${data.length}&nbsp;m ${data.estimated ? '(estimado)' : ''}</h3><p>${data.short_description}</p><p>Fecha de inicio: ${(new Date(data.start).toLocaleDateString('es-ES', { day: '2-digit', month: 'long', year: 'numeric' }))}</p>`);

          // Show popup on mouse enter
          marker.getElement().addEventListener('mouseenter', () => {
            popup.setLngLat(center).addTo(mapGranResistencia);
          });

          // Hide popup on mouse leave
          // Add mouseenter event listener to the popup element when it's added to the map
          popup.on('open', () => {
            const popupElement = popup.getElement();
            popupElement.addEventListener('mouseleave', () => {
              popup.remove();
            });
          });

          // Add click handler for zoom
          marker.getElement().addEventListener('click', () => {
            mapGranResistencia.fitBounds(obraData.bounds, {
              padding: 50,
              duration: 1000,
              bearing: 45
            });
          });
        });

        // --- Agregar lista de obras dentro de un div específico ---
        let listaObrasContainer = document.getElementById('lista-obras-container');
        if (!listaObrasContainer) {
          listaObrasContainer = document.createElement('div');
          listaObrasContainer.id = 'lista-obras-container';
          // Insertar después del mapa si existe, si no al final del body
          const mapaDiv = document.getElementById('mapGranResistencia');
          if (mapaDiv && mapaDiv.parentNode) {
            mapaDiv.parentNode.insertBefore(listaObrasContainer, mapaDiv.nextSibling);
          } else {
            document.body.appendChild(listaObrasContainer);
          }
        }
        // --- Listado principal con separadores ---
        const listaObras = document.createElement('div');
        listaObras.id = 'lista-obras';
        listaObras.innerHTML = '<h2>Listado de obras en ejecución</h2>' +
          Object.entries(groupedByObra).map(([obraName, obraData], idx, arr) => {
            const data = obraData.features[0].properties;
            return `
              <div style="margin-bottom:1.5em;">
                <h3><a href="${data.link_progress}" target="_blank">${data.type}: ${data.title}</a></h3>
                <div><strong>Municipio:</strong> ${data.municipality}</div>
                <div><strong>Longitud:</strong> ${data.length}&nbsp;m ${data.estimated ? '(estimado)' : ''}</div>
                <div><strong>Descripción:</strong> ${data.short_description}</div>
                <div><strong>Fecha de inicio:</strong> ${(new Date(data.start).toLocaleDateString('es-ES', { day: '2-digit', month: 'long', year: 'numeric' }))}</div>
                <div style="margin-top:0.5em;"><em>Nota: <a href="${data.link_progress}" target="_blank">Ver avance de obra</a></em></div>
                ${idx < arr.length - 1 ? '<hr style="margin:1.5em 0;">' : ''}
              </div>
            `;
          }).join('');
        listaObrasContainer.appendChild(listaObras);

        // --- Listado lateral derecho de obras ---
        let listaObrasLateral = document.getElementById('lista-obras-lateral');
        if (!listaObrasLateral) {
          listaObrasLateral = document.createElement('div');
          listaObrasLateral.id = 'lista-obras-lateral';
          listaObrasLateral.style.position = 'fixed';
          listaObrasLateral.style.top = '80px';
          listaObrasLateral.style.right = '0';
          listaObrasLateral.style.width = '320px';
          listaObrasLateral.style.maxHeight = '80vh';
          listaObrasLateral.style.overflowY = 'auto';
          listaObrasLateral.style.background = '#fff';
          listaObrasLateral.style.borderLeft = '2px solid #eee';
          listaObrasLateral.style.boxShadow = '-2px 0 8px #0001';
          listaObrasLateral.style.zIndex = '9999';
          listaObrasLateral.style.padding = '1em';
          document.body.appendChild(listaObrasLateral);
        }
        // Limpiar y agregar listado de títulos
        listaObrasLateral.innerHTML = '<h2>Obras</h2>' +
          '<ul style="list-style:none; padding:0;">' +
          Object.entries(groupedByObra).map(([obraName, obraData], idx) => {
            const data = obraData.features[0].properties;
            return `<li style="margin-bottom:0.7em;">
              <a href="#" style="font-weight:bold; color:#0074d9; text-decoration:underline;" data-obra="${obraName}">${data.title}</a>
            </li>`;
          }).join('') + '</ul>';

        // Agregar evento para hacer zoom al hacer clic en el título
        listaObrasLateral.querySelectorAll('a[data-obra]').forEach(a => {
          a.addEventListener('click', function(e) {
            e.preventDefault();
            const obraName = this.getAttribute('data-obra');
            const obraData = groupedByObra[obraName];
            if (obraData && obraData.bounds) {
              mapGranResistencia.fitBounds(obraData.bounds, {
                padding: 50,
                duration: 1000,
                bearing: 45
              });
            }
          });
        });
    });