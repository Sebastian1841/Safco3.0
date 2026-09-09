// src/utils/useDataFilters.js
import { ref, computed, watch } from 'vue';

let _store = null;

/**
 * Lógica de filtrado, búsqueda, ordenación, paginación y control visual de dropdowns.
 * - Primer llamado: pásale (initialDataRef, dispositivosRef, fetchDatosFunction) para inicializar.
 * - Llamados siguientes (ej. desde App.vue): llama sin argumentos y reutiliza el mismo estado.
 */
export function useDataFilters(initialDataRef, dispositivosRef, fetchDatosFunction) {
  if (_store) return _store;

  // --- si no vino initialDataRef en el primer llamado, crea refs internos (fallback) ---
  const _initialDataRef = initialDataRef ?? ref([]);
  const _dispositivosRef = dispositivosRef ?? ref([]);

  // 🔹 Estados de Filtros
  const searchTerm = ref("");
  const selectedDevices = ref(_dispositivosRef.value.map(d => d.id));
  const fechaInicio = ref("");
  const fechaFin = ref("");
  const selectedRange = ref('all');

  // 💡 ESTADOS DE INTERFAZ
  const showDropdownDevices = ref(false);
  const showDropdownDates = ref(false);

  // 🔹 Opciones estáticas
  const dateOptions = ref([
    { key: 'last_hour', label: 'Última Hora' },
    { key: 'last_12_hours', label: 'Últimas 12 Hrs' },
    { key: 'last_week', label: 'Última Semana' },
    { key: 'last_month', label: 'Último Mes' },
    { key: 'last_6_months', label: 'Últimos 6 Meses' },
    { key: 'all', label: 'Rango Por Defecto' },
  ]);

  // 🔹 Ordenación
  const sortBy = ref(null);
  const sortOrder = ref("asc");

  // 🔹 Paginación
  const rowsPerPageOptions = [5, 10, 20, 50];
  const rowsPerPage = ref(5);
  const currentPage = ref(1);

  // --- Visual ---
  const closeDropdownDevices = () => { showDropdownDevices.value = false; };
  const closeDropdownDates = () => { showDropdownDates.value = false; };
  const closeAllDropdowns = () => {
    showDropdownDevices.value = false;
    showDropdownDates.value = false;
  };
  const toggleDropdown = (type) => {
    if (type === 'devices') {
      showDropdownDevices.value = !showDropdownDevices.value;
      showDropdownDates.value = false;
    } else if (type === 'dates') {
      showDropdownDates.value = !showDropdownDates.value;
      showDropdownDevices.value = false;
    }
  };

  // --- Helpers Dispositivos ---
  const allDeviceIds = computed(() => _dispositivosRef.value.map(d => d.id));
  const allDevicesSelected = computed(() => selectedDevices.value.length === allDeviceIds.value.length);
  const getDeviceName = (id) => {
    const device = _dispositivosRef.value.find(d => d.id === id);
    return device ? device.nombre : 'Desconocido';
  };
  const toggleDeviceSelection = (deviceId) => {
    const index = selectedDevices.value.indexOf(deviceId);
    if (index === -1) {
      selectedDevices.value.push(deviceId);
    } else {
      if (selectedDevices.value.length > 1) {
        selectedDevices.value.splice(index, 1);
      }
    }
  };
  const toggleSelectAllDevices = () => {
    if (allDevicesSelected.value) {
      selectedDevices.value = [_dispositivosRef.value[0]?.id].filter(Boolean);
    } else {
      selectedDevices.value = [...allDeviceIds.value];
    }
  };

  // --- Helpers Fechas ---
  const formatearFecha = (ts) => {
    const fecha = new Date(ts);
    return fecha.toLocaleString("es-CL", { year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false });
  };
  const toYMDLocal = (d) => {
    const pad = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  };

  const clearSelectedRange = () => { selectedRange.value = null; };

  const clearDateFilters = () => {
    fechaInicio.value = "";
    fechaFin.value = "";
    selectedRange.value = 'all';
  };

  const applyDateRange = (key) => {
    if (!key || key === 'all') {
      clearDateFilters();
      return;
    }
    const now = new Date();
    let fechaInicioCalc = null;

    if (key === 'last_hour') fechaInicioCalc = new Date(now.getTime() - 1 * 60 * 60 * 1000);
    else if (key === 'last_12_hours') fechaInicioCalc = new Date(now.getTime() - 12 * 60 * 60 * 1000);
    else if (key === 'last_week') fechaInicioCalc = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    else if (key === 'last_month') { fechaInicioCalc = new Date(now); fechaInicioCalc.setMonth(now.getMonth() - 1); }
    else if (key === 'last_6_months') { fechaInicioCalc = new Date(now); fechaInicioCalc.setMonth(now.getMonth() - 6); }

    fechaFin.value = toYMDLocal(now);
    fechaInicio.value = toYMDLocal(fechaInicioCalc);
    selectedRange.value = key;
  };

  const clearAllFilters = () => {
    searchTerm.value = "";
    selectedDevices.value = [...allDeviceIds.value];
    clearDateFilters();
  };

  // --- Trigger opcional para compatibilidad con `filters.filtrarDatos()`
  const _touch = ref(0);
  const filtrarDatos = () => { _touch.value++; }; // no-op para forzar recompute si lo llamas

  // --- Filtrado General ---
  const filteredDatos = computed(() => {
    void _touch.value;

    let lista = _initialDataRef.value.filter(item =>
      selectedDevices.value.includes(item.dispositivo_id)
    );

    const now = new Date();

    if (selectedRange.value === "last_hour") {
      lista = lista.filter(item => new Date(item.fecha) >= new Date(now.getTime() - 1 * 60 * 60 * 1000));
    } else if (selectedRange.value === "last_12_hours") {
      lista = lista.filter(item => new Date(item.fecha) >= new Date(now.getTime() - 12 * 60 * 60 * 1000));
    } else if (selectedRange.value === "last_week") {
      lista = lista.filter(item => new Date(item.fecha) >= new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000));
    } else if (selectedRange.value === "last_month") {
      lista = lista.filter(item => new Date(item.fecha) >= new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000));
    } else if (fechaInicio.value && fechaFin.value) {
      const ini = new Date(`${fechaInicio.value}T00:00:00`);
      const fin = new Date(`${fechaFin.value}T23:59:59`);
      lista = lista.filter(item => new Date(item.fecha) >= ini && new Date(item.fecha) <= fin);
    } else {
      const cutoff = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      lista = lista.filter(item => new Date(item.fecha) >= cutoff);
    }

    if (searchTerm.value) {
      const s = searchTerm.value.toLowerCase();

      lista = lista.filter(item => {
        const compare = (val) => String(val || "").toLowerCase().includes(s);

        return (
          compare(new Date(item.fecha).toLocaleString("es-CL")) ||
          compare(getDeviceName(item.dispositivo_id)) ||
          compare(item.litros) ||
          compare(item.ibutton) ||
          compare(item.dato1_nombre) ||
          compare(item.dato2_nombre)
        );
      });
    }


    // ✅ ORDENACIÓN QUE FALTABA
    if (sortBy.value) {
      lista = lista.slice().sort((a, b) => {
        let x = a[sortBy.value];
        let y = b[sortBy.value];

        if (sortBy.value === "fecha") {
          x = new Date(x);
          y = new Date(y);
        }

        if (x < y) return sortOrder.value === "asc" ? -1 : 1;
        if (x > y) return sortOrder.value === "asc" ? 1 : -1;
        return 0;
      });
    }

    return lista;
  });


  // --- Paginación ---
  const totalPages = computed(() => Math.ceil(filteredDatos.value.length / rowsPerPage.value) || 1);
  const paginatedDatos = computed(() => {
    const start = (currentPage.value - 1) * rowsPerPage.value;
    return filteredDatos.value.slice(start, start + rowsPerPage.value);
  });

  const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++; };
  const previousPage = () => { if (currentPage.value > 1) currentPage.value--; };

  // --- Watchers ---
  watch([rowsPerPage, filteredDatos], () => currentPage.value = 1);
  watch(selectedDevices, () => { currentPage.value = 1; });
  watch([fechaInicio, fechaFin, selectedRange], () => {
    if (fetchDatosFunction) fetchDatosFunction();
  }, { immediate: false, deep: false });

  _store = {
    // fuentes compartidas
    initialDataRef: _initialDataRef,
    dispositivosRef: _dispositivosRef,

    // filtros/estado
    searchTerm, selectedDevices, fechaInicio, fechaFin, selectedRange,
    showDropdownDevices, showDropdownDates,
    sortBy, sortOrder, rowsPerPage, currentPage,

    // computed y helpers
    allDevicesSelected, filteredDatos, paginatedDatos, totalPages, allDeviceIds,
    dateOptions, rowsPerPageOptions,
    toggleDropdown, closeDropdownDevices, closeDropdownDates, closeAllDropdowns,
    clearSelectedRange, clearDateFilters, clearAllFilters, applyDateRange,
    toggleDeviceSelection, toggleSelectAllDevices,
    ordenarPor: (campo) => {
      if (sortBy.value === campo) {
        sortOrder.value = (sortOrder.value === "asc") ? "desc" : "asc";
      } else {
        sortBy.value = campo;
        sortOrder.value = "asc";
      }
    },
    nextPage, previousPage, getDeviceName, formatearFecha,
    filtrarDatos,
  };

  return _store;
}
