<template>
  <div class="
    flex flex-col bg-gray-100 
    min-h-screen 
    md:h-screen md:overflow-hidden
  ">
    <AppHeader @toggle-sidebar="toggleSidebar" />

    <div class="flex flex-1 overflow-auto md:overflow-hidden">
      <AppSidebar :isOpen="showSidebar" @update:isOpen="val => showSidebar = val" />

      <div class="flex flex-col flex-1">

        <!-- KPI GLOBAL -->
        <div
          class="
            p-2 bg-white shadow-md border-b border-gray-200
            z-10
            md:z-50 md:sticky md:top-0
          "
        >
          <KpiCards
            :datos="kpiStore.datos"
            :manuales="kpiStore.manuales"
            :dispositivos="kpiStore.dispositivos"
            :cargas="kpiStore.cargas"
          />
        </div>

        <main class="flex-1 p-4 overflow-auto bg-[#f3f3f3]">
          <router-view />
        </main>

      </div>
    </div>
  </div>
</template>


<script setup>
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppSidebar from './components/AppSidebar.vue'
import KpiCards from "@/components/DashboardUi/KpiCards.vue"
import { kpiStore } from '@/stores/kpiStore.js'

const showSidebar = ref(false)
const toggleSidebar = () => showSidebar.value = !showSidebar.value
</script>

<style>

canvas {
  max-width: 100% !important;
  width: 100% !important;
  display: block !important;
}

.chartjs-size-monitor,
.chartjs-size-monitor-expand,
.chartjs-size-monitor-shrink {
  max-width: 100% !important;
  overflow: hidden !important;
}

.chartjs-render-monitor {
  max-width: 100% !important;
}

.responsive-container {
  width: 100% !important;
  max-width: 100% !important;
  overflow-x: hidden !important;
}
</style>
