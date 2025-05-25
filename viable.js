<>
<script src="https://api.mapbox.com/mapbox-gl-js/v1.2.0/mapbox-gl.js"></script>
<link href="/mapbox-gl.css" rel="stylesheet">
<style>
/**
* Create a position for the map
* on the page */
#B112_12 { position: relative; height:400px; width:100%; }

/**
* Set rules for how the map overlays
* (information box and legend) will be displayed
* on the page. */
.B112_12-overlay {
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
top: 20px;
  width: 200px;
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

.legend-key {
  display: inline-block;
  border-radius: 20%;
  width: 10px;
  height: 10px;
  margin-right: 5px;
}

</style>

<div id="B112_12"><div class="B112_12-overlay" id="features"><h2>Leyenda</h2></div></div>

<script>
mapboxgl.accessToken = 'pk.eyJ1IjoicGVydGlsZSIsImEiOiJjaWhqa2Fya2gwbmhtdGNsemtuaW14YmNlIn0.67aoJXemP7021X6XxsF71g';
var B112_12 = new mapboxgl.Map({
container: 'B112_12',
style: 'mapbox://styles/mapbox/streets-v11',
center: [-62.584620560982216,-38.873789654100186],
zoom: 9,
});

const lines = [
    {"id": "B112-12", "name": "M\u00e9danos - Ombucta", "color": "#ff0000", "lat": -38.873789654100186, "long": -62.584620560982216}
];

B112_12.on('load', function () {
    B112_12.addLayer({
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
    item.appendChild(key);
    item.appendChild(value);
    features.appendChild(item);
});
    
});
</script>
</>