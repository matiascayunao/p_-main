/* static/p_w_pvsa/js/mapa_admin.js */
(function () {
  if (typeof maplibregl === "undefined") return;

  const MAX_ZOOM = 19;

  const LIMIT_BOUNDS = [
    [-71.5100, -32.7800], // SW
    [-71.4500, -32.7300], // NE
  ];
  const LIMIT_BOUNDS_OBJ = new maplibregl.LngLatBounds(LIMIT_BOUNDS[0], LIMIT_BOUNDS[1]);

  const STYLE = {
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

  const el = document.getElementById("mapa-data");
  const fc0 = el ? JSON.parse(el.textContent) : { type: "FeatureCollection", features: [] };

  // ids estables para feature-state
  const fc = {
    type: "FeatureCollection",
    features: (fc0.features || []).map((f) => {
      const p = f.properties || {};
      const id =
        p.kind === "sector"
          ? `sector-${p.sector_id || p.id}`
          : p.kind === "ubicacion"
          ? `ubicacion-${p.id}`
          : p.kind === "lugar"
          ? `lugar-${p.id}`
          : `x-${Math.random().toString(16).slice(2)}`;
      return { ...f, id };
    }),
  };

  const map = new maplibregl.Map({
    container: "mapaAdmin",
    style: STYLE,
    center: [-71.484847, -32.752389],
    zoom: 15,
    maxZoom: MAX_ZOOM,
    maxBounds: LIMIT_BOUNDS_OBJ,
    renderWorldCopies: false,
  });

  map.addControl(new maplibregl.NavigationControl(), "top-right");
  map.setMaxBounds(LIMIT_BOUNDS_OBJ);

  const vistaSel = document.getElementById("mapVista");
  const sectorSel = document.getElementById("mapSector");
  const ubicSel = document.getElementById("mapUbicacion");
  const btnLimpiar = document.getElementById("btnLimpiar");
  const lista = document.getElementById("listaFeatures");

  let popup = null;

  let statsSector = {};
  let statsUbic = {};
  let statsLugar = {};

  function clamp(n, a, b) {
    return Math.max(a, Math.min(b, n));
  }

  function hexToRgb(h) {
    const x = (h || "").replace("#", "").trim();
    const v = x.length === 3 ? x.split("").map((c) => c + c).join("") : x;
    return {
      r: parseInt(v.slice(0, 2), 16),
      g: parseInt(v.slice(2, 4), 16),
      b: parseInt(v.slice(4, 6), 16),
    };
  }

  function rgbToHex(r, g, b) {
    const f = (n) => n.toString(16).padStart(2, "0");
    return `#${f(r)}${f(g)}${f(b)}`;
  }

  function mixHex(a, b, t) {
    const pa = hexToRgb(a),
      pb = hexToRgb(b);
    const r = Math.round(pa.r + (pb.r - pa.r) * t);
    const g = Math.round(pa.g + (pb.g - pa.g) * t);
    const bl = Math.round(pa.b + (pb.b - pa.b) * t);
    return rgbToHex(r, g, bl);
  }

  function colorForPct(pct) {
    if (pct === null || pct === undefined || pct === "") return "#64748b";
    pct = Number(pct);
    if (!isFinite(pct)) return "#64748b";

    if (pct >= 65) {
      const t = (clamp(pct, 65, 100) - 65) / 35;
      return mixHex("#86efac", "#16a34a", t);
    }
    if (pct >= 50) return "#facc15";

    const t = clamp(pct, 0, 49) / 49;
    return mixHex("#7f1d1d", "#f87171", t);
  }

  function badgeForPct(pct) {
    if (pct === null || pct === undefined || pct === "") {
      return { label: "Sin datos", color: "#64748b" };
    }
    pct = Number(pct);
    if (!isFinite(pct)) return { label: "Sin datos", color: "#64748b" };
    return { label: `${pct}% Bueno`, color: colorForPct(pct) };
  }

  function coordsFromGeom(geom) {
    if (!geom) return [];
    if (geom.type === "Polygon") {
      const out = [];
      (geom.coordinates || []).forEach((ring) => (ring || []).forEach((c) => out.push(c)));
      return out;
    }
    if (geom.type === "MultiPolygon") {
      const out = [];
      (geom.coordinates || []).forEach((poly) => {
        (poly || []).forEach((ring) => (ring || []).forEach((c) => out.push(c)));
      });
      return out;
    }
    return [];
  }

  function bboxFromGeom(geom) {
    const coords = coordsFromGeom(geom);
    let minX = 999,
      minY = 999,
      maxX = -999,
      maxY = -999;

    coords.forEach(([x, y]) => {
      if (typeof x !== "number" || typeof y !== "number") return;
      minX = Math.min(minX, x);
      minY = Math.min(minY, y);
      maxX = Math.max(maxX, x);
      maxY = Math.max(maxY, y);
    });

    if (minX === 999) return null;
    return [
      [minX, minY],
      [maxX, maxY],
    ];
  }

  function bboxOfFeatureCollection(fcX) {
    let minX = 999,
      minY = 999,
      maxX = -999,
      maxY = -999;

    (fcX.features || []).forEach((f) => {
      const bb = bboxFromGeom(f.geometry);
      if (!bb) return;
      minX = Math.min(minX, bb[0][0]);
      minY = Math.min(minY, bb[0][1]);
      maxX = Math.max(maxX, bb[1][0]);
      maxY = Math.max(maxY, bb[1][1]);
    });

    if (minX === 999) return null;
    return [
      [minX, minY],
      [maxX, maxY],
    ];
  }

  function intersectBbox(bb, limit) {
    const sw = [
      Math.max(bb[0][0], limit[0][0]),
      Math.max(bb[0][1], limit[0][1]),
    ];
    const ne = [
      Math.min(bb[1][0], limit[1][0]),
      Math.min(bb[1][1], limit[1][1]),
    ];
    if (sw[0] > ne[0] || sw[1] > ne[1]) return null;
    return [sw, ne];
  }

  function safeFitBounds(bb, padding = 60, maxZoom = MAX_ZOOM) {
    const safe = bb ? intersectBbox(bb, LIMIT_BOUNDS) : null;
    map.fitBounds(safe || LIMIT_BOUNDS, { padding, maxZoom });
    map.setMaxBounds(LIMIT_BOUNDS_OBJ);
  }

  function zoomToFeature(f) {
    const bb = bboxFromGeom(f.geometry);
    safeFitBounds(bb, 60, MAX_ZOOM);
  }

  function getPctBuenasFromFeature(f) {
    const p = f.properties || {};
    if (p.kind === "sector") return statsSector[String(p.sector_id || p.id)]?.pct_buenas ?? null;
    if (p.kind === "ubicacion") return statsUbic[String(p.id)]?.pct_buenas ?? null;
    if (p.kind === "lugar") return statsLugar[String(p.id)]?.pct_buenas ?? null;
    return null;
  }

  function popupForFeature(f, lngLat) {
    const p = f.properties || {};
    const pct = getPctBuenasFromFeature(f);
    const badge = badgeForPct(pct);

    const kindLabel =
      p.kind === "sector" ? "SECTOR" :
      p.kind === "ubicacion" ? "UBICACIÓN" :
      p.kind === "lugar" ? (p.is_movil ? "CONTENEDOR / MÓVIL" : "LUGAR") :
      (p.kind || "").toUpperCase();

    let sub = "";
    if (p.kind === "ubicacion") sub = p.sector_name || "";
    if (p.kind === "lugar") {
      if (p.is_movil) {
        sub = `Sector ${p.sector_name || ""}`;
      } else {
        sub = `${p.ubicacion_name ? (p.ubicacion_name + " · ") : ""}Piso ${p.piso ?? "-"}`;
      }
    }

    const html = `
      <div style="min-width:240px">
        <div class="d-flex justify-content-between align-items-start gap-2">
          <div>
            <div class="fw-semibold mb-1">${p.name || "-"}</div>
            <div class="small text-muted">${kindLabel}${sub ? " · " + sub : ""}</div>
          </div>
          <span style="
            font-size:12px;
            color:white;
            background:${badge.color};
            padding:4px 8px;
            border-radius:999px;
            white-space:nowrap;
          ">${badge.label}</span>
        </div>

        ${
          pct === null || pct === undefined
            ? `<div class="small text-muted mt-2">Sin datos para calcular % Bueno</div>`
            : `
              <div class="mt-2">
                <div class="d-flex justify-content-between small">
                  <span class="text-muted">Calidad</span>
                  <span class="fw-semibold">${pct}% Bueno</span>
                </div>
                <div style="height:10px; background:#e5e7eb; border-radius:999px; overflow:hidden;">
                  <div style="width:${Math.max(0, Math.min(100, pct))}%; height:10px; background:${badge.color};"></div>
                </div>
              </div>
            `
        }

        <div class="d-grid gap-1 mt-3">
          ${p.detail_url ? `<a class="btn btn-sm btn-outline-primary" href="${p.detail_url}">Detalles</a>` : ""}
          ${p.edit_geom_url ? `<a class="btn btn-sm btn-primary" href="${p.edit_geom_url}">Editar polígono</a>` : ""}
        </div>
      </div>
    `;

    if (popup) popup.remove();
    popup = new maplibregl.Popup({ closeOnClick: true, maxWidth: "260px" })
      .setLngLat(lngLat || map.getCenter())
      .setHTML(html)
      .addTo(map);
  }

  function renderList(features) {
    if (!lista) return;

    lista.innerHTML = "";
    if (!features.length) {
      lista.innerHTML = `<div class="text-muted small">No hay polígonos guardados aún.</div>`;
      return;
    }

    features.forEach((f) => {
      const p = f.properties || {};

      const kind =
        p.kind === "sector" ? "SECTOR" :
        p.kind === "ubicacion" ? "UBICACIÓN" :
        p.kind === "lugar" ? (p.is_movil ? "MÓVIL" : "LUGAR") :
        "OTRO";

      const pct = getPctBuenasFromFeature(f);
      const badge = badgeForPct(pct);

      const sub =
        p.kind === "sector" ? "" :
        p.kind === "ubicacion" ? (p.sector_name || "") :
        p.kind === "lugar" ? (p.is_movil ? (p.sector_name || "") : (p.ubicacion_name || "")) :
        "";

      const item = document.createElement("a");
      item.href = "javascript:void(0)";
      item.className = "list-group-item list-group-item-action";
      item.innerHTML = `
        <div class="d-flex justify-content-between align-items-center gap-2">
          <div>
            <div class="fw-semibold">${p.name || "-"}</div>
            <div class="small text-muted">${kind}${sub ? " · " + sub : ""}</div>
          </div>
          <span style="
            font-size:12px;
            color:white;
            background:${badge.color};
            padding:4px 8px;
            border-radius:999px;
          ">${badge.label}</span>
        </div>
      `;
      item.addEventListener("click", () => {
        zoomToFeature(f);
        popupForFeature(f);
      });
      lista.appendChild(item);
    });
  }

  function setPctStates(features) {
    (fc.features || []).forEach((f) => {
      try {
        map.setFeatureState({ source: "polys", id: f.id }, { hasPct: false, pct: null });
      } catch (e) {}
    });

    (features || []).forEach((f) => {
      const pct = getPctBuenasFromFeature(f);
      const has = pct !== null && pct !== undefined && isFinite(Number(pct));
      try {
        map.setFeatureState(
          { source: "polys", id: f.id },
          { hasPct: has, pct: has ? Number(pct) : null }
        );
      } catch (e) {}
    });
  }

  function applyFilters() {
    if (!vistaSel || !sectorSel || !ubicSel) return;

    const vista = vistaSel.value; // todo/sector/ubicacion
    const sectorId = sectorSel.value;
    const ubicId = ubicSel.value;

    Array.from(ubicSel.options).forEach((opt) => {
      const s = opt.getAttribute("data-sector");
      if (!s) return;
      opt.hidden = sectorId ? s !== sectorId : false;
    });

    if (sectorId && ubicSel.value) {
      const opt = ubicSel.selectedOptions[0];
      if (opt && opt.hidden) ubicSel.value = "";
    }

    const filtered = (fc.features || []).filter((f) => {
      const p = f.properties || {};

      if (vista !== "todo" && p.kind !== vista) return false;

      if (sectorId && String(p.sector_id) !== String(sectorId)) return false;

      // si eligen una ubicación: mostrar esa ubicación + sus lugares (incluye móviles si pertenecen a esa ubicación especial)
      if (ubicId) {
        if (p.kind === "sector") return false;
        if (p.kind === "ubicacion" && String(p.id) !== String(ubicId)) return false;
        if (p.kind === "lugar" && String(p.ubicacion_id || "") !== String(ubicId)) return false;
      }

      return true;
    });

    const out = { type: "FeatureCollection", features: filtered };

    const src = map.getSource("polys");
    if (src) src.setData(out);

    setPctStates(filtered);
    renderList(filtered);

    const bb = bboxOfFeatureCollection(out);
    safeFitBounds(bb, 60, MAX_ZOOM);
  }

  async function loadStats() {
    try {
      const res = await fetch("stats/", {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();

      statsSector = data.sector || {};
      statsUbic = data.ubicacion || {};
      statsLugar = data.lugar || {};
    } catch (e) {
      console.error("No se pudieron cargar stats del mapa:", e);
      statsSector = {};
      statsUbic = {};
      statsLugar = {};
    }
  }

  map.on("load", async () => {
    map.addSource("polys", { type: "geojson", data: fc });

    const fallbackFillByKind = [
      "case",
      ["==", ["get", "kind"], "sector"], "#06b6b9",
      ["==", ["get", "kind"], "ubicacion"], "#0d6efd",
      ["==", ["get", "kind"], "lugar"], "#a855f7",
      "#64748b"
    ];

    const fallbackLineByKind = [
      "case",
      ["==", ["get", "kind"], "sector"], "#0f172a",
      ["==", ["get", "kind"], "ubicacion"], "#0b5ed7",
      ["==", ["get", "kind"], "lugar"], "#7c3aed",
      "#0f172a"
    ];

    map.addLayer({
      id: "fill",
      type: "fill",
      source: "polys",
      paint: {
        "fill-color": [
          "case",
          ["==", ["feature-state", "hasPct"], true],
          [
            "case",
            [">=", ["feature-state", "pct"], 65],
            ["interpolate", ["linear"], ["feature-state", "pct"], 65, "#86efac", 100, "#16a34a"],
            [">=", ["feature-state", "pct"], 50],
            ["interpolate", ["linear"], ["feature-state", "pct"], 50, "#facc15", 65, "#facc15"],
            ["interpolate", ["linear"], ["feature-state", "pct"], 0, "#7f1d1d", 49, "#f87171"],
          ],
          fallbackFillByKind,
        ],
        "fill-opacity": 0.28,
      },
    });

    map.addLayer({
      id: "line",
      type: "line",
      source: "polys",
      paint: {
        "line-color": [
          "case",
          ["==", ["feature-state", "hasPct"], true],
          [
            "case",
            [">=", ["feature-state", "pct"], 65], "#15803d",
            [">=", ["feature-state", "pct"], 50], "#a16207",
            "#991b1b",
          ],
          fallbackLineByKind,
        ],
        "line-width": [
          "case",
          ["==", ["get", "kind"], "lugar"], 2.5,
          3
        ],
      },
    });

    map.addLayer({
      id: "labels",
      type: "symbol",
      source: "polys",
      layout: {
        "text-field": ["get", "name"],
        "text-size": 14,
      },
    });

    map.on("click", "fill", (e) => {
      const f = e.features && e.features[0];
      if (!f) return;
      popupForFeature(f, e.lngLat);
    });

    await loadStats();

    renderList(fc.features);
    setPctStates(fc.features);

    const bb = bboxOfFeatureCollection(fc);
    safeFitBounds(bb, 60, MAX_ZOOM);

    if (vistaSel) vistaSel.addEventListener("change", applyFilters);
    if (sectorSel) sectorSel.addEventListener("change", applyFilters);
    if (ubicSel) ubicSel.addEventListener("change", applyFilters);

    if (btnLimpiar) {
      btnLimpiar.addEventListener("click", () => {
        if (vistaSel) vistaSel.value = "todo";
        if (sectorSel) sectorSel.value = "";
        if (ubicSel) ubicSel.value = "";
        applyFilters();
      });
    }

    applyFilters();
  });
})();