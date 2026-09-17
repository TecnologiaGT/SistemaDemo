function configurarFormset(prefix) {
  const totalInput = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
  const contenedor = document.getElementById(`formset-${prefix}`);
  const btnAgregar = document.getElementById(`agregar-${prefix}`);
  if (!totalInput || !contenedor || !btnAgregar) return;

  function actualizarIndices() {
    const filas = contenedor.querySelectorAll(".fila-formset");
    filas.forEach((fila, idx) => {
      fila.querySelectorAll("[name], [id], label[for]").forEach((el) => {
        ["name", "id", "for"].forEach((attr) => {
          if (el.hasAttribute(attr)) {
            el.setAttribute(
              attr,
              el.getAttribute(attr).replace(new RegExp(`${prefix}-(\\d+)-`), `${prefix}-${idx}-`)
            );
          }
        });
      });
    });
    totalInput.value = filas.length;
  }

  btnAgregar.addEventListener("click", function () {
    const filas = contenedor.querySelectorAll(".fila-formset");
    const plantilla = filas[filas.length - 1];
    const nueva = plantilla.cloneNode(true);
    nueva.querySelectorAll('input[type=text], input[type=email], input[type=tel]').forEach((i) => (i.value = ""));
    nueva.querySelectorAll("input[type=checkbox]").forEach((i) => (i.checked = false));
    const idInput = nueva.querySelector('input[name$="-id"]');
    if (idInput) idInput.value = "";
    nueva.style.display = "";
    contenedor.appendChild(nueva);
    actualizarIndices();
  });

  contenedor.addEventListener("click", function (e) {
    if (e.target.matches(".btn-quitar-fila")) {
      const fila = e.target.closest(".fila-formset");
      const deleteInput = fila.querySelector('input[name$="-DELETE"]');
      const idInput = fila.querySelector('input[name$="-id"]');
      if (idInput && idInput.value) {
        if (deleteInput) deleteInput.checked = true;
        fila.style.display = "none";
      } else {
        fila.remove();
        actualizarIndices();
      }
    }
  });
}
