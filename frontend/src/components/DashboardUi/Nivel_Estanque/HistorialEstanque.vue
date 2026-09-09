<template>
  <div class="space-y-3">

    <!-- ============================== -->
    <!--        CONTROLES FIJOS         -->
    <!-- ============================== -->
    <div class="sticky top-0 bg-gray-50 py-2 z-20 border-b pb-2">

      <div class="flex gap-2 mb-2">

        <!-- Botones de filtro -->
        <button @click="filtro = 'todos'" :class="btnClass(filtro === 'todos')">
          Todos
        </button>

        <button @click="filtro = 'carga'" :class="btnClass(filtro === 'carga')">
          Cargas
        </button>

        <button @click="filtro = 'descarga'" :class="btnClass(filtro === 'descarga')">
          Descargas
        </button>

        <!-- Dropdown Fechas -->
        <div class="relative ml-auto" v-click-outside="() => showDropdownFechas = false">

          <button @click="showDropdownFechas = !showDropdownFechas"
            class="flex items-center gap-1 px-3 py-1 bg-white border rounded-md text-xs shadow-sm hover:bg-gray-100">
            <span>Fechas</span>
            <SvgIcon name="chevron-down" class="w-3 h-3 sm:w-4 sm:h-4" />
          </button>

          <div v-if="showDropdownFechas"
            class="absolute right-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-xl p-3 w-48 z-40">

            <label class="text-xs text-gray-600 font-semibold">Desde:</label>
            <input type="date" v-model="fechaInicio" class="w-full border rounded px-2 py-1 text-xs mb-2" />

            <label class="text-xs text-gray-600 font-semibold">Hasta:</label>
            <input type="date" v-model="fechaFin" class="w-full border rounded px-2 py-1 text-xs" />

            <p v-if="rangoInvalido" class="text-red-600 text-[11px] mt-2">
              Máx: {{ MAX_DIAS }} días.
            </p>

            <button @click="limpiarFechas" class="w-full mt-2 text-[11px] text-red-600 hover:text-red-800">
              Limpiar
            </button>

          </div>

        </div>
      </div>

    </div>

    <!-- ============================== -->
    <!--      LISTA SCROLLEABLE         -->
    <!-- ============================== -->
    <div class="max-h-64 overflow-y-auto pr-1">

      <div v-for="(item, index) in eventosFiltrados" :key="index"
        class="flex items-center gap-4 p-3 bg-white border border-slate-200 rounded-xl shadow-sm hover:shadow-md transition">

        <!-- ============================== -->
        <!--   ÍCONO SEGÚN ORIGEN          -->
        <!-- ============================== -->
        <div class="w-10 h-10 rounded-lg flex items-center justify-center"
          :class="{
            'bg-red-100 text-red-600': item.origen === 'sensor',
            'bg-green-100 text-green-600': item.origen === 'manual',
            'bg-blue-100 text-blue-600': item.origen === 'factura'
          }">

          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">

            <!-- DESCARGA (sensor) -->
            <path v-if="item.origen === 'sensor'"
              stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 3v14m0 0l-4-4m4 4l4-4M4 21h16" />

            <!-- CARGA MANUAL -->
            <path v-else-if="item.origen === 'manual'"
              stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 21V7m0 0l-4 4m4-4l4 4M4 3h16" />

            <!-- CARGA FACTURA -->
            <path v-else
              stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 4h16v16H4z" />

          </svg>

        </div>

        <!-- ============================== -->
        <!--         CONTENIDO TEXTO         -->
        <!-- ============================== -->

        <div class="flex-1 space-y-1">

          <div class="text-xs font-semibold text-slate-600">
            {{ item.estanque }}
          </div>

          <div class="flex justify-between text-xs">
            <span class="text-slate-500">Movimiento</span>

            <!-- BADGE SEGÚN ORIGEN -->
            <span
              class="px-2 py-0.5 rounded-md font-semibold text-[10px]"
              :class="{
                'bg-red-100 text-red-700': item.origen === 'sensor',
                'bg-green-100 text-green-700': item.origen === 'manual',
                'bg-blue-100 text-blue-700': item.origen === 'factura'
              }">
              {{ item.descripcion }}
              ({{ item.tipo === 'descarga' ? '-' : '+' }}
              {{ item.cantidad.toLocaleString('es-CL') }} L)
            </span>
          </div>

          <div class="flex justify-between text-xs" v-if="item.total_posterior !== null">
            <span class="font-semibold">Total después del movimiento</span>
            <span class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-md">
              {{ item.total_posterior.toLocaleString('es-CL') }} L
            </span>
          </div>

          <div class="flex justify-between text-[10px] text-slate-500">
            {{ item.hora_texto }} — {{ item.fecha_texto }}
          </div>

        </div>
      </div>

      <!-- Sin datos -->
      <div v-if="eventosFiltrados.length === 0"
        class="text-center py-4 bg-gray-100 border border-gray-300 rounded-lg text-sm text-gray-600 mt-3">
        No hay movimientos registrados en este rango de fechas.
      </div>

      <p v-if="props.eventos.length >= LIMITE_HISTORIAL" class="text-center text-xs text-blue-600 mt-2">
        Mostrando solo los últimos {{ LIMITE_HISTORIAL }} eventos.
      </p>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import SvgIcon from '@/components/icons/SvgIcon.vue'

const props = defineProps({
  eventos: { type: Array, default: () => [] }
})

const LIMITE_HISTORIAL = 100
const MAX_DIAS = 5

const filtro = ref("todos")
const fechaInicio = ref("")
const fechaFin = ref("")
const showDropdownFechas = ref(false)

function btnClass(active) {
  return [
    "px-3 py-1 text-xs rounded-md shadow-sm border",
    active ? "bg-sky-600 text-white" : "bg-white text-slate-600"
  ]
}

function limpiarFechas() {
  fechaInicio.value = ""
  fechaFin.value = ""
}

const rangoInvalido = computed(() => {
  if (!fechaInicio.value || !fechaFin.value) return false
  const ini = new Date(fechaInicio.value)
  const fin = new Date(fechaFin.value)
  return (fin - ini) / (1000 * 3600 * 24) > MAX_DIAS
})

const eventosFiltrados = computed(() => {
  if (rangoInvalido.value) return []

  let lista = props.eventos

  if (filtro.value === "carga") {
    lista = lista.filter(e => e.tipo === "carga")
  } else if (filtro.value === "descarga") {
    lista = lista.filter(e => e.tipo === "descarga")
  }

  if (fechaInicio.value && fechaFin.value) {
    const ini = new Date(fechaInicio.value)
    const fin = new Date(fechaFin.value + "T23:59:59")
    lista = lista.filter(e => {
      const f = new Date(e._orden)
      return f >= ini && f <= fin
    })
  }

  return lista
})
</script>
