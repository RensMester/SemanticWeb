var vectorSource = new ol.source.Vector();
var stepsource = new ol.source.Vector();

var iconStyle = new ol.style.Style({
    image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
    anchor: [0.5, 46],
    anchorXUnits: 'fraction',
    anchorYUnits: 'pixels',
    opacity: 0.75,
    src:'https://cdn1.iconfinder.com/data/icons/Map-Markers-Icons-Demo-PNG/256/Map-Marker-Marker-Outside-Pink.png',
    offset: [0,20],
    scale: 0.15,
    }))
});

var stepStyle = new ol.style.Style({
    image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
    anchor: [0.5, 46],
    anchorXUnits: 'fraction',
    anchorYUnits: 'pixels',
    opacity: 0.75,
    src:'https://cdn0.iconfinder.com/data/icons/gcons-2/9/point1-128.png',
    offset: [0,20],
    scale: 0.15,
    }))
});

var vectorLayer = new ol.layer.Vector({
source: vectorSource,
style: iconStyle,
});

var stepLayer = new ol.layer.Vector({
source: stepsource,
style: stepStyle,
});

var map;
function get_route() {
    var start = $('#inputStart').value();
    var dest = $('#inputDestination').value();
    $.ajax({type: "POST",
            url: '/route',
            data: {'start': start, 'dest': dest},
            success: drawRoute,
    })
}
function drawRoute(data){
    $('#map').empty();

    var on_route = data.on_route;
    var step_points = data.step_points;
    console.log(on_route);
    console.log(step_points);
    var i; //speciaal voor jim
    for (i=0; i<on_route.length; ++i) {
        var iconFeature = new ol.Feature({
            geometry: new
        ol.geom.Point(ol.proj.transform([on_route[i].lon, on_route[i].lat], 'EPSG:4326',   'EPSG:3857')),
        });
        vectorSource.addFeature(iconFeature);
    };

    var i; //speciaal voor jim
    for (i=0; i<step_points.length; ++i) {
        var iconFeature = new ol.Feature({
            geometry: new
        ol.geom.Point(ol.proj.transform([step_points[i][1], step_points[i][0]], 'EPSG:4326',   'EPSG:3857')),
        });
        stepsource.addFeature(iconFeature);
    };

    //create the style
    map = new ol.Map({
            layers: [new ol.layer.Tile({ source: new ol.source.OSM() }), vectorLayer, stepLayer],
            target: document.getElementById('map'),
            view: new ol.View({
                center: [0, 0],
                zoom: 3
            })
            });

}

(function(){
map = new ol.Map({
        layers: [new ol.layer.Tile({ source: new ol.source.OSM() }), vectorLayer, stepLayer],
        target: document.getElementById('map'),
        view: new ol.View({
            center: [0, 0],
            zoom: 3
        })
        });
})();
