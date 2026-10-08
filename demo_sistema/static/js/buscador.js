/*
 * Buscador rápido tipo "campo de consulta" (Shift+F12), inspirado en el
 * sistema anterior: campos de solo lectura que abren una ventana modal de
 * búsqueda por nombre (y teléfono en clientes/proveedores), con resultados
 * en vivo. Se elige un registro con clic en la fila o el botón "Escoger".
 *
 * Requiere el modal genérico #modal-buscador definido en base.html.
 */
(function () {
  const modal = document.getElementById("modal-buscador");
  if (!modal) return;

  const input = document.getElementById("modal-buscador-input");
  const titulo = document.getElementById("modal-buscador-titulo");
  const encabezado = document.getElementById("modal-buscador-encabezado");
  const cuerpo = document.getElementById("modal-buscador-cuerpo");
  const btnCerrar = document.getElementById("modal-buscador-cerrar");

  let configActual = null;
  let temporizador = null;

  function cerrar() {
    modal.classList.remove("activo");
    configActual = null;
    input.value = "";
    cuerpo.innerHTML = "";
  }

  function celda(valor) {
    return valor === undefined || valor === null || valor === "" ? "—" : valor;
  }

  function pintarResultados(resultados) {
    cuerpo.innerHTML = "";
    if (!resultados.length) {
      const fila = document.createElement("tr");
      fila.innerHTML = `<td colspan="${configActual.columnas.length + 1}">Sin resultados.</td>`;
      cuerpo.appendChild(fila);
      return;
    }
    resultados.forEach(function (resultado) {
      const fila = document.createElement("tr");
      fila.className = "fila-buscador";
      const celdas = configActual.columnas
        .map(function (col) { return `<td>${celda(resultado[col.campo])}</td>`; })
        .join("");
      fila.innerHTML = `${celdas}<td><button type="button" class="btn btn-sm btn-primario btn-escoger">Escoger</button></td>`;
      fila.addEventListener("click", function () { escoger(resultado); });
      cuerpo.appendChild(fila);
    });
  }

  function ejecutarBusqueda(q) {
    if (!configActual || q.length < 2) {
      cuerpo.innerHTML = "";
      return;
    }
    const params = new URLSearchParams({ q: q });
    if (configActual.parametrosExtra) {
      const extra = configActual.parametrosExtra() || {};
      Object.keys(extra).forEach(function (clave) {
        if (extra[clave] !== undefined && extra[clave] !== null && extra[clave] !== "") {
          params.set(clave, extra[clave]);
        }
      });
    }
    fetch(`${configActual.url}?${params.toString()}`)
      .then(function (r) { return r.json(); })
      .then(function (data) { pintarResultados(data.resultados || []); })
      .catch(function () { cuerpo.innerHTML = "<tr><td>Ocurrió un error al buscar.</td></tr>"; });
  }

  function escoger(resultado) {
    if (configActual && configActual.alEscoger) configActual.alEscoger(resultado);
    cerrar();
  }

  input.addEventListener("input", function () {
    clearTimeout(temporizador);
    const valor = input.value.trim();
    temporizador = setTimeout(function () { ejecutarBusqueda(valor); }, 300);
  });

  btnCerrar.addEventListener("click", cerrar);
  modal.addEventListener("click", function (e) { if (e.target === modal) cerrar(); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && modal.classList.contains("activo")) cerrar();
  });

  window.abrirBuscador = function (config) {
    configActual = config;
    titulo.textContent = config.titulo || "Buscar";
    encabezado.innerHTML = `<tr>${config.columnas.map(function (c) { return `<th>${c.titulo}</th>`; }).join("")}<th></th></tr>`;
    cuerpo.innerHTML = "";
    input.value = "";
    input.placeholder = config.placeholder || "Escribe para buscar...";
    modal.classList.add("activo");
    setTimeout(function () { input.focus(); }, 30);
  };
})();

/*
 * Convierte un campo de texto (readonly) en un "campo de consulta": clic o
 * Shift+F12 abre el buscador; al escoger un resultado llena el campo visible
 * y un campo oculto con el id real, y mueve el foco al siguiente campo.
 *
 * opciones: {
 *   campoTexto: id del input visible (readonly),
 *   campoId: id del input oculto donde se guarda el id real,
 *   url: endpoint de búsqueda,
 *   columnas: [{campo, titulo}, ...],
 *   titulo: título de la ventana,
 *   placeholder: placeholder del cuadro de búsqueda,
 *   parametrosExtra: () => ({...}) parámetros adicionales para la búsqueda,
 *   textoResultado: (resultado) => texto a mostrar en el campo visible,
 *   alEscoger: (resultado) => acciones adicionales (llenar precios, etc.),
 *   enfocarDespues: id del elemento a enfocar después de escoger,
 * }
 */
function crearCampoBusqueda(opciones) {
  const texto = document.getElementById(opciones.campoTexto);
  const idEl = opciones.campoId ? document.getElementById(opciones.campoId) : null;
  if (!texto) return;

  function abrir() {
    window.abrirBuscador({
      titulo: opciones.titulo,
      url: opciones.url,
      columnas: opciones.columnas,
      placeholder: opciones.placeholder,
      parametrosExtra: opciones.parametrosExtra,
      alEscoger: function (resultado) {
        texto.value = opciones.textoResultado ? opciones.textoResultado(resultado) : resultado.nombre;
        if (idEl) idEl.value = resultado.id;
        if (opciones.alEscoger) opciones.alEscoger(resultado);
        const siguiente = opciones.enfocarDespues && document.getElementById(opciones.enfocarDespues);
        (siguiente || texto).focus();
      },
    });
  }

  texto.addEventListener("click", abrir);
  texto.addEventListener("keydown", function (e) {
    if (e.shiftKey && e.key === "F12") {
      e.preventDefault();
      abrir();
    }
  });
}
