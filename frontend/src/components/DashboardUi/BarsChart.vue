<template>
  <div class="w-full bg-white rounded-lg shadow p-2 sm:p-4">

    <!-- ✅ CONTENEDOR RESPONSIVO CON ALTURA REAL -->
    <div class="relative w-full min-h-[55vh] sm:min-h-[380px]">
      <canvas ref="chartCanvas" class="w-full h-full"></canvas>
    </div>

    <div class="flex gap-2 mt-2">
      <button v-if="chartInstance" @click="chartInstance.resetZoom()"
        class="px-3 py-1 bg-blue-600 text-white rounded text-xs shadow hover:bg-blue-700">
        Reiniciar Zoom
      </button>

      <button @click="toggleZoom" class="px-3 py-1 rounded text-xs shadow" :class="zoomEnabled
        ? 'bg-red-600 text-white hover:bg-red-700'
        : 'bg-gray-300 text-gray-900 hover:bg-gray-400'">
        {{ zoomEnabled ? 'Desactivar Zoom' : 'Activar Zoom' }}
      </button>
    </div>

  </div>
</template>



<script setup>
import { ref, onMounted, watch, nextTick, defineProps } from 'vue';
import axios from 'axios';
import zoomPlugin from 'chartjs-plugin-zoom';

import {
  Chart,
  BarController,
  BarElement,
  TimeScale,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend
} from 'chart.js';

import 'chartjs-adapter-date-fns';
import es from 'date-fns/locale/es';

Chart.register(
  BarController,
  BarElement,
  TimeScale,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
  zoomPlugin
);
import { ibuttonAlias } from '@/config/ibuttonAliases';


const props = defineProps({
  fechaInicio: String,
  fechaFin: String,
  selectedDevices: Array,
  selectedRange: String
});

const BACKEND_URL =
  process.env.VUE_APP_BACKEND_URL || "http://localhost:8081";
console.log("🔧 BACKEND_URL (BarsChart):", BACKEND_URL);


const chartCanvas = ref(null);
let chartInstance = null;
const rawDatos = ref([]);
const zoomEnabled = ref(false);

const generateMockData = () => {
  const data = [];
  const devices = ['A101', 'B202', 'C303'];
  const now = new Date();
  for (let i = 0; i < 50; i++) {
    const date = new Date(now.getTime() - (i * 3600000 * 2));
    data.push({
      fecha: date.toISOString(),
      dispositivo_id: devices[i % devices.length],
      litros: (Math.random() * 5 + 1).toFixed(2),
      ibutton: i % 10 === 0 ? `iBtn-${i}` : null,
      dato1_nombre: i % 5 === 0 ? 'Sensor Temp' : null,
      dato2_nombre: i % 7 === 0 ? 'Sensor Pres' : null,
    });
  }
  return data;
};

async function fetchDatos() {
  try {
    const r = await axios.get(`${BACKEND_URL}/datos`);
    rawDatos.value = Array.isArray(r.data) ? r.data : [];
  } catch (error) {
    console.error("Error fetching data, using mock data:", error.message);
    rawDatos.value = generateMockData();
  }
}

/* ======================================
   AGRUPAR POR DÍA
   ====================================== */
function agruparPorDia(data) {
  const mapa = {};

  data.forEach(d => {
    const fecha = new Date(d.fecha).toISOString().split("T")[0];
    const key = `${fecha}-${d.dispositivo_id}`; // 👈 clave única por día + dispositivo

    if (!mapa[key]) {
      mapa[key] = {
        fecha,
        dispositivo_id: d.dispositivo_id,
        litros: 0,
        ibutton: null,
        dato1_nombre: null,
        dato2_nombre: null
      };
    }

    mapa[key].litros += Number(d.litros);
  });

  return Object.values(mapa);
}


function initChart() {
  if (!chartCanvas.value) return;

  if (chartInstance) {
    try { chartInstance.destroy(); } catch (e) {
      // instancia ya estaba destruida
    }
    chartInstance = null;
  }

  let data = [...rawDatos.value];
  const now = new Date();

  /* ======================================
     FILTRADO POR RANGO
     ====================================== */
  if (props.selectedDevices?.length) {
    data = data.filter(d => props.selectedDevices.includes(d.dispositivo_id));
  }

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
  } else if (props.fechaInicio && props.fechaFin) {
    const ini = new Date(`${props.fechaInicio}T00:00:00`);
    const fin = new Date(`${props.fechaFin}T23:59:59`);
    data = data.filter(d => new Date(d.fecha) >= ini && new Date(d.fecha) <= fin);
  } else {
    // 🔥 Vista por defecto → 24 horas
    data = data.filter(d => new Date(d.fecha) >= new Date(now - 24 * 3600000));
  }

  /* ======================================
     AGRUPAR POR DÍA (Semana/Mes/6 meses)
     ====================================== */
  const rangosQueAgrupan = ["last_week", "last_month", "last_6_months"];
  const debeAgrupar = rangosQueAgrupan.includes(props.selectedRange);
  if (debeAgrupar) data = agruparPorDia(data);

  /* ======================================
     ORDENAR
     ====================================== */
  data.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));

  if (!data.length) return;

  /* ======================================
     CALCULAR RANGO X + PADDING
     ====================================== */
  const first = new Date(data[0].fecha);
  const last = new Date(data[data.length - 1].fecha);

  const esVista24h = !props.selectedRange && !props.fechaInicio && !props.fechaFin;

  let xMin, xMax;

  if (esVista24h) {
    xMin = new Date(now - 24 * 3600000).getTime();
    xMax = now.getTime();
  } else {
    xMin = first.getTime();
    xMax = last.getTime();
  }

  // 🔥 Padding visual amplio para separar las barras de los bordes
  const paddingHoras = 6; // horas de espacio

  const padding = paddingHoras * 3600000; // 6h
  xMin -= padding;
  xMax += padding;

  /* ======================================
     TIME UNIT
     ====================================== */
  let timeUnit = "hour";
  if (debeAgrupar) timeUnit = "day";

  /* ======================================
     DATASETS
     ====================================== */
  const devicesToShow = props.selectedDevices.length
    ? props.selectedDevices
    : [...new Set(data.map(d => d.dispositivo_id))];

  const datasets = devicesToShow.map((dev, i) => ({
    label: `Dispositivo ${dev}`,
    backgroundColor: ['#2563EB', '#ff6600', '#065F46', '#B91C1C', '#312E81'][i % 5],
    borderWidth: 1.5,
    borderColor: "#1f2937",
    borderRadius: 3,
    maxBarThickness: 14,
    barPercentage: 0.4,
    categoryPercentage: 0.6,
    data: data.filter(d => d.dispositivo_id === dev).map(d => ({
      x: new Date(d.fecha),
      y: Number(d.litros),
      ibutton: d.ibutton,
      dato1: d.dato1_nombre,
      dato2: d.dato2_nombre
    }))
  }));

  /* ======================================
     CREAR CHART
     ====================================== */
  const ctx = chartCanvas.value.getContext("2d");

  chartInstance = new Chart(ctx, {
    type: "bar",
    data: { datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      parsing: false,

      plugins: {
        legend: { display: true, position: "bottom" },

        tooltip: {
          backgroundColor: "#111827e6",
          displayColors: false,
          callbacks: {
            title: ([p]) => new Date(p.raw.x).toLocaleString("es-CL", {
              timeZone: "America/Santiago",
              hour12: false,
              year: 'numeric',
              month: 'numeric',
              day: 'numeric',
              hour: debeAgrupar ? undefined : '2-digit',
              minute: debeAgrupar ? undefined : '2-digit',
              second: debeAgrupar ? undefined : '2-digit'
            }),
            label: ({ raw }) => {
              const litrosRedondeados = Math.round(Number(raw.y));
              const l = [`Litros: ${litrosRedondeados.toLocaleString("es-CL")} L`];
              if (raw.ibutton) l.push(`iButton: ${ibuttonAlias[raw.ibutton] ?? raw.ibutton}`);
              if (raw.dato1) l.push(`COD Equipo: ${raw.dato1}`);
              if (raw.dato2) l.push(`ACC NEGOCIO: ${raw.dato2}`);
              return l;
            }
          }
        },

        zoom: {
          zoom: {
            enabled: zoomEnabled.value,
            wheel: { enabled: zoomEnabled.value },
            mode: "x"
          },
          pan: { enabled: zoomEnabled.value, mode: "x" }
        }
      },

      scales: {
        x: {
          type: "time",
          adapters: { date: { locale: es } },
          min: xMin,
          max: xMax,
          time: {
            unit: timeUnit,
            displayFormats: { hour: "HH:mm", day: "dd/MM" }
          },
          ticks: { autoSkip: true, maxTicksLimit: 10 }
        },
        y: {
          beginAtZero: true,
          title: { text: "Litros", display: true }
        }
      }
    }
  });
}

function toggleZoom() {
  zoomEnabled.value = !zoomEnabled.value;
  if (chartInstance) {
    chartInstance.options.plugins.zoom.zoom.enabled = zoomEnabled.value;
    chartInstance.options.plugins.zoom.zoom.wheel.enabled = zoomEnabled.value;
    chartInstance.options.plugins.zoom.pan.enabled = zoomEnabled.value;
    chartInstance.update('none');
  }
}

onMounted(async () => {
  await fetchDatos();
  await nextTick();
  initChart();
});

watch(
  () => [props.fechaInicio, props.fechaFin, props.selectedDevices, props.selectedRange],
  async () => {
    await nextTick();
    if (chartCanvas.value) initChart();
  },
  { deep: true }
);
</script>


<style scoped>
@media (max-width: 480px) {
  .relative canvas {
    height: 65vh !important;
  }
}
</style>
