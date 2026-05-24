(function () {
  const STYLE = {
    version: 8,
    sources: {
      sat: {
        type: "raster",
        tiles: ["https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"],
        tileSize: 256,
        attribution: "Esri"
      }
    },
    layers: [{ id: "sat", type: "raster", source: "sat" }]
  };

  const map = new maplibregl.Map({
    container: "map",
    style: STYLE,
    center: [-71.484847, -32.752389],
    zoom: 17
  });

  map.addControl(new maplibregl.NavigationControl(), "top-right");
})();