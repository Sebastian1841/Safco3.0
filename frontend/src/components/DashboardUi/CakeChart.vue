<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    
    <LitrosPorIbutton 
      :fecha-inicio="fechaInicio"
      :fecha-fin="fechaFin"
      :selected-devices="selectedDevices"
      :selected-range="selectedRange"
    />

    <PorcentajeDato1 
      :fecha-inicio="fechaInicio"
      :fecha-fin="fechaFin"
      :selected-devices="selectedDevices"
      :selected-range="selectedRange"
    />

    <PorcentajeDato2 
      :fecha-inicio="fechaInicio"
      :fecha-fin="fechaFin"
      :selected-devices="selectedDevices"
      :selected-range="selectedRange"
    />

  </div>
</template>

<script setup>
import { defineProps } from "vue";

import LitrosPorIbutton from "./pies/LitrosPorIbutton.vue";
import PorcentajeDato1 from "./pies/PorcentajeDato1.vue";
import PorcentajeDato2 from "./pies/PorcentajeDato2.vue";

defineProps({
  fechaInicio: String,
  fechaFin: String,
  selectedDevices: Array,
  selectedRange: String
});
</script>
