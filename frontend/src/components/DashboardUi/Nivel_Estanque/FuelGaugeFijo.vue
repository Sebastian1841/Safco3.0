<template>
  <div class="flex flex-col items-center">
    <svg width="360" height="300" viewBox="0 0 360 300" preserveAspectRatio="xMidYMid meet">
      <defs>

        <!-- Clip centrado y ajustado -->
        <clipPath id="fixedTankClip">
          <rect x="80" y="50" width="200" height="200" rx="18" ry="18" />
        </clipPath>

        <linearGradient id="fixedFuelGrad" x1="0%" y1="100%" x2="0%" y2="0%">
          <stop offset="0%" stop-color="#0f172a" /> <!-- azul noche -->
          <stop offset="50%" stop-color="#1e3a8a" /> <!-- azul petróleo -->
          <stop offset="100%" stop-color="#3b82f6" /> <!-- azul diésel -->
        </linearGradient>


      </defs>

      <!-- TAPA centrada -->
      <rect x="230" y="20" width="40" height="30" rx="6" ry="6" fill="white" stroke="#6b7280" stroke-width="2" />

      <!-- CUERPO centrado (200 px de alto) -->
      <rect x="80" y="50" width="200" height="200" rx="18" ry="18" fill="white" stroke="#6b7280" stroke-width="3" />

      <!-- Líquido -->
      <g clip-path="url(#fixedTankClip)">
        <path :d="wave1" fill="url(#fixedFuelGrad)" opacity="0.9">
          <animate attributeName="d" dur="4s" repeatCount="indefinite" :values="waveAnim1" />
        </path>

        <path :d="wave2" fill="url(#fixedFuelGrad)" opacity="0.6">
          <animate attributeName="d" dur="6s" repeatCount="indefinite" :values="waveAnim2" />
        </path>
      </g>

      <!-- Porcentaje centrado REAL -->
      <text x="180" y="160" text-anchor="middle" font-size="50" font-weight="700" fill="#ffffff" stroke="#000000"
        stroke-width="2" paint-order="stroke">
        {{ Math.round(pct * 100) }}%
      </text>

    </svg>
    <p class="mt-3 text-center font-semibold">
      <span class="text-2xl text-slate-900 tracking-tight">
        {{ safeLitros.toLocaleString('es-CL') }}
      </span>
      <span class="ml-1 text-sm text-emerald-600 font-bold uppercase">
        Litros
      </span>
    </p>

  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  litros: Number,
  max: Number,
})

const safeLitros = computed(() => Number(props.litros) || 0)

const pct = computed(() => {
  const m = Number(props.max) || 1
  return Math.min(Math.max(safeLitros.value / m, 0), 1)
})


const top = 60          // nivel superior del agua
const bottom = 250      // base exacta según nueva altura

const baseY = computed(() => bottom - pct.value * (bottom - top))

/* Ondas centradas en 80→280 con nueva altura */
const wave1 = computed(() => {
  const y = baseY.value
  return `M80 ${y} Q180 ${y - 18},280 ${y} L280 300 L80 300 Z`
})

const wave2 = computed(() => {
  const y = baseY.value + 12
  return `M80 ${y} Q180 ${y - 10},280 ${y} L280 300 L80 300 Z`
})

/* Animación actualizada */
const waveAnim1 = computed(() => `
  M80 ${baseY.value} Q180 ${baseY.value - 18},280 ${baseY.value} L280 300 L80 300 Z;
  M80 ${baseY.value} Q180 ${baseY.value + 12},280 ${baseY.value - 8} L280 300 L80 300 Z;
  M80 ${baseY.value} Q180 ${baseY.value - 18},280 ${baseY.value} L280 300 L80 300 Z
`)

const waveAnim2 = computed(() => `
  M80 ${baseY.value + 12} Q180 ${baseY.value + 4},280 ${baseY.value + 12} L280 300 L80 300 Z;
  M80 ${baseY.value + 12} Q180 ${baseY.value + 20},280 ${baseY.value} L280 300 L80 300 Z;
  M80 ${baseY.value + 12} Q180 ${baseY.value + 4},280 ${baseY.value + 12} L280 300 L80 300 Z
`)
</script>
