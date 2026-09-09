<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 w-full">

    <!-- Litros Totales Estanque Fijo -->
    <div class="p-4 bg-white rounded-xl shadow border border-gray-100 flex flex-col">
      <p class="text-gray-500 text-xs font-semibold">Litros Totales</p>
      <p class="text-gray-900 text-sm font-medium">Estanque Fijo</p>
      <h2 class="text-2xl font-bold text-blue-600 mt-2">
        {{ Math.round(litrosFijo).toLocaleString('es-CL', { minimumFractionDigits: 0, maximumFractionDigits: 0 }) }} L
      </h2>
    </div>

    <!-- Litros Totales Estanque Móvil -->
    <div class="p-4 bg-white rounded-xl shadow border border-gray-100 flex flex-col">
      <p class="text-gray-500 text-xs font-semibold">Litros Totales</p>
      <p class="text-gray-900 text-sm font-medium">Estanque Móvil</p>
      <h2 class="text-2xl font-bold text-green-600 mt-2">
        {{ Math.round(litrosMovil).toLocaleString('es-CL', { minimumFractionDigits: 0, maximumFractionDigits: 0 }) }} L
      </h2>
    </div>

    <!-- Litros Manuales Estanque Fijo -->
    <div class="p-4 bg-white rounded-xl shadow border border-gray-100 flex flex-col">
      <p class="text-gray-500 text-xs font-semibold">Litros Manuales</p>
      <p class="text-gray-900 text-sm font-medium">Estanque Fijo</p>
      <h2 class="text-2xl font-bold text-red-600 mt-2">
        {{ manualFijo.toLocaleString('es-CL') }} L
      </h2>
    </div>

    <!-- Litros Manuales Estanque Móvil -->
    <div class="p-4 bg-white rounded-xl shadow border border-gray-100 flex flex-col">
      <p class="text-gray-500 text-xs font-semibold">Litros Manuales</p>
      <p class="text-gray-900 text-sm font-medium">Estanque Móvil</p>
      <h2 class="text-2xl font-bold text-orange-600 mt-2">
        {{ manualMovil.toLocaleString('es-CL') }} L
      </h2>
    </div>

  </div>
</template>

<script setup>
import { computed, defineProps } from "vue";

const props = defineProps({
  datos: { type: Array, default: () => [] },
  manuales: { type: Array, default: () => [] },
  dispositivos: { type: Array, default: () => [] }
});

// Resolver tipo cuando backend no lo trae
const dispositivosConTipo = computed(() =>
  props.dispositivos.map(d => ({
    ...d,
    tipo: d.nombre.toLowerCase().includes("mov") ? "movil" : "fijo"
  }))
);

// Totales
const litrosFijo = computed(() =>
  props.datos
    .filter(d => {
      const dev = dispositivosConTipo.value.find(x => x.id === d.dispositivo_id);
      return dev && dev.tipo === "fijo";
    })
    .reduce((t, r) => t + Number(r.litros || 0), 0)
);

const litrosMovil = computed(() =>
  props.datos
    .filter(d => {
      const dev = dispositivosConTipo.value.find(x => x.id === d.dispositivo_id);
      return dev && dev.tipo === "movil";
    })
    .reduce((t, r) => t + Number(r.litros || 0), 0)
);

const manualFijo = computed(() =>
  props.manuales
    .filter(d => {
      const dev = dispositivosConTipo.value.find(x => x.id === d.dispositivo);
      return dev && dev.tipo === "fijo";
    })
    .reduce((t, r) => t + Math.abs(Number(r.diferencia_manual || 0)), 0)
);

const manualMovil = computed(() =>
  props.manuales
    .filter(d => {
      const dev = dispositivosConTipo.value.find(x => x.id === d.dispositivo);
      return dev && dev.tipo === "movil";
    })
    .reduce((t, r) => t + Math.abs(Number(r.diferencia_manual || 0)), 0)
);
</script>
