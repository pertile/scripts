<>
<script src="https://api.mapbox.com/mapbox-gl-js/v1.2.0/mapbox-gl.js"></script>
<link href="/mapbox-gl.css" rel="stylesheet">
<style>
/**
* Create a position for the map
* on the page */
#VillaGesellMarChiquita { position: relative; height:400px; width:100%; }

/**
* Set rules for how the map overlays
* (information box and legend) will be displayed
* on the page. */
.VillaGesellMarChiquita-overlay {
  position: absolute;
//  margin-right: 20px;
  background: rgba(255, 255, 255, 0.5);
  font-family: Arial, sans-serif;
  overflow: auto;
  border-radius: 3px;
}

#features {
  position: absolute;  
  height: 170px;
  right: 20px;
  top: 200px;
  width: 300px;
z-index: 5;
}

#legend {
  padding: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  line-height: 18px;
  height: 150px;
  margin-top: 40px;
  width: 100px;
}

#legend-checkbox {
  padding: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  line-height: 18px;
  height: 150px;
  margin-top: 40px;
  width: 100px;
}

.legend-key {
  display: inline-block;
  border-radius: 20%;
  width: 10px;
  height: 10px;
  margin-right: 5px;
}

</style>

<div id="VillaGesellMarChiquita"><div class="VillaGesellMarChiquita-</script>overlay" id="features"><h2>Leyenda</h2></div></div>

<script>
mapboxgl.accessToken = 'pk.eyJ1IjoicGVydGlsZSIsImEiOiJjaWhqa2Fya2gwbmhtdGNsemtuaW14YmNlIn0.67aoJXemP7021X6XxsF71g';
var VillaGesellMarChiquita = new mapboxgl.Map({
container: 'VillaGesellMarChiquita',
style: 'mapbox://styles/mapbox/streets-v11',
center: [-63.6456,-22.4727],
zoom: 10,
});

const lines = [
    { id: 'B11-1', name: 'Tartagal - Misión Kilómetro 6', color: '#ff0000' },
    { id: 'A86-2', name: 'Kilómetro 6 - Kilómetro 17', color: '#008000' },
    { id: 'B11-3', name: 'Kilómetro 17 - río Itiyuro', color: '#B695C0' },
];

let activeLines = lines.map(line => line.id);

VillaGesellMarChiquita.on('load', function () {
    VillaGesellMarChiquita.addLayer({
        id: 'obras',
        type: 'line',
        source: {
            type: 'geojson',
            data: '/viable.geojson'
        },
        "layout": {
    "line-join": "round",
    "line-cap": "round"
        },
        'paint': {
    'line-color': ['match', ['get', 'Clave'], ...lines.flat().map(line => [line.id, line.color]).flat(), '#ffffff'],
    "line-width": 8
        },
    "filter": ['match', ['get', 'Clave'], lines.map(line => line.id), true, false]
    });
     
lines.forEach(line => {
  var item = document.createElement('div');
  var key = document.createElement('span');
  key.className = 'legend-key';
  key.style.backgroundColor = line.color;

  var value = document.createElement('span');
  value.style.fontSize = '12px';
  value.innerHTML = line.name;

  var checkbox = document.createElement('input');
  checkbox.type = 'checkbox';
  checkbox.className = 'legend-checkbox';
  checkbox.checked = true;
  checkbox.onchange = function() {
      if (checkbox.checked) {
          activeLines.push(line.id);
      } else {
          activeLines = activeLines.filter(id => id !== line.id);
      }
      VillaGesellMarChiquita.setFilter('obras', ['match', ['get', 'Clave'], activeLines, true, false]);
  };

  item.appendChild(checkbox);
  item.appendChild(key);
  item.appendChild(value);
  features.appendChild(item);
});
    
});
</script>
</>