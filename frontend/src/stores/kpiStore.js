// src/stores/kpiStore.js
import { reactive } from "vue";

export const kpiStore = reactive({
  datos: [],
  manuales: [],
  dispositivos: [],
  cargas: [],

  updateKPIs(payload = {}) {
    this.datos = payload.datos || [];
    this.manuales = payload.manuales || [];
    this.dispositivos = payload.dispositivos || [];
    this.cargas = payload.cargas || [];
  }
});
