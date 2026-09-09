<template>
  <div class="bg-gray-50 min-h-screen">
    <Tables @update-kpis="updateKPIs" />
  </div>
</template>

<script>
import Tables from '@/components/Tables/DataTables.vue'
import { kpiStore } from '@/stores/kpiStore.js'   // 🟦 IMPORTANTE

export default {
  name: 'SafcoTables',
  components: { Tables },

  setup() {

    // 🔥 Esta función actualiza los KPIs globales
    function updateKPIs(payload) {
      kpiStore.updateKPIs({
        datos: payload.datos || [],
        manuales: payload.manuales || [],
        dispositivos: payload.dispositivos || [],
        cargas: payload.cargas || []
      })
    }

    return { updateKPIs }
  }
}
</script>

<style scoped>
/* estilos opcionales */
</style>
