<template>
  <div class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 p-3">

    <!-- MODAL -->
    <div class="w-full max-w-3xl bg-gradient-to-br from-white to-slate-100 rounded-2xl shadow-2xl p-6 relative
             max-h-[90vh] overflow-y-auto transform transition-all scale-100">

      <!-- BOTÓN CERRAR -->
      <button @click="$emit('cerrar')"
        class="absolute top-3 right-4 text-xl text-slate-500 hover:text-sky-500 transition">
        ✕
      </button>

      <h2 class="text-center text-3xl font-extrabold text-slate-800 mb-8">
        <span class="block text-sky-600 tracking-wide text-base font-semibold mb-2">
          — Nivel Actual de Estanque —
        </span>
      </h2>



      <!-- CONTENEDOR PRINCIPAL -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

        <!-- ====================== F I J O ====================== -->
        <div
          class="bg-slate-50 border border-slate-200 rounded-xl shadow-sm p-5 flex flex-col items-center gap-4 hover:shadow-lg transition">
          <h3 class="text-lg font-semibold text-sky-700">Estanque fijo</h3>

          <!-- GAUGE -->
          <div class="flex justify-center w-full h-[210px] md:h-[220px]">
            <FuelGaugeF :litros="nivelFijo" :max="maxFijo" />
          </div>

          <!-- SELECT -->
          <select v-model="selectedFijo" class="w-full border border-slate-300 rounded-md px-3 py-2 text-sm bg-white shadow-sm
                   focus:border-sky-500 focus:ring-2 focus:ring-sky-300 transition">
            <option v-for="d in dispositivosFijo" :key="d.id" :value="d.id">
              {{ d.nombre }}
            </option>
          </select>
        </div>

        <!-- ====================== M Ó V I L ====================== -->
        <div
          class="bg-slate-50 border border-slate-200 rounded-xl shadow-sm p-5 flex flex-col items-center gap-4 hover:shadow-lg transition">
          <h3 class="text-lg font-semibold text-sky-700">Estanque móvil</h3>

          <!-- GAUGE -->
          <div class="flex justify-center w-full h-[210px] md:h-[220px]">
            <FuelGaugeM :litros="nivelMovil" :max="maxMovil" />
          </div>

          <!-- SELECT -->
          <select v-model="selectedMovil" class="w-full border border-slate-300 rounded-md px-3 py-2 text-sm bg-white shadow-sm
                   focus:border-sky-500 focus:ring-2 focus:ring-sky-300 transition">
            <option v-for="d in dispositivosMovil" :key="d.id" :value="d.id">
              {{ d.nombre }}
            </option>
          </select>
        </div>

      </div>

      <!-- ======================== HISTORIAL ======================== -->
      <div class="mt-7">
        <h3 class="text-sm font-semibold text-slate-600 mb-3">
          Historial de movimientos
        </h3>

        <HistorialEstanque :eventos="historial" />
      </div>

    </div>

  </div>
</template>



<script setup>
import FuelGaugeF from "@/components/DashboardUi/Nivel_Estanque/FuelGaugeFijo.vue";
import FuelGaugeM from "@/components/DashboardUi/Nivel_Estanque/FuelGaugeMovil.vue";
import HistorialEstanque from "@/components/DashboardUi/Nivel_Estanque/HistorialEstanque.vue";

import { ref, computed, onMounted } from "vue";

const props = defineProps({
  nivelFijo: Number,
  nivelMovil: Number,
  maxFijo: Number,
  maxMovil: Number,
  historial: { type: Array, default: () => [] },
  dispositivos: { type: Array, default: () => [] },
});


const selectedFijo = ref(null);
const selectedMovil = ref(null);

onMounted(() => {
  selectedFijo.value =
    props.dispositivos.find(d => d.nombre.toLowerCase().includes("fijo"))?.id || null;

  selectedMovil.value =
    props.dispositivos.find(d => d.nombre.toLowerCase().includes("mov"))?.id || null;
});

const dispositivosFijo = computed(() =>
  props.dispositivos.filter(d => d.nombre.toLowerCase().includes("fijo"))
);

const dispositivosMovil = computed(() =>
  props.dispositivos.filter(d => d.nombre.toLowerCase().includes("mov"))
);
</script>
