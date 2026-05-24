/* static/p_w_pvsa/js/mapa_editor.js */
(function () {
  const container = document.getElementById("mapaEditor");
  if (!container) return;

  if (typeof maplibregl === "undefined") return;

  const MAX_ZOOM = 19;
  const LIMIT_BOUNDS = [
    [-71.5100, -32.7800],
    [-71.4500, -32.7300],
  ];
  const LIMIT_BOUNDS_OBJ = new maplibregl.LngLatBounds(LIMIT_BOUNDS[0], LIMIT_BOUNDS[1]);

  const STYLE_SAT = {
    version: 8,
    sources: {
      sat: {
        type: "raster",
        tiles: [
          "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        ],
        tileSize: 256,
        maxzoom: MAX_ZOOM,
        attribution: "Esri",
      },
    },
    layers: [{ id: "sat", type: "raster", source: "sat" }],
  };

  const map = new maplibregl.Map({
    container: "mapaEditor",
    style: STYLE_SAT,
    center: [-71.484847, -32.752389],
    zoom: 18,
    maxZoom: MAX_ZOOM,
    maxBounds: LIMIT_BOUNDS_OBJ,
    renderWorldCopies: false,
  });

  map.setMaxBounds(LIMIT_BOUNDS_OBJ);
  map.addControl(new maplibregl.NavigationControl(), "top-right");

  const btnMarcar = document.getElementById("btnMarcar");
  const btnDeshacer = document.getElementById("btnDeshacer");
  const btnLimpiar = document.getElementById("btnLimpiar");
  const btnListo = document.getElementById("btnListo");
  const estadoModo = document.getElementById("estadoModo");
  const contador = document.getElementById("contador");
  const geomInput = document.getElementById("geom_json");

  const modalEl = document.getElementById("modalGuardar");
  const modalGuardar = modalEl ? new bootstrap.Modal(modalEl) : null;

  const modalErrEl = document.getElementById("modalErrorGeom");
  const modalError = modalErrEl ? new bootstrap.Modal(modalErrEl) : null;
  const errorMsg = document.getElementById("errorGeomMsg");

  const tipoRegistro = document.getElementById("tipoRegistro");

  const bloqueSector = document.getElementById("bloqueSector");
  const bloqueUbicacion = document.getElementById("bloqueUbicacion");
  const bloqueLugar = document.getElementById("bloqueLugar");

  // lugar_sector
  const bloqueLugarSector = document.getElementById("bloqueLugarSector");
  const lugarSectorSector = document.getElementById("lugarSectorSector");
  const lugarSectorExistente = document.getElementById("lugarSectorExistente");

  const sectorParaUbicacion = document.getElementById("sectorParaUbicacion");
  const ubicacionExistente = document.getElementById("ubicacionExistente");

  // Lugar normal
  const lugarUbicacion = document.getElementById("lugarUbicacion");
  const lugarPiso = document.getElementById("lugarPiso");
  const lugarExistente = document.getElementById("lugarExistente");

  const cfg = document.getElementById("mapa-config");
  const URL_PISOS = cfg?.dataset.urlPisos || "";
  const URL_LUGARES = cfg?.dataset.urlLugares || "";

  const parentSectorId = document.getElementById("parentSectorId");
  const parentUbicacionId = document.getElementById("parentUbicacionId");
  const accion = document.querySelector('input[name="accion"]')?.value || "crear";
  const editarTipo = document.querySelector('input[name="editar_tipo"]')?.value || "";
  const editarId = document.querySelector('input[name="editar_id"]')?.value || "";

  function showError(msg) {
    if (errorMsg) errorMsg.textContent = msg || "Error";
    if (modalError) modalError.show();
  }

  const dataEl = document.getElementById("mapa-data");
  const fc0 = dataEl ? JSON.parse(dataEl.textContent) : { type: "FeatureCollection", features: [] };

  const sectorGeomById = {};
  const ubicGeomById = {};

  (fc0.features || []).forEach((f) => {
    const p = f.properties || {};
    if (!f.geometry) return;

    if (p.kind === "sector") {
      const sid = String(p.id || p.sector_id || "");
      if (sid) sectorGeomById[sid] = f.geometry;
    }

    if (p.kind === "ubicacion") {
      const uid = String(p.id || "");
      if (uid) ubicGeomById[uid] = f.geometry;
    }
  });

  function buildSavedFC() {
    const eid = String(editarId || "");
    const et = String(editarTipo || "");

    const feats = (fc0.features || []).filter((f) => {
      const p = f.properties || {};
      if (!f.geometry) return false;

      if (accion === "editar" && eid && et) {
        if (p.kind === et && String(p.id) === eid) return false;
      }
      return true;
    });

    return { type: "FeatureCollection", features: feats };
  }

  function addSavedOverlay() {
    const savedFC = buildSavedFC();

    if (!map.getSource("saved")) {
      map.addSource("saved", { type: "geojson", data: savedFC });
    } else {
      map.getSource("saved").setData(savedFC);
    }

    if (!map.getLayer("saved-line-glow")) {
      map.addLayer({
        id: "saved-line-glow",
        type: "line",
        source: "saved",
        paint: { "line-color": "#ffff00", "line-opacity": 0.35, "line-width": 10 },
      });
    }

    if (!map.getLayer("saved-line")) {
      map.addLayer({
        id: "saved-line",
        type: "line",
        source: "saved",
        paint: { "line-color": "#fff200", "line-opacity": 1, "line-width": 3.5 },
      });
    }

    if (!map.getLayer("saved-fill")) {
      map.addLayer(
        {
          id: "saved-fill",
          type: "fill",
          source: "saved",
          paint: { "fill-color": "#fff200", "fill-opacity": 0.06 },
        },
        "saved-line-glow"
      );
    }
  }

  function setParentGeom(geom) {
    if (!geom) return;

    if (!map.getSource("parent")) {
      map.addSource("parent", { type: "geojson", data: { type: "Feature", geometry: geom, properties: {} } });
      map.addLayer({ id: "parent-line", type: "line", source: "parent", paint: { "line-color": "#00ffb7", "line-width": 3 } });
      map.addLayer({ id: "parent-fill", type: "fill", source: "parent", paint: { "fill-color": "#00ffb7", "fill-opacity": 0.05 } });
    } else {
      map.getSource("parent").setData({ type: "Feature", geometry: geom, properties: {} });
    }
  }

  function drawParentIfEdit() {
    let parentGeom = null;

    if (accion === "editar") {
      if (editarTipo === "ubicacion") {
        const sid = parentSectorId?.value || "";
        parentGeom = sectorGeomById[String(sid)] || null;
      }

      if (editarTipo === "lugar") {
        const uid = parentUbicacionId?.value || "";
        parentGeom = ubicGeomById[String(uid)] || null;

        // móvil: si no hay ubicación geom, usar sector padre
        if (!parentGeom) {
          const sid = parentSectorId?.value || "";
          parentGeom = sectorGeomById[String(sid)] || null;
        }
      }
    }

    if (parentGeom) setParentGeom(parentGeom);
  }

  function updateBloques() {
    if (!tipoRegistro) return;
    const v = tipoRegistro.value;

    if (bloqueSector) bloqueSector.style.display = v === "sector" ? "" : "none";
    if (bloqueUbicacion) bloqueUbicacion.style.display = v === "ubicacion" ? "" : "none";
    if (bloqueLugar) bloqueLugar.style.display = v === "lugar" ? "" : "none";
    if (bloqueLugarSector) bloqueLugarSector.style.display = v === "lugar_sector" ? "" : "none";
  }

  function filterUbicacionesBySector() {
    if (!sectorParaUbicacion || !ubicacionExistente) return;
    const sid = sectorParaUbicacion.value;

    Array.from(ubicacionExistente.options).forEach((opt) => {
      const s = opt.getAttribute("data-sector");
      if (!s) return;
      opt.hidden = sid ? s !== sid : false;
    });

    if (sid && ubicacionExistente.value) {
      const opt = ubicacionExistente.selectedOptions[0];
      if (opt && opt.hidden) ubicacionExistente.value = "";
    }
  }

  function filterLugaresMovilesBySector() {
    if (!lugarSectorSector || !lugarSectorExistente) return;
    const sid = lugarSectorSector.value;

    Array.from(lugarSectorExistente.options).forEach((opt) => {
      const s = opt.getAttribute("data-sector");
      if (!s) return;
      opt.hidden = sid ? s !== sid : false;
    });

    if (sid && lugarSectorExistente.value) {
      const opt = lugarSectorExistente.selectedOptions[0];
      if (opt && opt.hidden) lugarSectorExistente.value = "";
    }

    // dibujar padre mientras creas contenedor (opcional)
    const parent = sectorGeomById[String(sid)];
    if (parent) setParentGeom(parent);
  }

  async function loadPisosForUbic(ubicId) {
    if (!lugarPiso) return;
    lugarPiso.innerHTML = `<option value="">-- seleccionar --</option>`;
    if (!ubicId || !URL_PISOS) return;

    try {
      const res = await fetch(`${URL_PISOS}?ubicacion_id=${encodeURIComponent(ubicId)}`, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();

      data.forEach((p) => {
        const opt = document.createElement("option");
        opt.value = p.id;
        opt.textContent = p.nombre;
        lugarPiso.appendChild(opt);
      });
    } catch (e) {}
  }

  async function loadLugaresForPiso(pisoId) {
    if (!lugarExistente) return;
    lugarExistente.innerHTML = `<option value="">-- seleccionar --</option>`;
    if (!pisoId || !URL_LUGARES) return;

    try {
      const res = await fetch(`${URL_LUGARES}?piso_id=${encodeURIComponent(pisoId)}`, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();

      data.forEach((l) => {
        const opt = document.createElement("option");
        opt.value = l.id;
        opt.textContent = l.nombre;
        lugarExistente.appendChild(opt);
      });
    } catch (e) {}
  }

  if (tipoRegistro) tipoRegistro.addEventListener("change", updateBloques);
  if (sectorParaUbicacion) sectorParaUbicacion.addEventListener("change", filterUbicacionesBySector);

  if (lugarSectorSector) lugarSectorSector.addEventListener("change", filterLugaresMovilesBySector);

  if (lugarUbicacion) {
    lugarUbicacion.addEventListener("change", async () => {
      const uid = lugarUbicacion.value;
      await loadPisosForUbic(uid);
      await loadLugaresForPiso("");
      // dibujar padre ubicación (si tiene geom)
      const parent = ubicGeomById[String(uid)];
      if (parent) setParentGeom(parent);
    });
  }
  if (lugarPiso) {
    lugarPiso.addEventListener("change", async () => {
      await loadLugaresForPiso(lugarPiso.value);
    });
  }

  let points = [];
  let marking = false;

  function setCount() {
    if (contador) contador.textContent = `Puntos: ${points.length}`;
  }
  function setModeLabel() {
    if (!estadoModo) return;
    estadoModo.textContent = `Modo: ${marking ? "ON (click en el mapa)" : "OFF"}`;
  }
  function setCursor() {
    map.getCanvas().style.cursor = marking ? "crosshair" : "";
  }

  function geoPoints() {
    return {
      type: "FeatureCollection",
      features: points.map((p, i) => ({
        type: "Feature",
        geometry: { type: "Point", coordinates: p },
        properties: { idx: i + 1 },
      })),
    };
  }

  function geoLineOrPoly() {
    if (points.length < 2) return { type: "FeatureCollection", features: [] };

    if (points.length < 3) {
      return {
        type: "FeatureCollection",
        features: [{ type: "Feature", geometry: { type: "LineString", coordinates: points }, properties: {} }],
      };
    }

    const ring = points.concat([points[0]]);
    return {
      type: "FeatureCollection",
      features: [{ type: "Feature", geometry: { type: "Polygon", coordinates: [ring] }, properties: {} }],
    };
  }

  function polygonGeometry() {
    if (points.length < 3) return null;
    const ring = points.concat([points[0]]);
    return { type: "Polygon", coordinates: [ring] };
  }

  function refreshDraw() {
    setCount();
    const srcPts = map.getSource("pts");
    const srcShape = map.getSource("shape");
    if (srcPts) srcPts.setData(geoPoints());
    if (srcShape) srcShape.setData(geoLineOrPoly());
  }

  function clearAll() {
    points = [];
    refreshDraw();
  }

  function undo() {
    points.pop();
    refreshDraw();
  }

  function ensureDrawLayers() {
    if (!map.getSource("pts")) map.addSource("pts", { type: "geojson", data: geoPoints() });
    if (!map.getSource("shape")) map.addSource("shape", { type: "geojson", data: geoLineOrPoly() });

    if (!map.getLayer("shape-fill")) {
      map.addLayer({ id: "shape-fill", type: "fill", source: "shape", paint: { "fill-color": "#06b6b9", "fill-opacity": 0.25 } });
    }
    if (!map.getLayer("shape-line")) {
      map.addLayer({ id: "shape-line", type: "line", source: "shape", paint: { "line-color": "#06b6b9", "line-width": 3 } });
    }
    if (!map.getLayer("pts-layer")) {
      map.addLayer({ id: "pts-layer", type: "circle", source: "pts", paint: { "circle-radius": 6, "circle-color": "#ef4444" } });
    }
    if (!map.getLayer("pts-label")) {
      map.addLayer({ id: "pts-label", type: "symbol", source: "pts", layout: { "text-field": ["get", "idx"], "text-size": 12, "text-offset": [0, -1.2] } });
    }
  }

  function loadInitialGeomIfAny() {
    const el = document.getElementById("geom-inicial");
    if (!el) return;

    try {
      const geom = JSON.parse(el.textContent);
      const ring = geom?.coordinates?.[0] || [];
      if (ring.length >= 4) {
        points = ring.slice(0, ring.length - 1);
        refreshDraw();
      }
    } catch (e) {}
  }

  function validateWithinParent(geom) {
    if (!geom) return { ok: false, msg: "Geometría inválida." };
    if (typeof turf === "undefined") return { ok: true };

    const child = { type: "Feature", geometry: geom, properties: {} };

    if (accion === "editar") {
      if (editarTipo === "ubicacion") {
        const sid = parentSectorId?.value || "";
        const parentGeom = sectorGeomById[String(sid)];
        if (!parentGeom) return { ok: false, msg: "No encontré el polígono del Sector padre." };
        const parent = { type: "Feature", geometry: parentGeom, properties: {} };
        return turf.booleanWithin(child, parent) ? { ok: true } : { ok: false, msg: "Debe quedar completamente dentro del Sector (padre)." };
      }

      if (editarTipo === "lugar") {
        const uid = parentUbicacionId?.value || "";
        const sid = parentSectorId?.value || "";

        const parentGeomU = ubicGeomById[String(uid)];
        if (parentGeomU) {
          const parent = { type: "Feature", geometry: parentGeomU, properties: {} };
          return turf.booleanWithin(child, parent) ? { ok: true } : { ok: false, msg: "El Lugar debe quedar completamente dentro de la Ubicación (padre)." };
        }

        const parentGeomS = sectorGeomById[String(sid)];
        if (!parentGeomS) return { ok: false, msg: "No encontré el polígono del Sector padre." };
        const parent = { type: "Feature", geometry: parentGeomS, properties: {} };
        return turf.booleanWithin(child, parent) ? { ok: true } : { ok: false, msg: "El contenedor debe quedar completamente dentro del Sector (padre)." };
      }

      return { ok: true };
    }

    const tr = tipoRegistro?.value || "sector";

    if (tr === "ubicacion") {
      const sid = sectorParaUbicacion?.value || "";
      const parentGeom = sectorGeomById[String(sid)];
      if (!parentGeom) return { ok: false, msg: "El Sector seleccionado NO tiene polígono. Primero dibuja el Sector." };
      const parent = { type: "Feature", geometry: parentGeom, properties: {} };
      return turf.booleanWithin(child, parent) ? { ok: true } : { ok: false, msg: "La Ubicación debe quedar completamente dentro del Sector seleccionado." };
    }

    if (tr === "lugar") {
      const uid = lugarUbicacion?.value || "";
      const parentGeom = ubicGeomById[String(uid)];
      if (!parentGeom) return { ok: false, msg: "La Ubicación seleccionada NO tiene polígono. Primero dibuja la Ubicación." };
      const parent = { type: "Feature", geometry: parentGeom, properties: {} };
      return turf.booleanWithin(child, parent) ? { ok: true } : { ok: false, msg: "El Lugar debe quedar completamente dentro de la Ubicación seleccionada." };
    }

    if (tr === "lugar_sector") {
      const sid = lugarSectorSector?.value || "";
      const parentGeom = sectorGeomById[String(sid)];
      if (!parentGeom) return { ok: false, msg: "El Sector seleccionado NO tiene polígono. Primero dibuja el Sector." };
      const parent = { type: "Feature", geometry: parentGeom, properties: {} };
      return turf.booleanWithin(child, parent) ? { ok: true } : { ok: false, msg: "El contenedor debe quedar completamente dentro del Sector seleccionado." };
    }

    return { ok: true };
  }

  map.on("load", () => {
    addSavedOverlay();
    ensureDrawLayers();
    refreshDraw();
    setModeLabel();
    setCursor();

    updateBloques();
    filterUbicacionesBySector();
    filterLugaresMovilesBySector();
    loadInitialGeomIfAny();
    drawParentIfEdit();

    map.fitBounds(LIMIT_BOUNDS, { padding: 30, maxZoom: MAX_ZOOM });
  });

  map.on("click", (e) => {
    if (!marking) return;
    points.push([e.lngLat.lng, e.lngLat.lat]);
    refreshDraw();
  });

  if (btnMarcar) {
    btnMarcar.addEventListener("click", () => {
      marking = !marking;
      setModeLabel();
      setCursor();

      btnMarcar.classList.toggle("btn-outline-primary", !marking);
      btnMarcar.classList.toggle("btn-primary", marking);
      btnMarcar.textContent = marking ? "MARCADO ON (CLICK EN MAPA)" : "ACTIVAR MARCADO (CLICK)";
    });
  }

  if (btnDeshacer) btnDeshacer.addEventListener("click", undo);
  if (btnLimpiar) btnLimpiar.addEventListener("click", clearAll);

  if (btnListo) {
    btnListo.addEventListener("click", () => {
      const geom = polygonGeometry();
      if (!geom) {
        showError("Debes marcar al menos 3 puntos para formar un polígono.");
        return;
      }

      const v = validateWithinParent(geom);
      if (!v.ok) {
        showError(v.msg);
        return;
      }

      if (geomInput) geomInput.value = JSON.stringify(geom);
      if (modalGuardar) modalGuardar.show();
    });
  }
})();