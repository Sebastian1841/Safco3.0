<template>
<div class="p-3 sm:p-4 bg-gray-50 min-h-screen font-sans w-full overflow-x-hidden">

    <!-- Capa cierre dropdowns -->
    <div v-if="showDropdownDevices || showDropdownDates" @click="closeAllDropdowns" class="fixed inset-0 z-10">
    </div>

    <!-- HEADER FILTROS -->
    <div class="flex flex-col lg:flex-row justify-between lg:items-center mb-4 gap-3 w-full">

        <!-- ⭐ BOTÓN RESPONSIVE -->
        <button @click="emitirModalNivel" class="w-full sm:w-auto px-4 py-2 bg-green-600 text-white font-medium rounded-md 
               hover:bg-green-700 transition shadow-sm text-sm text-center">
            Ver Nivel de Estanque
        </button>

        <!-- FILTROS -->
        <!-- 🔧 FIX: que no se desborde en móvil -->
        <div class="flex flex-wrap justify-start sm:justify-end items-center gap-2 w-full lg:w-auto">

            <!-- Dropdown Dispositivos -->
            <div class="relative z-20" v-click-outside="closeDropdownDevices">
                <button @click="toggleDropdown('devices')" class="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white font-medium rounded-md 
                   hover:bg-blue-700 transition shadow-sm text-xs sm:text-sm w-full sm:w-auto">
                    <SvgIcon name="chevron-down" class="w-4 h-4" />
                    <span>Dispositivos ({{ selectedDevices.length }})</span>
                </button>

                <!-- 🔧 FIX COMPLETO RESPONSIVE -->
                <div v-if="showDropdownDevices" class="absolute z-30 mt-1 
                   left-0 sm:left-auto right-0
                   bg-white border border-gray-300 rounded-lg 
                   shadow-xl w-48 max-h-52 overflow-y-auto">

                    <div @click="toggleSelectAllDevices" class="flex items-center px-3 py-1.5 bg-gray-100 hover:bg-gray-200 cursor-pointer border-b">
                        <input type="checkbox" :checked="allDevicesSelected" class="mr-2 h-3 w-3" />
                        <span class="text-xs sm:text-sm font-bold text-gray-800">
                            {{ allDevicesSelected ? 'Deseleccionar Todos' : 'Seleccionar Todos' }}
                        </span>
                    </div>

                    <div v-for="device in dispositivos" :key="device.id" @click="toggleDeviceSelection(device.id)" class="flex items-center px-3 py-1.5 hover:bg-blue-50 cursor-pointer">
                        <input type="checkbox" :checked="selectedDevices.includes(device.id)" class="mr-2 h-3 w-3" />
                        <span class="text-xs sm:text-sm">{{ device.nombre }}</span>
                    </div>
                </div>
            </div>

            <!-- Dropdown Fechas -->
            <div class="relative z-20" v-click-outside="closeDropdownDates">
                <button @click="toggleDropdown('dates')" class="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white font-medium rounded-md 
                   hover:bg-blue-700 transition duration-150 shadow-sm text-xs sm:text-sm w-full sm:w-auto">
                    <SvgIcon name="calendar-range" class="w-3 h-3 sm:w-4 sm:h-4" />
                    <span>Rango de Fechas</span>
                </button>

                <!-- 🔧 FIX COMPLETO RESPONSIVE -->
                <div v-if="showDropdownDates" class="absolute z-20 mt-1 
                   left-0 sm:left-auto right-0
                   bg-white border border-gray-300 rounded-lg shadow-xl 
                   p-3 w-64">

                    <div class="mb-3 border-b pb-3 border-gray-100">
                        <label class="text-xs font-semibold">Selección Rápida:</label>
                        <select v-model="selectedRange" @change="applyDateRange(selectedRange)" class="w-full border px-2 py-1.5 text-xs rounded-md bg-white">
                            <option :value="null" disabled>-- Rango Predefinido --</option>
                            <option v-for="option in dateOptions" :key="option.key" :value="option.key">
                                {{ option.label }}
                            </option>
                        </select>
                    </div>

                    <div class="flex flex-col gap-2 text-gray-700">
                        <label class="text-xs font-semibold">Fecha Inicio:</label>
                        <input type="date" v-model="fechaInicio" @input="clearSelectedRange" class="border rounded-md px-2 py-1 text-xs" />

                        <label class="text-xs font-semibold">Fecha Fin:</label>
                        <input type="date" v-model="fechaFin" @input="clearSelectedRange" class="border rounded-md px-2 py-1 text-xs" />

                        <button @click="clearDateFilters" class="mt-2 text-xs text-red-600 hover:text-red-800 font-medium">
                            Limpiar Filtro de Fechas
                        </button>
                    </div>

                </div>
            </div>

        </div>
    </div>

    <!-- CONTENEDOR GRÁFICAS -->
    <div class="bg-white rounded-lg shadow p-3 space-y-6 w-full overflow-hidden">

        <div class="w-full max-w-full overflow-hidden">
            <CakeChart :fecha-inicio="fechaInicio" :fecha-fin="fechaFin" :selected-devices="selectedDevices" :selected-range="selectedRange" />
        </div>

        <div class="w-full max-w-full overflow-hidden">
            <BarsChart :fecha-inicio="fechaInicio" :fecha-fin="fechaFin" :selected-devices="selectedDevices" :selected-range="selectedRange" :dispositivos="dispositivos" />
        </div>

    </div>

    <!-- MODAL NIVEL -->
    <ModalNivelEstanque v-if="showModalNivel" :nivelFijo="nivelFijo" :nivelMovil="nivelMovil" :maxFijo="maxFijoTotal" :maxMovil="maxMovilTotal" :historial="historial" :dispositivos="dispositivos" @cerrar="showModalNivel = false" />

</div>
</template>

<script>
import {
    ref,
    onMounted,
    watch,
    computed
} from "vue";
import axios from "axios";

import ModalNivelEstanque from "@/components/DashboardUi/ModalNivelEstanque.vue";
import CakeChart from "@/components/DashboardUi/CakeChart.vue";
import BarsChart from "@/components/DashboardUi/BarsChart.vue";
import SvgIcon from "@/components/icons/SvgIcon.vue";

import {
    useDataFilters
} from "@/utils/useDataFilters.js";
import {
    kpiStore
} from "@/stores/kpiStore.js";

export default {
    name: "SafcoDashboard",
    components: {
        CakeChart,
        BarsChart,
        ModalNivelEstanque,
        SvgIcon
    },

    setup() {
        const BACKEND_URL =
            process.env.VUE_APP_BACKEND_URL || "http://localhost:8081";
        console.log("🔧 BACKEND_URL (SafcoDashboard):", BACKEND_URL);

        const cargasCombustible = ref([]);
        const dispositivos = ref([]);
        const datosDummy = ref([]);
        const manuales = ref([]);
        const manualesFiltrados = ref([]);
        const facturas = ref([]);
        const showModalNivel = ref(false);

        let filters = useDataFilters(datosDummy, dispositivos, fetchDatos);

        const datosCharts = ref([]);

        function emitirModalNivel() {
            showModalNivel.value = true;
        }

        /* ===========================
           CARGAS MANUALES
        ============================ */
        async function fetchNiveles() {
            const res = await axios.get(`${BACKEND_URL}/cargas_combustible`);
            cargasCombustible.value = Array.isArray(res.data) ? res.data : [];
        }

        /* ===========================
           MANUALES
        ============================ */
        async function fetchManuales() {
            const r = await axios.get(`${BACKEND_URL}/litros_control`);
            manuales.value = Array.isArray(r.data) ? r.data : [];
            filtrarManuales();
        }

        function filtrarManuales() {
            const now = new Date();
            const last24 = new Date(now.getTime() - 24 * 3600 * 1000);

            let result = [...manuales.value];

            if (filters.selectedDevices.value.length)
                result = result.filter(m =>
                    filters.selectedDevices.value.includes(Number(m.dispositivo))
                );

            if (filters.selectedRange.value === "last_week")
                result = result.filter(m => new Date(m.fecha) >= now - 7 * 86400000);

            else if (filters.selectedRange.value === "last_month")
                result = result.filter(m => new Date(m.fecha) >= now - 30 * 86400000);

            else if (filters.fechaInicio.value && filters.fechaFin.value) {
                const ini = new Date(filters.fechaInicio.value);
                const fin = new Date(filters.fechaFin.value + "T23:59:59");
                result = result.filter(m => new Date(m.fecha) >= ini && new Date(m.fecha) <= fin);
            } else result = result.filter(m => new Date(m.fecha) >= last24);

            manualesFiltrados.value = result;
        }

        /* ===========================
           FACTURAS 
        ============================ */
        async function fetchFacturas() {
            const r = await axios.get(`${BACKEND_URL}/facturas/listar`);
            facturas.value = Array.isArray(r.data) ? r.data : [];
        }

        /* ===========================
          FACTURAS (FECHA FIX)
        =========================== */
        // ⭐ CONVERTIR "DD-MM-YYYY" → "YYYY-MM-DD"
        function toISO(fecha) {
            const [dd, mm, yyyy] = fecha.split("-");
            return `${yyyy}-${mm}-${dd}`;
        }

        /* ===========================
           NIVELES + HISTORIAL
        ============================ */

        const nivelesCalculados = computed(() => {
            const eventos = [];

            const nombreEstanque = id =>
                id === 1 ? "Estanque Fijo" : id === 2 ? "Estanque Móvil" : "Estanque";

            if (!cargasCombustible.value.length && !facturas.value.length) {
                return {
                    fijo: 0,
                    movil: 0,
                    maxFijo: 0,
                    maxMovil: 0,
                    eventos: []
                };
            }

            // Obtener fecha de inicio general
            const allFechas = [
                ...cargasCombustible.value.map(c => new Date(`${c.fecha}T${c.hora}`)),
                ...facturas.value.map(f => new Date(`${f.fecha}T00:00:00`))
            ];

            const primeraCarga = allFechas.sort((a, b) => a - b)[0];

            let raw = [];

            // ----------------------------
            // CARGAS MANUALES
            // ----------------------------
            cargasCombustible.value.forEach(c => {
                raw.push({
                    tipo: "carga",
                    origen: "manual",
                    dispositivo: Number(c.dispositivo_id),
                    fechaISO: `${c.fecha}T${c.hora}`,
                    cantidad: Number(c.litros_total)
                });
            });

            // ----------------------------
            // ⭐ CARGAS DESDE FACTURAS (solo Estanque Fijo)
            // ----------------------------
            facturas.value.forEach(f => {
                raw.push({
                    tipo: "carga",
                    origen: "factura",
                    dispositivo: 1,
                    fechaISO: `${toISO(f.fecha)}T00:00:00`,
                    cantidad: Number(f.litros)
                });
            });

            // ----------------------------
            // DESCARGAS (datos sensor TB)
            // ----------------------------
            datosDummy.value.forEach(d => {
                const fechaTB = new Date(d.fecha);

                if (fechaTB >= primeraCarga) {
                    raw.push({
                        tipo: "descarga",
                        origen: "sensor", // ⭐ NUEVO
                        dispositivo: Number(d.dispositivo_id),
                        fechaISO: d.fecha,
                        cantidad: Number(d.litros)
                    });
                }
            });

            // Orden temporal
            raw.sort((a, b) => new Date(a.fechaISO) - new Date(b.fechaISO));

            let nivelFijo = 0;
            let nivelMovil = 0;
            let maxFijo = 0;
            let maxMovil = 0;

            raw.forEach(ev => {
                const fechaObj = new Date(ev.fechaISO);
                let totalPosterior = 0;

                // FIJO
                if (ev.dispositivo === 1) {
                    if (ev.tipo === "carga") nivelFijo += ev.cantidad;
                    if (ev.tipo === "descarga") nivelFijo -= ev.cantidad;
                    totalPosterior = nivelFijo;
                    maxFijo = Math.max(maxFijo, totalPosterior);
                }

                // MOVIL
                if (ev.dispositivo === 2) {
                    if (ev.tipo === "carga") nivelMovil += ev.cantidad;
                    if (ev.tipo === "descarga") nivelMovil -= ev.cantidad;
                    totalPosterior = nivelMovil;
                    maxMovil = Math.max(maxMovil, totalPosterior);
                }

                eventos.push({
                    tipo: ev.tipo,
                    origen: ev.origen, // ⭐ NUEVO
                    descripcion: ev.origen === "factura" ?
                        "Carga por Factura COPEC" :
                        ev.origen === "manual" ?
                        "Carga Manual" :
                        "Descarga de combustible",
                    cantidad: ev.cantidad,
                    estanque: nombreEstanque(ev.dispositivo),
                    total_posterior: totalPosterior,
                    fecha_texto: fechaObj.toLocaleDateString("es-CL"),
                    hora_texto: fechaObj.toLocaleTimeString("es-CL", {
                        hour12: false
                    }),
                    _orden: fechaObj.getTime()
                });
            });

            return {
                fijo: nivelFijo,
                movil: nivelMovil,
                maxFijo,
                maxMovil,
                eventos: eventos.sort((a, b) => b._orden - a._orden)
            };
        });

        /* ===========================
           DISPOSITIVOS
        ============================ */
        async function fetchDispositivos() {
            const res = await axios.get(`${BACKEND_URL}/dispositivos`);
            dispositivos.value = Array.isArray(res.data) ? res.data : [];
            filters.selectedDevices.value = dispositivos.value.map(d => d.id);
        }

        /* ===========================
           DATOS SENSOR
        ============================ */
        async function fetchDatos() {
            const r = await axios.get(`${BACKEND_URL}/datos`);
            datosDummy.value = Array.isArray(r.data) ? r.data : [];
            filters.filtrarDatos();
            datosCharts.value = [...filters.filteredDatos.value];
        }

        /* ===========================
           MOUNT
        ============================ */
        onMounted(async () => {
            await fetchDispositivos();
            await fetchDatos();
            await fetchManuales();
            await fetchFacturas(); // ⭐ IMPORTANTE
            await fetchNiveles();

            kpiStore.updateKPIs({
                datos: filters.filteredDatos.value,
                manuales: manualesFiltrados.value,
                dispositivos: dispositivos.value,
                cargas: cargasCombustible.value,
                facturas: facturas.value
            });
        });

        /* ===========================
           WATCHERS
        ============================ */
        watch(
            [filters.selectedDevices, filters.selectedRange, filters.fechaInicio, filters.fechaFin],
            () => {
                datosCharts.value = [...filters.filteredDatos.value];
                filtrarManuales();

                kpiStore.updateKPIs({
                    datos: filters.filteredDatos.value,
                    manuales: manualesFiltrados.value,
                    dispositivos: dispositivos.value,
                    cargas: cargasCombustible.value,
                    facturas: facturas.value
                });
            }, {
                deep: true
            }
        );

        return {
            showModalNivel,
            emitirModalNivel,
            dispositivos,

            datosCharts,
            facturas,

            nivelFijo: computed(() => nivelesCalculados.value.fijo),
            nivelMovil: computed(() => nivelesCalculados.value.movil),
            maxFijoTotal: computed(() => nivelesCalculados.value.maxFijo),
            maxMovilTotal: computed(() => nivelesCalculados.value.maxMovil),
            historial: computed(() => nivelesCalculados.value.eventos),

            ...filters,
            manualesFiltrados
        };
    }
};
</script>

<style scoped></style>
