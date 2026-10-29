// ==========================================================================
// Lógica de la Aplicación: Diario de Estudio
// ==========================================================================

// Clave para guardar los datos en el navegador
const STORAGE_KEY = "diario_estudio_sesiones";

// Elementos del DOM
const form = document.getElementById("formularioSesion");
const inputFecha = document.getElementById("fecha");
const inputTema = document.getElementById("tema");
const inputMinutos = document.getElementById("minutos");
const rachaTexto = document.getElementById("rachaTexto");
const listaSesiones = document.getElementById("listaSesiones");
const mensajeVacio = document.getElementById("mensajeVacio");

// ==========================================================================
// 1. Funciones de Fechas (Trabajan siempre con la fecha local del usuario)
// ==========================================================================

/**
 * Convierte un objeto Date a formato "AAAA-MM-DD" según la hora local.
 */
function obtenerFechaLocalTexto(fecha) {
  const anio = fecha.getFullYear();
  const mes = String(fecha.getMonth() + 1).padStart(2, "0");
  const dia = String(fecha.getDate()).padStart(2, "0");
  return `${anio}-${mes}-${dia}`;
}

/**
 * Resta N días a una fecha base en horario local.
 */
function restarDias(fecha, dias) {
  const nuevaFecha = new Date(fecha.getFullYear(), fecha.getMonth(), fecha.getDate());
  nuevaFecha.setDate(nuevaFecha.getDate() - dias);
  return nuevaFecha;
}

/**
 * Da formato legible para mostrar en la lista (ej. 29/09/2026).
 */
function formatearFechaVisual(fechaTexto) {
  const partes = fechaTexto.split("-");
  if (partes.length === 3) {
    return `${partes[2]}/${partes[1]}/${partes[0]}`;
  }
  return fechaTexto;
}

// ==========================================================================
// 2. Manejo de Almacenamiento (localStorage)
// ==========================================================================

function cargarSesiones() {
  const datos = localStorage.getItem(STORAGE_KEY);
  return datos ? JSON.parse(datos) : [];
}

function guardarSesiones(sesiones) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(sesiones));
}

// ==========================================================================
// 3. Cálculo de la Racha
// ==========================================================================

/**
 * Calcula los días consecutivos con sesión.
 * - Si hoy hay sesión: cuenta desde hoy hacia atrás.
 * - Si hoy aún no hay sesión pero ayer sí: la racha sigue viva (cuenta desde ayer).
 * - Si ni hoy ni ayer hubo sesión: la racha es 0.
 */
function calcularRacha(sesiones) {
  if (sesiones.length === 0) {
    return 0;
  }

  // Conjunto de fechas únicas donde se estudió
  const diasEstudiados = new Set(sesiones.map(s => s.fecha));

  const hoy = new Date();
  const textoHoy = obtenerFechaLocalTexto(hoy);
  const textoAyer = obtenerFechaLocalTexto(restarDias(hoy, 1));

  let fechaPivote = null;

  if (diasEstudiados.has(textoHoy)) {
    fechaPivote = hoy;
  } else if (diasEstudiados.has(textoAyer)) {
    fechaPivote = restarDias(hoy, 1);
  } else {
    return 0; // Se rompió la racha
  }

  // Contar días consecutivos hacia atrás
  let racha = 0;
  let cursorFecha = new Date(fechaPivote.getFullYear(), fechaPivote.getMonth(), fechaPivote.getDate());

  while (diasEstudiados.has(obtenerFechaLocalTexto(cursorFecha))) {
    racha++;
    cursorFecha.setDate(cursorFecha.getDate() - 1);
  }

  return racha;
}

// ==========================================================================
// 4. Renderizado en la Interfaz (UI)
// ==========================================================================

function actualizarInterfaz() {
  const sesiones = cargarSesiones();

  // 1. Actualizar Racha
  const racha = calcularRacha(sesiones);
  rachaTexto.textContent = `${racha} ${racha === 1 ? "día" : "días"}`;

  // 2. Ordenar sesiones: de la más reciente a la más antigua
  const sesionesOrdenadas = [...sesiones].sort((a, b) => {
    if (a.fecha !== b.fecha) {
      return b.fecha.localeCompare(a.fecha);
    }
    return b.id - a.id; // Si son de la misma fecha, mostrar primero la última agregada
  });

  // 3. Renderizar lista
  listaSesiones.innerHTML = "";

  if (sesionesOrdenadas.length === 0) {
    mensajeVacio.style.display = "block";
  } else {
    mensajeVacio.style.display = "none";

    sesionesOrdenadas.forEach(sesion => {
      const li = document.createElement("li");
      li.className = "sesion-item";

      const infoDiv = document.createElement("div");
      infoDiv.className = "sesion-info";

      const temaSpan = document.createElement("span");
      temaSpan.className = "sesion-tema";
      temaSpan.textContent = sesion.tema;

      const fechaSpan = document.createElement("span");
      fechaSpan.className = "sesion-fecha";
      fechaSpan.textContent = formatearFechaVisual(sesion.fecha);

      infoDiv.appendChild(temaSpan);
      infoDiv.appendChild(fechaSpan);

      const minutosSpan = document.createElement("span");
      minutosSpan.className = "sesion-minutos";
      minutosSpan.textContent = `${sesion.minutos} min`;

      li.appendChild(infoDiv);
      li.appendChild(minutosSpan);
      listaSesiones.appendChild(li);
    });
  }
}

// ==========================================================================
// 5. Eventos e Inicialización
// ==========================================================================

// Poner por defecto la fecha de hoy local en el formulario
function inicializarFechaHoy() {
  inputFecha.value = obtenerFechaLocalTexto(new Date());
}

// Escuchar el envío del formulario
form.addEventListener("submit", function (evento) {
  evento.preventDefault();

  const fecha = inputFecha.value;
  const tema = inputTema.value.trim();
  const minutos = parseInt(inputMinutos.value, 10);

  if (!fecha || !tema || isNaN(minutos) || minutos <= 0) {
    return;
  }

  const nuevaSesion = {
    id: Date.now(),
    fecha: fecha,
    tema: tema,
    minutos: minutos
  };

  const sesiones = cargarSesiones();
  sesiones.push(nuevaSesion);
  guardarSesiones(sesiones);

  // Limpiar campos de texto pero mantener la fecha de hoy
  inputTema.value = "";
  inputMinutos.value = "";
  inputTema.focus();

  actualizarInterfaz();
});

// Al cargar la página
window.addEventListener("DOMContentLoaded", () => {
  inicializarFechaHoy();
  actualizarInterfaz();
});
