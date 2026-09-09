<template>
  <div class="w-full p-4 bg-white rounded-lg shadow space-y-2">
    <p class="text-xs font-semibold text-gray-600">Litros por ACC Negocio</p>

    <div class="w-full h-60 sm:h-72 md:h-80 lg:h-96 relative">

      <!-- ⚠️ MENSAJE SIN DATOS -->
      <div
        v-if="noData"
        class="absolute inset-0 flex items-center justify-center 
               text-gray-400 text-sm font-medium bg-white/80 rounded-lg z-10"
      >
        <div class="flex flex-col items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg"
               class="w-10 h-10 text-gray-300"
               fill="none" viewBox="0 0 24 24" stroke="currentColor"
               stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M12 9v3m0 3h.01M4.93 19.07a10 10 0 1 1 14.14 0A10 10 0 0 1 4.93 19.07z"/>
          </svg>
          No hay datos para mostrar
        </div>
      </div>

      <canvas ref="canvas" class="w-full h-full"></canvas>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated, computed, nextTick, watch, defineProps } from "vue";
import axios from "axios";
import { Chart, PieController, ArcElement, Tooltip, Legend } from "chart.js";

Chart.register(PieController, ArcElement, Tooltip, Legend);

/* ======================================
   RECIBIR FILTROS DEL DASHBOARD
====================================== */
const props = defineProps({
  fechaInicio: String,
  fechaFin: String,
  selectedDevices: Array,
  selectedRange: String
});

/* ======================================
   ESTADO
====================================== */
const BACKEND_URL =
  process.env.VUE_APP_BACKEND_URL || "http://localhost:8081";
console.log("🔧 BACKEND_URL (DATO 2):", BACKEND_URL);
const canvas = ref(null);
let chart = null;
const rawDatos = ref([]);

/* ======================================
   FETCH /datos
====================================== */
async function fetchDatos() {
  try {
    const r = await axios.get(`${BACKEND_URL}/datos`);
    rawDatos.value = Array.isArray(r.data) ? [...r.data] : [];
  } catch (err) {
    console.error("Error cargando datos ACC Negocio:", err);
    rawDatos.value = [];
  }
}

/* ======================================
   APLICAR FILTROS — IGUAL A BarsChart
====================================== */
function aplicarFiltros() {
  let data = [...rawDatos.value];
  const now = new Date();

  // Filtro por dispositivos
  if (props.selectedDevices?.length) {
    data = data.filter(d => props.selectedDevices.includes(Number(d.dispositivo_id)));
  }

  // Filtros rápidos
  if (props.selectedRange === "last_hour") {
    data = data.filter(d => new Date(d.fecha) >= new Date(now - 1 * 3600000));

  } else if (props.selectedRange === "last_12_hours") {
    data = data.filter(d => new Date(d.fecha) >= new Date(now - 12 * 3600000));

  } else if (props.selectedRange === "last_week") {
    data = data.filter(d => new Date(d.fecha) >= new Date(now - 7 * 86400000));

  } else if (props.selectedRange === "last_month") {
    data = data.filter(d => new Date(d.fecha) >= new Date(now - 30 * 86400000));

  } else if (props.selectedRange === "last_6_months") {
    data = data.filter(d => new Date(d.fecha) >= new Date(now - 180 * 86400000));
  }

  // Filtro manual por fechas
  else if (props.fechaInicio && props.fechaFin) {
    const ini = new Date(`${props.fechaInicio}T00:00:00`);
    const fin = new Date(`${props.fechaFin}T23:59:59`);
    data = data.filter(d => {
      const fecha = new Date(d.fecha);
      return fecha >= ini && fecha <= fin;
    });
  }

  // Default → últimas 24h
  else {
    data = data.filter(d => new Date(d.fecha) >= new Date(now - 24 * 3600000));
  }

  return data;
}

/* ======================================
   DETECTAR SIN DATOS
====================================== */
const noData = computed(() => {
  const d = aplicarFiltros();
  return !d.some(x => x.dato2_nombre && Number(x.litros) > 0);
});

/* ======================================
   RENDERIZAR PIE CHART CON ANIMACIÓN REAL
====================================== */
async function render() {
  if (!canvas.value) return;

  if (chart) chart.destroy();

  const datos = aplicarFiltros();
  if (!datos.length) return;

  const totals = {};
  datos.forEach(d => {
    if (!d.dato2_nombre) return;
    totals[d.dato2_nombre] = (totals[d.dato2_nombre] || 0) + Number(d.litros || 0);
  });

  const labels = Object.keys(totals);
  const values = Object.values(totals);
  if (!labels.length) return;

  const ctx = canvas.value.getContext("2d");

  const colors = [
    "#FFB74D", "#4ADE80", "#BA68C8", "#29B6F6",
    "#EF5350", "#FFD54F", "#81C784", "#9575CD"
  ];

  // 1️⃣ PRIMER CHART: valores en 0 para permitir animación
  chart = new Chart(ctx, {
    type: "pie",
    data: {
      labels,
      datasets: [{
        data: labels.map(() => 0), // TODAS LAS REBANADAS EN 0
        backgroundColor: colors
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: {
        legend: { position: "bottom" }
      }
    }
  });

  // 2️⃣ SEGUNDO UPDATE: animación stagger real
  setTimeout(() => {
    chart.data.datasets[0].data = values;

    chart.options.animation = {
      duration: 900,
      easing: "easeOutQuart",
      delay: (ctx) => ctx.dataIndex * 120 // ⭐ APARICIÓN EN SECUENCIA
    };

    chart.update();
  }, 30);
}

/* ======================================
   CICLOS DE VIDA
====================================== */
async function updateChart() {
  await fetchDatos();
  await nextTick();
  render();
}

onMounted(updateChart);
onActivated(updateChart);

// Redibujar si cambian filtros
watch(
  () => [props.fechaInicio, props.fechaFin, props.selectedDevices, props.selectedRange],
  () => nextTick(render),
  { deep: true }
);
</script>
