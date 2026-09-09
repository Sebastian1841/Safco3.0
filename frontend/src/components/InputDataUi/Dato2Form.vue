<template>
  <div class="bg-white p-4 sm:p-6 rounded-lg shadow-xl border border-gray-200">

    <h2 class="text-xl font-semibold text-blue-700 mb-4 flex items-center gap-2">
      Añadir Referencia: ACC Negocio
    </h2>

    <form @submit.prevent="onAdd" class="flex flex-col sm:flex-row gap-4 mb-4">
      <input
        type="text"
        v-model="nombre"
        required
        class="flex-1 border border-gray-300 rounded-md p-2 text-sm focus:ring-blue-500 focus:border-blue-500"
        placeholder="Ingrese ACC del negocio"
      />
      <button
        type="submit"
        class="sm:w-auto px-4 py-2 bg-[#4f46e5] text-white font-medium rounded-md hover:bg-indigo-700 transition shadow-md text-sm"
      >
        Agregar
      </button>
    </form>

    <h3 class="text-sm font-bold text-gray-700 mt-6 mb-2 border-t pt-4">
      Datos Agregados ({{ items.length }})
    </h3>

    <div class="max-h-40 overflow-y-auto border border-gray-100 rounded-md p-2 bg-gray-50">
      <ul v-if="items.length" class="space-y-1">
        <li
          v-for="item in items"
          :key="item.id"
          class="flex justify-between items-center bg-white p-2 rounded-md shadow-sm text-sm border border-gray-100"
        >
          <span class="text-gray-800 font-medium">{{ item.nombre }}</span>

          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-500 font-mono hidden sm:inline">
              ID: {{ item.id }}
            </span>

            <button
              @click="$emit('edit', item)"
              class="p-1 text-blue-600 hover:text-blue-800 transition rounded-full hover:bg-blue-50"
              title="Editar"
            >
              <SvgIcon name="pencil" class="w-4 h-4" />
            </button>

            <button
              @click="$emit('delete', item.id)"
              class="p-1 text-red-600 hover:text-red-800 transition rounded-full hover:bg-red-50"
              title="Eliminar"
            >
              <SvgIcon name="trash" class="w-4 h-4" />
            </button>
          </div>
        </li>
      </ul>

      <p v-else class="text-sm text-gray-500 italic p-2 text-center">
        Aún no se han agregado referencias.
      </p>
    </div>

  </div>
</template>

<script setup>
import { ref } from "vue";
import SvgIcon from "@/components/icons/SvgIcon.vue";

// Declaración sin guardar en variable (evita el warning)
defineProps({
  items: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(["add", "edit", "delete"]);

const nombre = ref("");

const onAdd = () => {
  if (nombre.value.trim()) {
    emit("add", nombre.value.trim());
    nombre.value = "";
  }
};
</script>
