(function () {
  const url = window.PVSA_FILTROS_URL;
  if (!url) return;

  const root =
    document.querySelector("[data-filtros-dependientes='1']") ||
    document.querySelector("form[method='get']") ||
    document.querySelector("form[method='GET']");

  if (!root) return;

  function getSelect(name) {
    return root.querySelector(`select[name="${name}"]`);
  }

  const selects = {
    sector: getSelect("sector"),
    ubicacion: getSelect("ubicacion"),
    piso: getSelect("piso"),
    tipoLugar: getSelect("tipo_lugar"),
    lugar: getSelect("lugar"),
    categoria: getSelect("categoria"),
    objeto: getSelect("objeto"),
    tipo: getSelect("tipo"),
    tipoObjeto: getSelect("tipo_objeto"),
    marca: getSelect("marca"),
    material: getSelect("material"),
  };

  const existeAlguno = Object.values(selects).some(Boolean);
  if (!existeAlguno) return;

  function valueOf(select) {
    return select ? select.value || "" : "";
  }

  function clearSelect(select) {
    if (select) select.value = "";
  }

  function setOptions(select, items, placeholder) {
    if (!select) return;

    const current = select.value || "";
    select.innerHTML = "";

    const first = document.createElement("option");
    first.value = "";
    first.textContent = placeholder;
    select.appendChild(first);

    let currentStillExists = false;

    (items || []).forEach((item) => {
      const opt = document.createElement("option");
      opt.value = item.id;
      opt.textContent = item.nombre;

      if (String(item.id) === String(current)) {
        currentStillExists = true;
      }

      select.appendChild(opt);
    });

    select.value = currentStillExists ? current : "";
  }

  function buildParams() {
    const params = new URLSearchParams();

    const tipoValue = valueOf(selects.tipoObjeto) || valueOf(selects.tipo);

    const values = {
      sector: valueOf(selects.sector),
      ubicacion: valueOf(selects.ubicacion),
      piso: valueOf(selects.piso),
      tipo_lugar: valueOf(selects.tipoLugar),
      lugar: valueOf(selects.lugar),
      categoria: valueOf(selects.categoria),
      objeto: valueOf(selects.objeto),
      tipo_objeto: tipoValue,
      marca: valueOf(selects.marca),
      material: valueOf(selects.material),
    };

    Object.entries(values).forEach(([key, value]) => {
      if (value) params.append(key, value);
    });

    return params;
  }

  async function actualizarFiltros() {
    try {
      const params = buildParams();
      const response = await fetch(`${url}?${params.toString()}`, {
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      if (!response.ok) return;

      const data = await response.json();

      setOptions(selects.ubicacion, data.ubicaciones, "Todas las ubicaciones");
      setOptions(selects.piso, data.pisos, "Todos los pisos");
      setOptions(selects.tipoLugar, data.tipos_lugar, "Todos los tipos");
      setOptions(selects.lugar, data.lugares, "Todos los lugares");
      setOptions(selects.categoria, data.categorias, "Todas las categorías");
      setOptions(selects.objeto, data.objetos, "Todos los objetos");

      setOptions(selects.tipo, data.tipos_objeto, "Todos los tipos");
      setOptions(selects.tipoObjeto, data.tipos_objeto, "Todos los tipos");

      setOptions(selects.marca, data.marcas, "Todas las marcas");
      setOptions(selects.material, data.materiales, "Todos los materiales");
    } catch (error) {
      console.error("Error actualizando filtros dependientes:", error);
    }
  }

  function bind(select, clears) {
    if (!select) return;

    select.addEventListener("change", () => {
      clears.forEach(clearSelect);
      actualizarFiltros();
    });
  }

  bind(selects.sector, [
    selects.ubicacion,
    selects.piso,
    selects.tipoLugar,
    selects.lugar,
    selects.categoria,
    selects.objeto,
    selects.tipo,
    selects.tipoObjeto,
    selects.marca,
    selects.material,
  ]);

  bind(selects.ubicacion, [
    selects.piso,
    selects.tipoLugar,
    selects.lugar,
    selects.categoria,
    selects.objeto,
    selects.tipo,
    selects.tipoObjeto,
    selects.marca,
    selects.material,
  ]);

  bind(selects.piso, [
    selects.tipoLugar,
    selects.lugar,
    selects.categoria,
    selects.objeto,
    selects.tipo,
    selects.tipoObjeto,
    selects.marca,
    selects.material,
  ]);

  bind(selects.tipoLugar, [
    selects.lugar,
    selects.categoria,
    selects.objeto,
    selects.tipo,
    selects.tipoObjeto,
    selects.marca,
    selects.material,
  ]);

  bind(selects.lugar, [
    selects.categoria,
    selects.objeto,
    selects.tipo,
    selects.tipoObjeto,
    selects.marca,
    selects.material,
  ]);

  bind(selects.categoria, [
    selects.objeto,
    selects.tipo,
    selects.tipoObjeto,
    selects.marca,
    selects.material,
  ]);

  bind(selects.objeto, [
    selects.tipo,
    selects.tipoObjeto,
    selects.marca,
    selects.material,
  ]);

  bind(selects.tipo, [
    selects.marca,
    selects.material,
  ]);

  bind(selects.tipoObjeto, [
    selects.marca,
    selects.material,
  ]);
})();