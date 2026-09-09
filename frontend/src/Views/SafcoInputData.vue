<template>
  <div class="p-4 sm:p-6 bg-gray-50 min-h-screen font-sans">

    <!-- ===================== MODAL DE EDICIÓN ===================== -->
    <div v-if="editingItem" class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-2xl w-full max-w-lg p-6">

        <h2 class="text-xl font-bold mb-4 text-blue-700">
          Editar:
          {{ editingItem.type === "litros"
            ? "Control de Consumo"
            : `Dato ${editingItem.type.slice(-1)}` }}
        </h2>

        <form @submit.prevent="saveEdit">

          <!-- === EDICIÓN DATO 1 / DATO 2 === -->
          <div v-if="editingItem.type === 'dato1' || editingItem.type === 'dato2'">
            <label class="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
            <input type="text" v-model="editingItem.item.nombre" required
              class="w-full border border-gray-300 rounded-md p-2 text-sm" />
          </div>

          <!-- === EDICIÓN LITROS === -->
          <div v-else-if="editingItem.type === 'litros'">

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Fecha</label>
                <input type="date" v-model="editingItem.item.fecha" required
                  class="w-full border border-gray-300 rounded-md p-2 text-sm" />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Dispositivo</label>
                <select v-model="editingItem.item.dispositivo" required
                  class="w-full border border-gray-300 rounded-md p-2 text-sm bg-white">
                  <option v-for="d in dispositivos" :key="d.id" :value="d.id">
                    {{ getOptionLabel(d) }}
                  </option>
                </select>
              </div>

            </div>

            <div class="flex gap-4 mb-4">

              <div class="flex-1">
                <label class="block text-sm font-medium text-gray-700 mb-1">Inicial</label>
                <input type="number" v-model.number="editingItem.item.litros_inicio" step="0.01" min="0" required
                  class="w-full border border-gray-300 rounded-md p-2 text-sm" />
              </div>

              <div class="flex-1">
                <label class="block text-sm font-medium text-gray-700 mb-1">Final</label>
                <input type="number" v-model.number="editingItem.item.litros_final" step="0.01" min="0" required
                  class="w-full border border-gray-300 rounded-md p-2 text-sm" />
              </div>

            </div>

            <div class="text-xs font-semibold p-2 rounded-md bg-red-100 text-red-800">
              El valor final debe ser mayor o igual al inicial.
            </div>
          </div>
          <!-- === EDICIÓN CARGA DE COMBUSTIBLE === -->
          <div v-else-if="editingItem.type === 'carga'">

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Fecha de Carga</label>
                <input type="date" v-model="editingItem.item.fecha" required
                  class="w-full border border-gray-300 rounded-md p-2 text-sm" />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Dispositivo/Vehículo</label>
                <select v-model="editingItem.item.dispositivo_id" required
                  class="w-full border border-gray-300 rounded-md p-2 text-sm bg-white">
                  <option disabled value="">Seleccione un dispositivo</option>
                  <option v-for="d in dispositivos" :key="d.id" :value="d.id">
                    {{ getOptionLabel(d) }}
                  </option>
                </select>
              </div>

            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Litros Cargados</label>
              <input type="number" v-model.number="editingItem.item.litros_total" step="0.01" min="0" required
                class="w-full border border-gray-300 rounded-md p-2 text-sm" />
            </div>

          </div>


          <div class="mt-6 flex justify-end gap-3">
            <button type="button" @click="cancelEdit"
              class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 text-sm">
              Cancelar
            </button>

            <button type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 shadow-md text-sm">
              Guardar Cambios
            </button>
          </div>

        </form>

      </div>
    </div>

    <!-- ===================== FORMULARIOS SUPERIORES (2 columnas) ===================== -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
      <Dato1Form :items="dato1Data" @add="addDato1" @edit="startEdit('dato1', $event)" @delete="deleteDato1" />

      <Dato2Form :items="dato2Data" @add="addDato2" @edit="startEdit('dato2', $event)" @delete="deleteDato2" />
    </div>

    <!-- ===================== FORMULARIOS INFERIORES (2 columnas ordenadas) ===================== -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">

      <!-- DESCARGA -->
      <LitrosControl :items="litrosControlData" :dispositivos="dispositivos" :getLabel="getOptionLabel"
        :getLabelById="getOptionLabelById" @add="addLitrosControl" @edit="startEdit('litros', $event)"
        @delete="deleteLitrosControl" />

      <!-- CARGA -->
      <CargaCombustible :items="cargasData" :dispositivos="dispositivos" :getLabel="getOptionLabel"
        :getLabelById="getOptionLabelById" @add="addCarga" @edit="startEdit('carga', $event)" @delete="deleteCarga" />

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

import Dato1Form from "@/components/InputDataUi/Dato1Form.vue";
import Dato2Form from "@/components/InputDataUi/Dato2Form.vue";
import LitrosControl from "@/components/InputDataUi/LitrosControl.vue";
import CargaCombustible from "@/components/InputDataUi/CargaCombustible.vue";

import { kpiStore } from "@/stores/kpiStore.js";   // 🟦 AGREGADO

// 🔧 IMPORTANTE: ahora apuntamos al backend en 8081 (expuesto por Docker)
const BACKEND_URL =
  process.env.VUE_APP_BACKEND_URL || "http://localhost:8081";

console.log("🔧 BACKEND_URL (InputData/SafcoDashboard):", BACKEND_URL);

/* ===================== ESTADOS ===================== */
const editingItem = ref(null);

const dispositivos = ref([]);
const dato1Data = ref([]);
const dato2Data = ref([]);
const litrosControlData = ref([]);
const cargasData = ref([]);

/* ===================== UTILS ===================== */
const getOptionLabel = (d) => d.nombre;

const getOptionLabelById = (id) => {
  const dev = dispositivos.value.find((d) => d.id === id);
  return dev ? dev.nombre : `Dispositivo ${id}`;
};

/* ===================== KPI UPDATE GLOBAL ===================== */
function updateKPIs() {
  kpiStore.updateKPIs({
    datos: litrosControlData.value,       // descargas
    manuales: litrosControlData.value,    // también consumos manuales si quieres
    dispositivos: dispositivos.value,
    cargas: cargasData.value
  });
}

/* ===================== EDICIÓN ===================== */
const startEdit = (type, item) => {
  editingItem.value = {
    type,
    item: { ...item },
    originalItem: item,
  };

  if (type === "litros") {
    editingItem.value.item.litros_inicio = Number(item.litros_inicio);
    editingItem.value.item.litros_final = Number(item.litros_final);
  }
};

const cancelEdit = () => {
  editingItem.value = null;
};

const saveEdit = async () => {
  if (!editingItem.value) return;

  const { type, item, originalItem } = editingItem.value;
  let url = "";
  let payload = {};

  try {
    if (type === "dato1") {
      url = `${BACKEND_URL}/dato1/${item.id}`;
      payload = { nombre: item.nombre.trim() };
    }

    if (type === "dato2") {
      url = `${BACKEND_URL}/dato2/${item.id}`;
      payload = { nombre: item.nombre.trim() };
    }

    if (type === "litros") {
      if (item.litros_inicio > item.litros_final) return;

      url = `${BACKEND_URL}/litros_control/${item.id}`;
      payload = {
        ...item,
        diferencia_manual: item.litros_final - item.litros_inicio,
      };
    }

    if (type === "carga") {
      url = `${BACKEND_URL}/cargas_combustible/${item.id}`;
      payload = { ...item };
    }

    const res = await axios.put(url, payload);
    Object.assign(originalItem, res.data);

    editingItem.value = null;

    updateKPIs();   // 🟦 ACTUALIZAR KPIs

  } catch (err) {
    console.error("❌ Error guardando edición:", err);
  }
};

/* ===================== LOADERS API ===================== */
const fetchDispositivos = async () => {
  try {
    const r = await axios.get(`${BACKEND_URL}/dispositivos`);
    dispositivos.value = r.data;
  } catch (err) {
    console.error("❌ Error cargando dispositivos:", err);
  }
};

const fetchDato1 = async () => {
  try {
    const r = await axios.get(`${BACKEND_URL}/dato1`);
    dato1Data.value = r.data;
  } catch (err) {
    console.error("❌ Error cargando Dato 1:", err);
  }
};

const fetchDato2 = async () => {
  try {
    const r = await axios.get(`${BACKEND_URL}/dato2`);
    dato2Data.value = r.data;
  } catch (err) {
    console.error("❌ Error cargando Dato 2:", err);
  }
};

const fetchLitrosControl = async () => {
  try {
    const r = await axios.get(`${BACKEND_URL}/litros_control`);
    litrosControlData.value = r.data.sort(
      (a, b) => new Date(b.fecha) - new Date(a.fecha)
    );
  } catch (err) {
    console.error("❌ Error cargando Litros Control:", err);
  }
};

const fetchCargas = async () => {
  try {
    const r = await axios.get(`${BACKEND_URL}/cargas_combustible`);
    cargasData.value = r.data.sort(
      (a, b) => new Date(b.fecha) - new Date(a.fecha)
    );
  } catch (err) {
    console.error("❌ Error cargando cargas:", err);
  }
};

/* ===================== ACCIONES: ADD ===================== */
const addDato1 = async (nombre) => {
  const r = await axios.post(`${BACKEND_URL}/dato1`, { nombre });
  dato1Data.value.push(r.data);
  updateKPIs();     // 🟦
};

const addDato2 = async (nombre) => {
  const r = await axios.post(`${BACKEND_URL}/dato2`, { nombre });
  dato2Data.value.push(r.data);
  updateKPIs();     // 🟦
};

const addLitrosControl = async (nuevo) => {
  const diferencia_manual = nuevo.litros_final - nuevo.litros_inicio;

  const r = await axios.post(`${BACKEND_URL}/litros_control`, {
    ...nuevo,
    diferencia_manual,
  });

  litrosControlData.value.unshift(r.data);
  updateKPIs();     // 🟦
};

const addCarga = async (nuevo) => {
  try {
    const r = await axios.post(`${BACKEND_URL}/cargas_combustible`, nuevo);
    cargasData.value.unshift(r.data);
    updateKPIs();   // 🟦
  } catch (err) {
    console.error("❌ Error registrando carga:", err);
  }
};

/* ===================== ELIMINAR ===================== */
const deleteDato1 = async (id) => {
  await axios.delete(`${BACKEND_URL}/dato1/${id}`);
  dato1Data.value = dato1Data.value.filter((x) => x.id !== id);
  updateKPIs();     // 🟦
};

const deleteDato2 = async (id) => {
  await axios.delete(`${BACKEND_URL}/dato2/${id}`);
  dato2Data.value = dato2Data.value.filter((x) => x.id !== id);
  updateKPIs();     // 🟦
};

const deleteLitrosControl = async (id) => {
  await axios.delete(`${BACKEND_URL}/litros_control/${id}`);
  litrosControlData.value = litrosControlData.value.filter((x) => x.id !== id);
  updateKPIs();     // 🟦
};

const deleteCarga = async (id) => {
  await axios.delete(`${BACKEND_URL}/cargas_combustible/${id}`);
  cargasData.value = cargasData.value.filter((x) => x.id !== id);
  updateKPIs();     // 🟦
};

/* ===================== MOUNT ===================== */
onMounted(async () => {
  await fetchDispositivos();
  await fetchDato1();
  await fetchDato2();
  await fetchLitrosControl();
  await fetchCargas();

  updateKPIs();     // 🟦 Inicial
});
</script>
