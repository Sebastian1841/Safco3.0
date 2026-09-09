<template>
    <div class="bg-gray-50 p-4 rounded-xl shadow">

        <!-- ===================================================== -->
        <!--                        HEADER                         -->
        <!-- ===================================================== -->
        <div class="flex flex-col lg:flex-row justify-between items-center gap-3 mb-4">

            <h2 class="text-lg font-semibold text-gray-800">Gestión de Facturas</h2>

            <div class="flex items-center gap-2">

                <!-- BOTÓN INGRESAR FACTURA -->
                <button @click="$emit('nuevaFactura')" class="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 
                    text-white font-medium rounded-lg shadow transition text-sm">
                    <SvgIcon name="plus" class="w-4 h-4" />
                    Ingresar Factura
                </button>

                <!-- BOTÓN ELIMINAR -->
                <transition name="fade">
                    <button v-if="selected.length > 0" @click="$emit('eliminarSeleccionadas')" class="flex items-center gap-2 px-3 py-2 bg-red-600 hover:bg-red-700 
                        text-white font-medium rounded-lg shadow transition text-sm">
                        <SvgIcon name="trash" class="w-4 h-4" />
                        Eliminar ({{ selected.length }})
                    </button>
                </transition>

            </div>
        </div>

        <!-- ===================================================== -->
        <!--                   FILTROS SUPERIORES                  -->
        <!-- ===================================================== -->
        <div class="flex flex-wrap gap-3 items-center mb-4">

            <!-- BUSCADOR -->
            <div class="flex flex-1 min-w-[260px]">
                <div class="flex w-full border border-gray-300 rounded-lg overflow-hidden bg-white shadow-sm">
                    <div class="flex items-center justify-center px-3 bg-gray-100 text-gray-500">
                        <SvgIcon name="search" class="w-4 h-4" />
                    </div>
                    <input v-model="search" placeholder="Buscar factura..."
                        class="flex-1 p-2 text-sm bg-white text-gray-800 placeholder-gray-400 focus:outline-none" />
                    <button v-if="search" @click="search = ''"
                        class="px-3 bg-red-500 hover:bg-red-600 text-white text-xs transition">
                        Limpiar
                    </button>
                </div>
            </div>

            <!-- ===================== -->
            <!--       PROVEEDOR       -->
            <!-- ===================== -->
            <div class="relative" v-click-outside="() => showProv = false">
                <button @click="showProv = !showProv"
                    class="px-3 py-2 bg-[#2563eb] rounded-lg text-white text-sm shadow-sm flex items-center gap-2">
                    <SvgIcon name="filter" class="w-4 h-4" />
                    {{ filtroProveedor || 'Proveedor' }}
                </button>

                <div v-if="showProv" class="absolute mt-2 w-48 bg-white rounded-xl shadow-lg border z-20 py-2">
                    <div class="px-3 py-1 text-xs text-gray-500 border-b">Seleccionar proveedor</div>

                    <div v-for="p in proveedoresUnicos" :key="p" @click="filtroProveedor = p; showProv = false"
                        class="px-3 py-2 text-sm hover:bg-blue-50 cursor-pointer">
                        {{ p }}
                    </div>
                </div>
            </div>

            <!-- ===================== -->
            <!--        FECHAS         -->
            <!-- ===================== -->
            <div class="relative" v-click-outside="() => showFecha = false">
                <button @click="closeAllDropdowns(); showFecha = !showFecha"
                    class="px-3 py-2 bg-[#2563eb] border rounded-lg text-white text-sm shadow-sm flex items-center gap-2">
                    <SvgIcon name="calendar" class="w-4 h-4" />
                    Fechas
                </button>

                <div v-if="showFecha"
                    class="absolute right-0 mt-2 w-56 bg-white p-4 rounded-xl shadow-lg border z-20 space-y-3">

                    <div>
                        <label class="text-xs text-gray-600">Desde</label>
                        <input type="date" v-model="fechaDesde" class="w-full px-2 py-1 border rounded-lg text-sm" />
                    </div>

                    <div>
                        <label class="text-xs text-gray-600">Hasta</label>
                        <input type="date" v-model="fechaHasta" class="w-full px-2 py-1 border rounded-lg text-sm" />
                    </div>

                    <button @click="fechaDesde = ''; fechaHasta = ''; showFecha = false"
                        class="w-full py-1 bg-gray-200 hover:bg-gray-300 rounded-lg text-xs font-medium text-gray-700">
                        Limpiar
                    </button>
                </div>
            </div>

            <!-- ===================== -->
            <!--     ORDEN CAMPO       -->
            <!-- ===================== -->
            <div class="relative" v-click-outside="() => showOrden = false">
                <button @click="showOrden = !showOrden"
                    class="px-3 py-2 bg-[#2563eb] rounded-lg text-white text-sm shadow-sm">
                    {{ ordenCampo || 'Ordenar por' }}
                </button>

                <div v-if="showOrden" class="absolute mt-2 w-44 bg-white rounded-xl shadow-lg border z-20 py-2">
                    <div v-for="campo in ['fecha', 'total', 'litros', 'numero']" :key="campo"
                        @click="ordenCampo = campo; showOrden = false"
                        class="px-3 py-2 text-sm hover:bg-blue-50 cursor-pointer capitalize">
                        {{ campo }}
                    </div>
                </div>
            </div>
        </div>

        <!-- ===================================================== -->
        <!--                SELECCIONAR TODAS                      -->
        <!-- ===================================================== -->
        <div class="flex items-center gap-2 mb-3">
            <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll"
                class="h-4 w-4 rounded border-gray-400" />
            <span class="text-xs text-gray-700 font-medium">Seleccionar todas</span>
        </div>

        <!-- ===================================================== -->
        <!--                     CARDS LIST                        -->
        <!-- ===================================================== -->
        <div class="max-h-[60vh] overflow-y-auto space-y-2 pr-1">

            <div v-for="f in paginated" :key="f.id"
                class="border border-gray-200 rounded-xl p-3 bg-white shadow-sm hover:shadow transition">

                <div class="flex items-start gap-3">

                    <input type="checkbox" :value="f.id" v-model="selected"
                        class="h-4 w-4 mt-1 rounded border-gray-400" />

                    <div class="flex-1 space-y-1.5">

                        <div class="flex justify-between items-center">
                            <h3 class="text-sm font-semibold text-gray-800">Nº {{ f.numero_factura }}</h3>

                            <div class="flex gap-1 items-center">
                                <span v-if="esNotaCredito(f)"
                                    class="text-[10px] px-2 py-0.5 rounded border font-medium bg-purple-100 text-purple-700 border-purple-300">
                                    Nota de Crédito
                                </span>

                                <span :class="badgeProveedor(f.proveedor)"
                                    class="text-[10px] px-2 py-0.5 rounded border font-medium">
                                    {{ f.proveedor || '—' }}
                                </span>
                            </div>
                        </div>

                        <p class="text-xs text-gray-600 font-medium truncate">
                            {{ f.producto }}
                        </p>

                        <div class="flex gap-2 mt-2">

                            <div class="flex-1 p-2 bg-blue-50 rounded-lg border border-blue-100 text-center">
                                <div class="text-blue-700 font-bold text-sm">
                                    {{ formatNumber(Math.round(toNumber(f.litros))) }} L
                                </div>
                            </div>

                            <div class="flex-1 p-2 bg-gray-50 rounded-lg border border-gray-200 text-center">
                                <div class="font-medium text-gray-700 text-sm">
                                    {{ f.fecha }}
                                </div>
                            </div>

                            <div class="flex-1 p-2 rounded-lg border text-center"
                                :class="esNotaCredito(f) ? 'bg-red-50 border-red-100' : 'bg-green-50 border-green-100'">
                                <div class="font-bold text-sm"
                                    :class="esNotaCredito(f) ? 'text-red-700' : 'text-green-700'">
                                    {{ formatCurrency(totalMostrado(f)) }}
                                </div>
                            </div>

                        </div>

                    </div>
                </div>
            </div>

            <!-- SIN DATOS -->
            <div v-if="paginated.length === 0"
                class="text-center py-6 text-gray-500 bg-gray-100 rounded-lg border border-gray-300 text-sm">
                No se encontraron facturas.
            </div>

        </div>

        <!-- ===================================================== -->
        <!--                     PAGINACIÓN                        -->
        <!-- ===================================================== -->
        <div
            class="flex justify-between items-center mt-4 text-xs text-gray-700 bg-white p-3 rounded-lg border shadow-inner">

            <div class="flex items-center gap-2">
                <span class="font-medium">Filas:</span>
                <select v-model.number="rows" class="border rounded px-2 py-1 bg-gray-50 focus:ring-blue-500 text-xs">
                    <option v-for="n in [5, 10, 25, 50, 100]" :key="n">{{ n }}</option>
                </select>
            </div>

            <div class="flex items-center gap-3">
                <button @click="prevPage" :disabled="page === 1"
                    class="px-2 py-1 border rounded bg-gray-100 hover:bg-blue-600 hover:text-white disabled:opacity-50">
                    <SvgIcon name="chevron-left" class="w-3 h-3" />
                </button>

                <span>Pág. <b>{{ page }}</b> / <b>{{ totalPages }}</b></span>

                <button @click="nextPage" :disabled="page === totalPages"
                    class="px-2 py-1 border rounded bg-gray-100 hover:bg-blue-600 hover:text-white disabled:opacity-50">
                    <SvgIcon name="chevron-right" class="w-3 h-3" />
                </button>
            </div>

        </div>
    </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import SvgIcon from "@/components/icons/SvgIcon.vue";

const props = defineProps({
    facturas: Array,
    modelValue: { type: Array, default: () => [] }
});

const emit = defineEmits(["update:modelValue", "nuevaFactura", "eliminarSeleccionadas"]);


// ========= MULTISELECT ==========
const selected = ref([...props.modelValue]);

function arraysIguales(a, b) {
    if (a.length !== b.length) return false;
    return a.every(v => b.includes(v));
}

// hijo → padre
watch(selected, (val) => {
    if (!arraysIguales(val, props.modelValue)) {
        emit("update:modelValue", val);
    }
});

// padre → hijo
watch(() => props.modelValue, (val) => {
    if (!arraysIguales(val, selected.value)) {
        selected.value = [...val];
    }
});


// ========= ESTADOS DE FILTROS ==========
const search = ref("");
const filtroProveedor = ref("");
const fechaDesde = ref("");
const fechaHasta = ref("");

const showProv = ref(false);
const showOrden = ref(false);
const showFecha = ref(false);

const ordenCampo = ref("");
const ordenDir = ref("asc");
const rows = ref(5);
const page = ref(1);


// ========= CERRAR TODO ==========
const closeAllDropdowns = () => {
    showProv.value = false;
    showOrden.value = false;
    showFecha.value = false;
};


// ========= FORMATEO SEGURO ==========
const toNumber = (value) => {
    const num = Number(value);

    if (value === null || value === undefined || value === "" || Number.isNaN(num)) {
        return 0;
    }

    return num;
};

const formatNumber = (value) => {
    return toNumber(value).toLocaleString("es-CL");
};

const formatCurrency = (value) => {
    return toNumber(value).toLocaleString("es-CL", {
        style: "currency",
        currency: "CLP",
        maximumFractionDigits: 0
    });
};


// ========= NOTA DE CRÉDITO ==========
const normalizarTexto = (value) => {
    return String(value || "")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim();
};

const esNotaCredito = (factura) => {
    const texto = [
        factura?.tipo,
        factura?.tipo_documento,
        factura?.documento,
        factura?.descripcion,
        factura?.producto,
        factura?.numero_factura,
        factura?.proveedor
    ].map(normalizarTexto).join(" ");

    return (
        texto.includes("nota de credito") ||
        texto.includes("nota credito") ||
        texto.includes("notacredito") ||
        normalizarTexto(factura?.tipo) === "nota de credito" ||
        normalizarTexto(factura?.tipo_documento) === "nota de credito" ||
        toNumber(factura?.total) < 0
    );
};

const totalMostrado = (factura) => {
    const total = toNumber(factura?.total);
    return esNotaCredito(factura) ? -Math.abs(total) : total;
};

// ========= PARSE DE FECHAS ROBUSTO ==========
const parseFecha = (valor) => {
    if (!valor) return null;

    // YYYY-MM-DD
    if (/^\d{4}-\d{2}-\d{2}$/.test(valor)) {
        return new Date(valor + "T00:00:00");
    }

    // DD-MM-YYYY
    if (/^\d{2}-\d{2}-\d{4}$/.test(valor)) {
        const [d, m, y] = valor.split("-");
        return new Date(`${y}-${m}-${d}T00:00:00`);
    }

    return new Date(valor);
};


// ========= PROVEEDORES ÚNICOS ==========
const proveedoresUnicos = computed(() => {
    const set = new Set((props.facturas || []).map(f => f.proveedor || "—"));
    return [...set];
});


// ========= BADGES ==========
function badgeProveedor(p) {
    p = (p || "").toUpperCase();
    if (p.includes("COPEC")) return "bg-red-100 text-red-700 border-red-300";
    if (p.includes("SHELL")) return "bg-yellow-100 text-yellow-700 border-yellow-300";
    return "bg-gray-100 text-gray-700 border-gray-300";
}


// ========= BÚSQUEDA GLOBAL ==========
const matchSearch = (factura, query) => {
    query = query.toLowerCase();

    return (
        factura.numero_factura?.toLowerCase().includes(query) ||
        factura.producto?.toLowerCase().includes(query) ||
        factura.proveedor?.toLowerCase().includes(query) ||
        ("" + factura.litros).toLowerCase().includes(query) ||
        ("" + factura.total).toLowerCase().includes(query) ||
        factura.fecha?.toLowerCase().includes(query) ||
        (esNotaCredito(factura) && "nota de credito".includes(query))
    );
};


// ========= FILTRADO COMPLETO ==========
const filtradas = computed(() => {
    let list = [...(props.facturas || [])];

    // 🔍 BUSCAR EN TODA LA FACTURA
    if (search.value.trim()) {
        const q = search.value.toLowerCase();
        list = list.filter(f => matchSearch(f, q));
    }

    // 📌 FILTRAR POR PROVEEDOR
    if (filtroProveedor.value) {
        list = list.filter(f => (f.proveedor || "—") === filtroProveedor.value);
    }

    // 📅 FECHA DESDE
    if (fechaDesde.value) {
        const desde = parseFecha(fechaDesde.value);
        list = list.filter(f => {
            const fechaFactura = parseFecha(f.fecha);
            return fechaFactura && fechaFactura >= desde;
        });
    }

    // 📅 FECHA HASTA
    if (fechaHasta.value) {
        const hasta = parseFecha(fechaHasta.value);
        hasta.setHours(23, 59, 59, 999);
        list = list.filter(f => {
            const fechaFactura = parseFecha(f.fecha);
            return fechaFactura && fechaFactura <= hasta;
        });
    }

    // 🔽 ORDENAMIENTO
    list.sort((a, b) => {
        if (!ordenCampo.value) return 0;

        let A = a[ordenCampo.value];
        let B = b[ordenCampo.value];

        if (ordenCampo.value === "fecha") {
            A = parseFecha(a.fecha)?.getTime() || 0;
            B = parseFecha(b.fecha)?.getTime() || 0;
        } else if (ordenCampo.value === "total") {
            A = totalMostrado(a);
            B = totalMostrado(b);
        } else {
            A = toNumber(A);
            B = toNumber(B);
        }

        return ordenDir.value === "asc" ? A - B : B - A;
    });

    return list;
});


// ========= MULTISELECT ==========
const isAllSelected = computed(() =>
    filtradas.value.length > 0 &&
    filtradas.value.every(f => selected.value.includes(f.id))
);

const toggleSelectAll = () => {
    if (isAllSelected.value) selected.value = [];
    else selected.value = filtradas.value.map(f => f.id);
};


// ========= PAGINACIÓN ==========
const totalPages = computed(() => Math.ceil(filtradas.value.length / rows.value));

const paginated = computed(() => {
    const start = (page.value - 1) * rows.value;
    return filtradas.value.slice(start, start + rows.value);
});

watch([rows, filtradas], () => (page.value = 1));

const nextPage = () => page.value < totalPages.value && page.value++;
const prevPage = () => page.value > 1 && page.value--;
</script>


<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity .25s;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>