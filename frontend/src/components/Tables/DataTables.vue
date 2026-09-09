<template>
  <div class="p-3 sm:p-4 bg-gray-50 min-h-screen font-sans">
    <!-- Fondo para cerrar dropdowns -->
    <div v-if="showDropdownDevices || showDropdownDates" @click="closeAllDropdowns" class="fixed inset-0 z-10"></div>

    <!-- Barra superior: búsqueda y filtros -->
    <div class="flex flex-col lg:flex-row justify-between items-center mb-4 gap-3">

      <!-- Input de búsqueda -->
      <div class="flex w-full lg:w-1/2">
        <div class="flex w-full border border-gray-300 rounded-lg overflow-hidden shadow-inner bg-white">
          <div class="flex items-center justify-center px-3 bg-gray-100 text-gray-500">
            <SvgIcon name="search" class="w-4 h-4 sm:w-5 sm:h-5" />
          </div>
          <input v-model="searchTerm" placeholder="Buscar por Fecha, Litros o iButton..."
            class="flex-1 p-2 text-sm bg-white text-gray-800 placeholder-gray-400 focus:outline-none" />
          <button v-if="searchTerm" @click="searchTerm = ''"
            class="px-3 bg-red-500 hover:bg-red-600 text-white font-medium text-xs sm:text-sm transition duration-150">
            Limpiar
          </button>
        </div>
      </div>

      <!-- Filtros: dispositivos y fechas -->
      <div class="flex flex-wrap justify-end items-center gap-3 w-full lg:w-auto">

        <button type="button" @click="openReport"
          class="flex items-center gap-2 px-3 py-1.5 bg-[#142777] text-white font-medium rounded-md hover:bg-blue-800 shadow-sm text-xs sm:text-sm">
          <svg viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true">
            <path d="M6 3h8l4 4v14H6zM14 3v5h4M9 12h6M9 16h6" />
          </svg>
          Generar informe
        </button>

        <!-- Dropdown Dispositivos -->
        <div class="relative z-20" v-click-outside="closeDropdownDevices">
          <button @click="toggleDropdown('devices')"
            class="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition duration-150 shadow-sm text-xs sm:text-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 sm:w-4 sm:h-4" fill="none" viewBox="0 0 24 24"
              stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
            <span>Dispositivos ({{ selectedDevices.length }})</span>
          </button>

          <div v-if="showDropdownDevices"
            class="absolute z-30 mt-1 right-0 bg-white border border-gray-300 rounded-lg shadow-xl w-48 max-h-52 overflow-y-auto">
            <div
              class="flex items-center px-3 py-1.5 bg-gray-100 hover:bg-gray-200 cursor-pointer border-b border-gray-200"
              @click="toggleSelectAllDevices()">
              <input type="checkbox" :checked="allDevicesSelected"
                class="mr-2 h-3 w-3 text-blue-600 focus:ring-blue-500 border-gray-300 rounded pointer-events-none" />
              <span class="text-xs sm:text-sm font-bold text-gray-800 pointer-events-none">
                {{ allDevicesSelected ? 'Deseleccionar Todos' : 'Seleccionar Todos' }}
              </span>
            </div>
            <div v-for="device in dispositivos" :key="device.id"
              class="flex items-center px-3 py-1.5 hover:bg-blue-50 cursor-pointer"
              @click="toggleDeviceSelection(device.id)">
              <input type="checkbox" :checked="selectedDevices.includes(device.id)" :value="device.id"
                class="mr-2 h-3 w-3 text-blue-600 focus:ring-blue-500 border-gray-300 rounded pointer-events-none" />
              <span class="text-xs sm:text-sm font-medium text-gray-700 pointer-events-none">{{ device.nombre }}</span>
            </div>
          </div>
        </div>

        <!-- Dropdown Fechas -->
        <div class="relative z-10" v-click-outside="closeDropdownDates">
          <button @click="toggleDropdown('dates')"
            class="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition duration-150 shadow-sm text-xs sm:text-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 sm:w-4 sm:h-4" fill="none" viewBox="0 0 24 24"
              stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span>Rango de Fechas</span>
          </button>

          <div v-if="showDropdownDates"
            class="absolute z-20 mt-1 right-0 bg-white border border-gray-300 rounded-lg shadow-xl p-3 w-64">
            <!-- Selección rápida -->
            <div class="mb-3 border-b pb-3 border-gray-100">
              <label for="quickRange" class="text-xs font-semibold text-gray-700 block mb-1">Selección Rápida:</label>
              <select id="quickRange" v-model="selectedRange" @change="applyDateRange(selectedRange)"
                class="w-full border border-gray-300 rounded-md px-2 py-1.5 text-xs bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition">
                <option :value="null" disabled>-- Rango Predefinido --</option>
                <option v-for="option in dateOptions" :key="option.key" :value="option.key">{{ option.label }}</option>
              </select>
            </div>

            <!-- Rango personalizado -->
            <div class="flex flex-col gap-2 text-gray-700">
              <label class="text-xs font-semibold">Fecha Inicio:</label>
              <input type="date" v-model="fechaInicio" @input="clearSelectedRange"
                class="border border-gray-300 rounded-md px-2 py-1 text-xs focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />

              <label class="text-xs font-semibold">Fecha Fin:</label>
              <input type="date" v-model="fechaFin" @input="clearSelectedRange"
                class="border border-gray-300 rounded-md px-2 py-1 text-xs focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />

              <button @click="clearDateFilters" class="mt-2 text-xs text-red-600 hover:text-red-800 font-medium">Limpiar
                Filtro de Fechas</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <FuelReportModal v-if="showReport" :initial-start="fechaInicio" :initial-end="fechaFin"
      :initial-device-id="selectedDevices.length === 1 ? selectedDevices[0] : ''" @close="showReport = false" />

    <!-- Contador de registros -->
    <div class="flex justify-end mb-4">
      <div class="text-xs font-semibold text-gray-700 p-1.5 bg-blue-100 rounded-md whitespace-nowrap">
        Mostrando <span class="text-blue-700">{{ paginatedDatos.length }}</span> de
        <span class="text-blue-700">{{ filteredDatos.length }}</span> registros
        <span v-if="selectedRange && selectedRange !== 'all'" class="ml-1 text-gray-500 italic">
          ({{dateOptions.find(o => o.key === selectedRange)?.label}})
        </span>
      </div>
    </div>

    <!-- Tabla principal -->
    <div class="bg-white rounded-lg shadow-xl overflow-hidden">
      <!-- Encabezado -->
      <div v-if="filteredDatos.length > 0"
        class="hidden sm:flex items-center p-3 bg-gray-800 text-white font-semibold uppercase tracking-wider select-none text-xs">
        <h3 class="w-1/4 cursor-pointer" @click="ordenarPor('fecha')">
          Fecha / Hora <span v-if="sortBy === 'fecha'">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
        </h3>
        <h3 v-if="selectedDevices.length > 1" class="w-1/6 text-left cursor-pointer"
          @click="ordenarPor('dispositivo_nombre')">
          Dispositivo <span v-if="sortBy === 'dispositivo_nombre'">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
        </h3>
        <h3 :class="selectedDevices.length > 1 ? 'w-[10%]' : 'w-1/6'" class="text-right cursor-pointer"
          @click="ordenarPor('litros')">
          Litros <span v-if="sortBy === 'litros'">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
        </h3>
        <h3 :class="selectedDevices.length > 1 ? 'w-[15%]' : 'w-1/6'" class="text-right cursor-pointer"
          @click="ordenarPor('ibutton')">
          iButton ID <span v-if="sortBy === 'ibutton'">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
        </h3>
        <h3 :class="selectedDevices.length > 1 ? 'w-1/4' : 'w-1/4'" class="text-center">COD Equipo</h3>
        <h3 :class="selectedDevices.length > 1 ? 'w-[10%]' : 'w-1/6'" class="text-center">ACC Negocio</h3>
      </div>

      <!-- Filas de datos -->
      <div v-if="paginatedDatos.length > 0" class="divide-y divide-gray-100 max-h-[50vh] overflow-y-auto">
        <div v-for="(item, index) in paginatedDatos" :key="index"
          class="p-3 transition duration-150 hover:bg-blue-50 even:bg-white odd:bg-gray-50">
          <!-- Desktop -->
          <div class="hidden sm:flex items-center gap-3 text-sm text-gray-700">
            <div class="w-1/4 font-mono font-medium text-blue-700 truncate text-xs">{{ formatearFecha(item.fecha) }}
            </div>
            <div v-if="selectedDevices.length > 1" class="w-1/6 text-left font-semibold text-xs text-gray-600 truncate">
              {{ getDeviceName(item.dispositivo_id) }}
            </div>
            <div :class="selectedDevices.length > 1 ? 'w-[10%]' : 'w-1/6'"
              class="text-right font-bold text-gray-800 text-sm">
              {{ Number(item.litros).toLocaleString('es-CL') }} L
            </div>

            <div :class="selectedDevices.length > 1 ? 'w-[15%]' : 'w-1/6'"
              class="text-right font-mono text-xs text-gray-600 truncate">
              {{ ibuttonAlias[item.ibutton] ?? item.ibutton }}
            </div>
            <div :class="selectedDevices.length > 1 ? 'w-1/4' : 'w-1/4'" class="text-center text-xs">
              <select v-model="item.dato1_id" @change="updateItemReference(item, 'dato1_id', $event.target.value)"
                class="w-full border border-gray-300 rounded-md px-1 py-1 text-xs bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition cursor-pointer">
                <option :value="null" :selected="!item.dato1_id">Seleccionar...</option>
                <option v-for="d1 in dato1Data" :key="d1.id" :value="d1.id">{{ d1.nombre }}</option>
              </select>
            </div>
            <div :class="selectedDevices.length > 1 ? 'w-[10%]' : 'w-1/6'" class="text-center text-xs">
              <select v-model="item.dato2_id" @change="updateItemReference(item, 'dato2_id', $event.target.value)"
                class="w-full border border-gray-300 rounded-md px-1 py-1 text-xs bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition cursor-pointer">
                <option :value="null" :selected="!item.dato2_id">Seleccionar...</option>
                <option v-for="d2 in dato2Data" :key="d2.id" :value="d2.id">{{ d2.nombre }}</option>
              </select>
            </div>
          </div>

          <!-- Mobile -->
          <div class="sm:hidden grid grid-cols-2 gap-y-1 text-xs">
            <div class="font-semibold text-gray-600">Fecha/Hora:</div>
            <div class="font-medium text-blue-700 text-right">{{ formatearFecha(item.fecha) }}</div>

            <template v-if="selectedDevices.length > 1">
              <div class="font-semibold text-gray-600">Dispositivo:</div>
              <div class="font-semibold text-gray-600 text-right">{{ getDeviceName(item.dispositivo_id) }}</div>
            </template>

            <div class="font-semibold text-gray-600">Litros:</div>
            <div class="font-bold text-gray-800 text-right">
              {{ Number(item.litros).toLocaleString('es-CL') }} L
            </div>


            <div class="font-semibold text-gray-600">iButton ID:</div>
            <div class="font-mono text-gray-600 text-right truncate">{{ item.ibutton }}</div>

            <div class="font-semibold text-gray-600">Dato 1:</div>
            <div class="text-right text-xs">
              <select v-model="item.dato1_id" @change="updateItemReference(item, 'dato1_id', $event.target.value)"
                class="w-full border border-gray-300 rounded-md px-1 py-1 text-xs bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition cursor-pointer">
                <option :value="null" :selected="!item.dato1_id">Seleccionar...</option>
                <option v-for="d1 in dato1Data" :key="d1.id" :value="d1.id">{{ d1.nombre }}</option>
              </select>
            </div>

            <div class="font-semibold text-gray-600">Dato 2:</div>
            <div class="text-right text-xs">
              <select v-model="item.dato2_id" @change="updateItemReference(item, 'dato2_id', $event.target.value)"
                class="w-full border border-gray-300 rounded-md px-1 py-1 text-xs bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition cursor-pointer">
                <option :value="null" :selected="!item.dato2_id">Seleccionar...</option>
                <option v-for="d2 in dato2Data" :key="d2.id" :value="d2.id">{{ d2.nombre }}</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Mensaje vacío -->
      <div v-else class="p-6 text-center text-gray-500 text-sm">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 mx-auto mb-2 text-gray-400" fill="none"
          viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="M9 13h6m-3-3v6m-9 1l4 4-4 4m6 7h12a2 2 0 002-2v-8a2 2 0 00-2-2H9a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        <p v-if="datos.length === 0">No se encontraron registros de datos en el sistema.</p>
        <p v-else>No hay registros que coincidan con los filtros y la búsqueda aplicados.</p>
        <button
          v-if="datos.length > 0 && (searchTerm || selectedDevices.length < dispositivos.length || selectedRange !== 'all')"
          @click="clearAllFilters"
          class="mt-3 text-blue-600 hover:text-blue-800 font-medium text-xs transition duration-150">
          Limpiar todos los filtros y búsqueda
        </button>
      </div>
    </div>

    <!-- Paginación -->
    <div v-if="filteredDatos.length > 0"
      class="flex flex-col sm:flex-row justify-between items-center mt-4 text-xs text-gray-700 bg-white p-3 rounded-lg shadow-inner gap-2 border border-gray-200">
      <div class="flex items-center gap-2">
        <label for="rowsPerPage" class="font-medium text-gray-600">Filas por pág:</label>
        <select id="rowsPerPage" v-model.number="rowsPerPage"
          class="border border-gray-300 rounded-md px-2 py-1 text-xs bg-gray-50 focus:ring-blue-500 focus:border-blue-500 transition">
          <option v-for="n in rowsPerPageOptions" :key="n" :value="n">{{ n }}</option>
        </select>
        <span class="text-gray-500 text-xs italic">Máx. {{ totalPages > 1 ? rowsPerPage : filteredDatos.length }}</span>
      </div>

      <div class="flex items-center gap-3">
        <button @click="previousPage" :disabled="currentPage === 1"
          class="px-2 py-1 rounded-md bg-gray-100 border border-gray-300 text-blue-600 disabled:opacity-50 hover:bg-blue-600 hover:text-white transition duration-150 shadow-sm">
          <SvgIcon name="chevron-left" class="w-3 h-3" />
        </button>

        <span class="font-medium">Pág. <span class="text-blue-700 font-bold">{{ currentPage }}</span> /
          <span class="text-blue-700 font-bold">{{ totalPages }}</span></span>

        <button @click="nextPage" :disabled="currentPage === totalPages"
          class="px-2 py-1 rounded-md bg-gray-100 border border-gray-300 text-blue-600 disabled:opacity-50 hover:bg-blue-600 hover:text-white transition duration-150 shadow-sm">
          <SvgIcon name="chevron-right" class="w-3 h-3" />
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import axios from "axios";
import SvgIcon from '@/components/icons/SvgIcon.vue';
import { useDataFilters } from '@/utils/useDataFilters.js';
import FuelReportModal from '@/components/Reports/FuelReportModal.vue';

import { ibuttonAlias } from '@/config/ibuttonAliases';

const BACKEND_URL =
  process.env.VUE_APP_BACKEND_URL || "http://localhost:8081";

console.log("🔧 BACKEND_URL (Datos/Table):", BACKEND_URL);


// Directiva para cerrar dropdown al hacer click fuera
const vClickOutside = {
  mounted(el, binding) {
    el.__ClickOutsideHandler__ = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event);
      }
    };
    document.body.addEventListener('click', el.__ClickOutsideHandler__);
  },
  unmounted(el) {
    document.body.removeEventListener('click', el.__ClickOutsideHandler__);
  }
};

export default {
  components: { SvgIcon, FuelReportModal },
  directives: { 'click-outside': vClickOutside },
  setup() {
    // Estados principales
    const datos = ref([]);
    const dato1Data = ref([]);
    const dato2Data = ref([]);
    const dispositivos = ref([]);
    const showReport = ref(false);
    const openReport = () => {
      filters.closeAllDropdowns();
      showReport.value = true;
    };

    // Cargar datos de referencia
    const fetchReferenceData = async (endpoint, dataRef) => {
      try {
        const res = await axios.get(`${BACKEND_URL}/${endpoint}`);
        dataRef.value = res.data;
      } catch (err) {
        console.error(`❌ Error al cargar ${endpoint}:`, err);
      }
    };

    // Cargar datos principales con filtros
    const fetchDatos = async () => {
      let url = `${BACKEND_URL}/datos`;
      let params = {};
      if (filters.fechaInicio.value && filters.fechaFin.value) {
        params.fecha_inicio = filters.fechaInicio.value;
        params.fecha_fin = filters.fechaFin.value;
      }

      try {
        const res = await axios.get(url, { params });
        datos.value = Array.isArray(res.data) ? res.data : [];
      } catch (err) {
        console.error("❌ Error al obtener datos de /datos", err);
        datos.value = [];
      }
    };

    // Composable de filtros
    const filters = useDataFilters(datos, dispositivos, fetchDatos);

    // Cargar dispositivos desde backend y seleccionar todos por defecto
    const fetchDispositivos = async () => {
      try {
        const res = await axios.get(`${BACKEND_URL}/dispositivos`);
        dispositivos.value = Array.isArray(res.data) ? res.data : [];
        const allIds = dispositivos.value.map(d => d.id);
        filters.selectedDevices.value = [...allIds];
      } catch (err) {
        console.error("⚠️ Error al cargar dispositivos:", err);
      }
    };

    // Actualizar referencia en un item
    const updateItemReference = async (item, field, value) => {
      let finalValue = value === 'null' || value === '' ? null : parseInt(value, 10);
      item[field] = finalValue;

      let method = item.id ? 'PATCH' : 'POST';
      let url = item.id ? `${BACKEND_URL}/datos/${item.id}` : `${BACKEND_URL}/datos`;
      let payload = item.id ? { [field]: finalValue } : { ...item, [field]: finalValue };

      try {
        const res = await axios({ method, url, data: payload });
        if (method === 'POST') item.id = res.data.id;

        // ✅ Recargar datos con los filtros actuales
        await fetchDatos();
      } catch (error) {
        console.error(`❌ Error al ${method === 'POST' ? 'crear' : 'actualizar'} registro`, error);
      }
    };


    // Formatear fecha
    const formatearFecha = (isoString) => {
      if (!isoString) return 'N/A';
      const date = new Date(isoString);
      return date.toLocaleString('es-CL', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        hour12: false
      });
    };

    // Carga inicial
    onMounted(async () => {
      await fetchReferenceData('dato1', dato1Data);
      await fetchReferenceData('dato2', dato2Data);
      await fetchDispositivos();
      filters.applyDateRange('all');
      await fetchDatos();
    });

    return {
      datos, dato1Data, dato2Data, dispositivos, ibuttonAlias, showReport, openReport,
      updateItemReference, formatearFecha,
      ...filters,
    };
  }
};
</script>
