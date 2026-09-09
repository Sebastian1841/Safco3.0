<template>
  <div
    class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50"
  >
    <div
      class="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6 relative animate-fadeIn"
    >
      <!-- BOTÓN CERRAR -->
      <button
        @click="$emit('close')"
        class="absolute right-4 top-4 text-gray-400 hover:text-gray-600 transition"
      >
        ✕
      </button>

      <!-- HEADER -->
      <h2 class="text-2xl font-bold text-gray-900 mb-4 text-center">
        Ingresar Factura COPEC
      </h2>

      <!-- ======== VISTA PREVIA DEL PDF ======== -->
      <div
        v-if="previewUrl"
        class="border rounded-lg overflow-hidden mb-4 shadow-sm"
      >
        <iframe :src="previewUrl" class="w-full h-64"></iframe>
      </div>

      <!-- INPUT ARCHIVO -->
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Seleccione un archivo PDF
      </label>

      <input
        type="file"
        accept="application/pdf"
        @change="onFileChange"
        class="border border-gray-300 bg-gray-50 hover:bg-white transition shadow-sm p-2 w-full rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      <!-- ERROR -->
      <p v-if="errorMsg" class="text-red-600 text-sm mt-2 font-semibold">
        {{ errorMsg }}
      </p>

      <!-- ====== MENSAJE DE ÉXITO ====== -->
      <div
        v-if="success"
        class="flex items-center gap-2 bg-green-50 border border-green-200 text-green-700 rounded-lg p-3 mt-4 animate-fadeIn"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="w-5 h-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="3"
            d="M5 13l4 4L19 7"
          />
        </svg>
        <span class="font-semibold">Factura cargada exitosamente.</span>
      </div>

      <!-- ====== PANTALLA DE CARGA ====== -->
      <div v-if="loading" class="mt-6 flex flex-col items-center">
        <div class="loader mb-3"></div>
        <p class="text-gray-600 text-sm">
          Subiendo factura, por favor espere...
        </p>
      </div>

      <!-- BOTÓN SUBIR -->
      <button
        v-if="!loading && !success"
        @click="subirFactura"
        :disabled="loading || !archivo"
        class="w-full mt-6 py-2.5 bg-blue-600 hover:bg-blue-700 
               text-white rounded-lg font-semibold transition shadow 
               disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Subir factura
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import axios from "axios"

const BACKEND_URL =
  process.env.VUE_APP_BACKEND_URL || "http://localhost:8081"

console.log("🔧 BACKEND_URL (FacturaUploadModal):", BACKEND_URL)

const emit = defineEmits(["close", "uploaded"])

const archivo = ref(null)
const previewUrl = ref(null)
const loading = ref(false)
const success = ref(false)
const errorMsg = ref("")

function onFileChange(e) {
  archivo.value = e.target.files[0]
  errorMsg.value = ""
  success.value = false

  if (archivo.value) {
    previewUrl.value = URL.createObjectURL(archivo.value)
  }
}

async function subirFactura() {
  if (!archivo.value) {
    errorMsg.value = "Debe seleccionar un archivo PDF."
    return
  }

  const form = new FormData()
  form.append("archivo", archivo.value)

  loading.value = true
  errorMsg.value = ""

  try {
    await axios.post(`${BACKEND_URL}/facturas/subir`, form, {
      headers: { "Content-Type": "multipart/form-data" }
    })

    success.value = true
    emit("uploaded")

    // Cerrar automáticamente tras 2 segundos
    setTimeout(() => emit("close"), 2000)
  } catch (err) {
    console.error(err)
    errorMsg.value =
      err.response?.data?.error ||
      "Error subiendo factura. Intente nuevamente."
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Animación suave */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.97);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.18s ease-out;
}

/* Loader */
.loader {
  width: 34px;
  height: 34px;
  border: 4px solid #d1d5db;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
