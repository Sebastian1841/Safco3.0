<template>
  <div class="bg-white p-4 sm:p-6 rounded-lg shadow-xl border border-gray-200">

    <h2 class="text-xl font-semibold text-[#4f46e5] mb-4 flex items-center gap-2">
      Registro Manual de Carga de Combustible (Nivel)
    </h2>

    <!-- FORMULARIO -->
    <form @submit.prevent="onAdd" class="flex flex-col gap-4 mb-6">

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">

        <!-- FECHA -->
        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">Fecha</label>
          <input type="date" v-model="form.fecha" required
            class="w-full border border-gray-300 rounded-md p-2 text-sm 
            focus:ring-green-500 focus:border-green-500" />
        </div>

        <!-- HORA -->
        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">Hora</label>
          <input type="time" v-model="form.hora" required
            class="w-full border border-gray-300 rounded-md p-2 text-sm 
            focus:ring-green-500 focus:border-green-500" />
        </div>

        <!-- DISPOSITIVO -->
        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">Dispositivo / Vehículo</label>
          <select v-model="form.dispositivo_id" required
            class="w-full border border-gray-300 rounded-md p-2 text-sm bg-white 
            focus:ring-green-500 focus:border-green-500">
            <option disabled value="">Seleccione un dispositivo</option>

            <option v-for="d in dispositivos" :key="d.id" :value="d.id">
              {{ getLabel(d) }}
            </option>
          </select>
        </div>

      </div>

      <!-- LITROS -->
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-1">Litros Cargados</label>
        <input type="number" v-model.number="form.litros_total" required step="0.01" min="0"
          class="w-full border border-gray-300 rounded-md p-2 text-sm 
          focus:ring-green-500 focus:border-green-500" placeholder="0.00" />
      </div>

      <button type="submit"
        class="sm:w-full px-4 py-2 bg-[#4f46e5] text-white font-medium rounded-md 
        hover:bg-indigo-700 shadow-md text-sm">
        Registrar Carga de Combustible
      </button>

    </form>

    <!-- LISTA -->
    <h3 class="text-sm font-bold text-gray-700 mt-4 mb-2 border-t pt-4">
      Cargas Registradas ({{ items.length }})
    </h3>

    <div class="max-h-60 overflow-y-auto border border-gray-100 rounded-md p-2 bg-gray-50">

      <ul v-if="items.length" class="space-y-1">

        <li v-for="item in items" :key="item.id"
          class="flex flex-wrap justify-between items-center bg-white p-2 rounded-md shadow-sm text-sm border border-gray-100">

          <div class="flex flex-col sm:flex-row sm:items-center justify-between w-full">

            <span class="text-gray-800 font-bold">
              <span class="text-green-600">CARGA</span>:
              {{ getLabelById(item.dispositivo_id) }}
            </span>

            <div class="flex items-center gap-2 mt-1 sm:mt-0">

              <!-- MOSTRAR FECHA Y HORA SEPARADAS SIN CONVERTIR -->
              <span class="text-xs text-gray-500 font-semibold">
                {{ item.fecha }} {{ item.hora }}
              </span>

              <button @click="$emit('edit', item)"
                class="p-1 text-blue-600 hover:text-blue-800 rounded-full hover:bg-blue-50"
                title="Editar Carga">
                <SvgIcon name="pencil" class="w-4 h-4" />
              </button>

              <button @click="$emit('delete', item.id)"
                class="p-1 text-red-600 hover:text-red-800 rounded-full hover:bg-red-50"
                title="Eliminar Carga">
                <SvgIcon name="trash" class="w-4 h-4" />
              </button>

            </div>
          </div>

          <div class="flex justify-between items-center w-full mt-1">
            <span class="text-xs text-gray-500">
              Litros cargados: <b>{{ item.litros_total }} L</b>
            </span>

            <span class="bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-bold text-xs">
              Carga
            </span>
          </div>

        </li>

      </ul>

      <p v-else class="text-sm text-gray-500 italic p-2 text-center">
        Aún no hay cargas registradas.
      </p>

    </div>

  </div>
</template>

<script setup>
import { ref } from "vue";
import SvgIcon from "@/components/icons/SvgIcon.vue";

defineProps({
  items: Array,
  dispositivos: Array,
  getLabel: Function,
  getLabelById: Function,
});

const emit = defineEmits(["add", "edit", "delete"]);

const today = new Date().toISOString().slice(0, 10);
const now = new Date();
const currentTime = now.toTimeString().slice(0, 5);

const form = ref({
  fecha: today,
  hora: currentTime,
  dispositivo_id: "",
  litros_total: null,
});

const onAdd = () => {
  emit("add", {
    fecha: form.value.fecha,
    hora: form.value.hora,
    dispositivo_id: form.value.dispositivo_id,
    litros_total: form.value.litros_total,
  });

  form.value = {
    fecha: today,
    hora: currentTime,
    dispositivo_id: "",
    litros_total: null,
  };
};
</script>
