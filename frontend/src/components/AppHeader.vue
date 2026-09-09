<template>
  <header class="bg-[#1f2937] border-b border-gray-700 flex justify-between items-center px-4 py-2">
    <!-- Lado izquierdo: botón menú y logo principal -->
    <div class="flex items-center gap-4">
      <button class="md:hidden text-white text-2xl" @click="$emit('toggle-sidebar')">☰</button>
      <img
        alt="Logo Principal"
        src="https://www.gpsenchile.com/wp-content/uploads/2023/06/logowebblanco.png"
        class="h-12 w-auto"
      />
    </div>

    <!-- Lado derecho: logo empresa -->
    <div class="flex items-center">
      <img
        alt="Logo Empresa"
        src="@/components/imgs/logo2.png"
        class="h-12 w-auto"
      />
    </div>
  </header>
</template>

<script setup>
// No se necesita script
</script>
