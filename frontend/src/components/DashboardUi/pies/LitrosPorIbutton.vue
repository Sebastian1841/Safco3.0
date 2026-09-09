<template>
  <div class="w-full p-4 bg-white rounded-lg shadow space-y-2">
    <p class="text-xs font-semibold text-gray-600">Litros por iButton</p>

    <div class="w-full h-60 sm:h-72 md:h-80 lg:h-96 relative">
      <canvas ref="canvas" class="w-full h-full"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated, watch, nextTick, defineProps } from "vue";
import axios from "axios";
import { Chart, BarController, BarElement, LinearScale, CategoryScale, Tooltip, Legend } from "chart.js";

Chart.register(BarController, BarElement, LinearScale, CategoryScale, Tooltip, Legend);

/* ======================================
   PROPS DESDE EL DASHBOARD
====================================== */
const props = defineProps({
  fechaInicio: String,
  fechaFin: String,
  selectedDevices: Array,
  selectedRange: String
});

/* ======================================
   CONSTANTES
====================================== */
const BACKEND_URL =
  process.env.VUE_APP_BACKEND_URL || "http://localhost:8081";
console.log("🔧 BACKEND_URL (IBBUTON):", BACKEND_URL);
const NO_IBTN = "_NO_IBUTTON_";

import { ibuttonAlias } from '@/config/ibuttonAliases';


const colorPalette = [
  "#ff660080","#2563EB80","#22C55E80","#A855F780","#E11D4880",
  "#14B8A680","#0EA5E980","#F59E0B80","#6366F180","#EF444480","#84CC1690"
];

/* ======================================
   STATE
====================================== */
const canvas = ref(null);
let chart = null;
const rawDatos = ref([]);

/* ======================================
   FETCH DIRECTO
====================================== */
async function fetchDatos() {
  try {
    const r = await axios.get(`${BACKEND_URL}/datos`);
    rawDatos.value = Array.isArray(r.data) ? [...r.data] : [];
  } catch (err) {
    console.error("Error cargando datos iButton:", err);
    rawDatos.value = [];
  }
}

/* ======================================
   FILTROS IGUALES A BarsChart
====================================== */
function aplicarFiltros() {
  let data = [...rawDatos.value];
  const now = new Date();

  // ⭐ FILTRO POR DISPOSITIVOS
  if (props.selectedDevices?.length) {
    data = data.filter(d => props.selectedDevices.includes(Number(d.dispositivo_id)));
  }

  // ⭐ FILTRO POR RANGOS RÁPIDOS
  if (props.selectedRange === "last_hour") {
    data = data.filter(d => new Date(d.fecha) >= new Date(now - 1 * 3600000));
  } else if (props.selectedRange === "last_12_hours") {
    data = data.filter(d => new Date(d.fecha) >= new Date(now - 12 * 3600000));
  } else if (props.selectedRange === "last_week") {
    data = data.filter(d => new Date(d.fecha) >= new Date(now - 7 * 24 * 3600000));
  } else if (props.selectedRange === "last_month") {
    data = data.filter(d => new Date(d.fecha) >= new Date(now - 30 * 24 * 3600000));
  } else if (props.selectedRange === "last_6_months") {
    data = data.filter(d => new Date(d.fecha) >= new Date(now - 180 * 24 * 3600000));
  }

  // ⭐ FILTRO POR FECHA INICIO-FIN
  else if (props.fechaInicio && props.fechaFin) {
    const ini = new Date(`${props.fechaInicio}T00:00:00`);
    const fin = new Date(`${props.fechaFin}T23:59:59`);
    data = data.filter(d => new Date(d.fecha) >= ini && new Date(d.fecha) <= fin);
  }

  // ⭐ FILTRO POR DEFECTO (24 horas)
  else {
    data = data.filter(d => new Date(d.fecha) >= new Date(now - 24 * 3600000));
  }

  return data;
}

/* ======================================
   RENDERIZAR GRÁFICO (CON ANIMACIÓN)
====================================== */
function render() {
  if (!canvas.value) return;

  if (chart) {
    try { chart.destroy(); } catch {
      //a
    }
    chart = null;
  }

  const datosFiltrados = aplicarFiltros();

  /* Agrupar litros por iButton */
  const totals = {};
  for (const d of datosFiltrados) {
    const key = d?.ibutton && d.ibutton.trim() ? d.ibutton.trim() : NO_IBTN;
    totals[key] = (totals[key] || 0) + Number(d.litros || 0);
  }

  const rawLabels = Object.keys(totals).sort((a, b) => {
    if (a === NO_IBTN) return 1;
    if (b === NO_IBTN) return -1;
    return (ibuttonAlias[a] ?? a).localeCompare(ibuttonAlias[b] ?? b, "es", { numeric: true });
  });

  const labels = rawLabels.map(k => ibuttonAlias[k] ?? k);
  const values = rawLabels.map(k => totals[k]);

  const ctx = canvas.value.getContext("2d");

  /* ===============================
     1️⃣ CREAR CHART CON DATA EN 0
     =============================== */
  chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Litros",
        data: labels.map(() => 0),  // ⬅ todas las barras arrancan en 0
        backgroundColor: rawLabels.map((_, i) => colorPalette[i % colorPalette.length])
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: "y",
      animation: false, // ⬅ sin animación inicial
      plugins: { legend: { display: false } },
      scales: {
        x: { beginAtZero: true },
        y: { ticks: { autoSkip: false } }
      }
    }
  });

  /* ===============================
     2️⃣ SEGUNDO UPDATE → ANIMACIÓN
     =============================== */
  setTimeout(() => {
    chart.data.datasets[0].data = values;

    chart.options.animation = {
      duration: 900,
      easing: "easeOutQuart",
      delay: (ctx) => ctx.dataIndex * 120  // ⭐ cada barra aparece con retraso
    };

    chart.update();
  }, 40);
}

/* ======================================
   MOUNT + ACTIVATED
====================================== */
async function updateChart() {
  await fetchDatos();
  await nextTick();
  render();
}

onMounted(updateChart);
onActivated(updateChart);

watch(
  () => [props.fechaInicio, props.fechaFin, props.selectedDevices, props.selectedRange],
  async () => {
    await nextTick();
    render();
  },
  { deep: true }
);
</script>
