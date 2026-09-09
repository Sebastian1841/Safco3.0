<template>
    <div class="bg-white p-4 sm:p-6 rounded-lg shadow-xl border border-gray-200">

        <h2 class="text-xl font-semibold text-blue-700 mb-4 flex items-center gap-2">
            Registro Manual Totalizador de Combustible
        </h2>

        <!-- FORMULARIO -->
        <form @submit.prevent="onAdd" class="flex flex-col gap-4 mb-6">

            <!-- Fecha y Dispositivo -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-medium text-gray-700 mb-1">Fecha de Control</label>
                    <input type="date" v-model="form.fecha" required
                        class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-blue-500 focus:border-blue-500" />
                </div>

                <div>
                    <label class="block text-xs font-medium text-gray-700 mb-1">Dispositivo/Vehículo</label>
                    <select v-model="form.dispositivo" required
                        class="w-full border border-gray-300 rounded-md p-2 text-sm bg-white focus:ring-blue-500 focus:border-blue-500">
                        <option disabled value="">Seleccione un dispositivo</option>
                        <option v-for="d in dispositivos" :key="d.id" :value="d.id">
                            {{ getLabel(d) }}
                        </option>
                    </select>
                </div>
            </div>

            <!-- Litros inicio / final -->
            <div class="flex gap-4">
                <div class="flex-1">
                    <label class="block text-xs font-medium text-gray-700 mb-1">Litros Iniciales</label>
                    <input type="number" v-model.number="form.litros_inicio" required step="0.01" min="0"
                        class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                        placeholder="0.00" />
                </div>

                <div class="flex-1">
                    <label class="block text-xs font-medium text-gray-700 mb-1">Litros Finales</label>
                    <input type="number" v-model.number="form.litros_final" required step="0.01" min="0"
                        class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                        placeholder="0.00" />
                </div>
            </div>

            <div class="text-sm font-semibold p-2 rounded-md bg-red-100 text-red-800">
                ATENCIÓN: Para registrar el consumo, el valor Inicial debe ser menor o igual al valor Final.
            </div>

            <button type="submit"
                class="sm:w-full px-4 py-2 bg-indigo-600 text-white font-medium rounded-md hover:bg-indigo-700 shadow-md text-sm">
                Registrar Consumo Manual
            </button>
        </form>

        <!-- LISTA -->
        <h3 class="text-sm font-bold text-gray-700 mt-4 mb-2 border-t pt-4">
            Controles Registrados ({{ items.length }})
        </h3>

        <div class="max-h-60 overflow-y-auto border border-gray-100 rounded-md p-2 bg-gray-50">
            <ul v-if="items.length" class="space-y-1">

                <li v-for="item in items" :key="item.id"
                    class="flex flex-wrap justify-between items-center bg-white p-2 rounded-md shadow-sm text-sm border border-gray-100">
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between w-full">
                        <span class="text-gray-800 font-bold">
                            <span class="text-red-600">CONSUMO</span>:
                            {{ getLabelById(item.dispositivo) }}
                        </span>

                        <div class="flex items-center gap-2 mt-1 sm:mt-0">
                            <span class="text-xs text-gray-500 font-semibold">{{ item.fecha }}</span>

                            <button @click="$emit('edit', item)"
                                class="p-1 text-blue-600 hover:text-blue-800 rounded-full hover:bg-blue-50"
                                title="Editar Control">
                                <SvgIcon name="pencil" class="w-4 h-4" />
                            </button>

                            <button @click="$emit('delete', item.id)"
                                class="p-1 text-red-600 hover:text-red-800 rounded-full hover:bg-red-50"
                                title="Eliminar Control">
                                <SvgIcon name="trash" class="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    <div class="flex justify-between items-center w-full mt-1">
                        <span class="text-xs text-gray-500">
                            Inicio: <b>{{ item.litros_inicio }} L</b> | Fin: <b>{{ item.litros_final }} L</b>
                        </span>

                        <span
                            class="bg-red-100 text-red-700 px-2 py-0.5 rounded-full font-bold text-xs whitespace-nowrap">
                            Consumo: {{ Math.abs(item.diferencia_manual).toFixed(2) }} L
                        </span>
                    </div>
                </li>

            </ul>

            <p v-else class="text-sm text-gray-500 italic p-2 text-center">
                Aún no hay controles registrados.
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
    getLabelById: Function
});

const emit = defineEmits(["add", "edit", "delete"]);

const today = new Date().toISOString().slice(0, 10);

const form = ref({
    fecha: today,
    dispositivo: "",
    litros_inicio: null,
    litros_final: null
});

const onAdd = () => {
    if (form.value.litros_inicio > form.value.litros_final) {
        console.error("❌ Litros iniciales mayores que los finales");
        return;
    }

    emit("add", { ...form.value });

    form.value = {
        fecha: today,
        dispositivo: "",
        litros_inicio: null,
        litros_final: null
    };
};
</script>
