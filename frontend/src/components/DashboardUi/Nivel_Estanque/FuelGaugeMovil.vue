<template>
    <div class="loader">
        <div class="truckWrapper">

            <!-- ======================= -->
            <!--      CUERPO CAMIÓN      -->
            <!-- ======================= -->
            <div class="truckBody">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 150" class="trucksvg">

                    <defs>
                        <!-- Clip del tanque -->
                        <clipPath id="tankClip">
                            <rect x="20" y="35" width="180" height="85" rx="15" ry="15" />
                        </clipPath>

                        <!-- Degradado combustible -->
                        <linearGradient id="fuelGrad" x1="0%" y1="100%" x2="0%" y2="0%">
                            <stop offset="0%" stop-color="#0f172a" /> <!-- azul noche -->
                            <stop offset="50%" stop-color="#1e3a8a" /> <!-- azul petróleo -->
                            <stop offset="100%" stop-color="#3b82f6" /> <!-- azul diésel -->
                        </linearGradient>

                    </defs>

                    <!-- Contorno tanque -->
                    <rect x="20" y="35" width="180" height="85" rx="15" ry="15" fill="white" stroke="#6b7280"
                        stroke-width="4" />

                    <!-- Olas animadas -->
                    <g clip-path="url(#tankClip)">
                        <path :d="wave1" fill="url(#fuelGrad)" opacity="0.9">
                            <animate attributeName="d" dur="4s" repeatCount="indefinite" :values="waveAnim1" />
                        </path>

                        <path :d="wave2" fill="url(#fuelGrad)" opacity="0.6">
                            <animate attributeName="d" dur="6s" repeatCount="indefinite" :values="waveAnim2" />
                        </path>
                    </g>

                    <!-- Porcentaje CENTRADO -->
                    <text x="110" y="84" text-anchor="middle" font-size="30" font-weight="700" fill="#ffffff"
                        stroke="#000000" stroke-width="2" paint-order="stroke" style="pointer-events:none;">
                        {{ Math.round(pct * 100) }}%
                    </text>


                    <!-- Cabina -->
                    <path stroke="#282828" stroke-width="4" fill="#F83D3D"
                        d="M215 40H270c1.5 0 3 .9 3.5 2L290 93c.5 1 .7 2 .7 3.3V130c0 2-1.7 3.5-3.5 3.5H215c-2 0-3.5-1.5-3.5-3.5V45c0-2.5 2-5 3.5-5Z" />

                    <path stroke="#282828" stroke-width="4" fill="#7D7C7C"
                        d="M230 55H268c1.5 0 2.8.9 3.3 2l10 28c1 2.5-.5 5-3 5H230c-2 0-3.5-1.5-3.5-3.5v-28c0-2 1.5-3.5 3.5-3.5Z" />

                </svg>
            </div>

            <!-- RUEDAS -->
            <div class="truckTires">
                <svg viewBox="0 0 40 40" class="wheel">
                    <circle stroke-width="4" stroke="#282828" fill="#282828" r="17" cy="20" cx="20" />
                    <circle fill="#DFDFDF" r="9" cy="20" cx="20" />
                </svg>

                <svg viewBox="0 0 40 40" class="wheel" style="transform: translateX(-30px)">
                    <circle stroke-width="4" stroke="#282828" fill="#282828" r="17" cy="20" cx="20" />
                    <circle fill="#DFDFDF" r="9" cy="20" cx="20" />
                </svg>
            </div>

            <div class="road"></div>

        </div>
        <p class="mt-10 text-center font-semibold">
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
import { computed } from "vue";

const props = defineProps({
    litros: Number,
    max: Number
});

const safeLitros = computed(() => Number(props.litros) || 0);

const pct = computed(() => {
    const m = Number(props.max) || 1;
    return Math.min(Math.max(safeLitros.value / m, 0), 1);
});

// Rango exacto del tanque
const tankTop = 35;
const tankBottom = 120;

const baseY = computed(() => tankBottom - pct.value * (tankBottom - tankTop));

const wave1 = computed(() => {
    const y = baseY.value;
    return `M20 ${y} Q110 ${y - 10},200 ${y} L200 155 L20 155 Z`;
});

const wave2 = computed(() => {
    const y = baseY.value + 8;
    return `M20 ${y} Q110 ${y - 5},200 ${y} L200 155 L20 155 Z`;
});

const waveAnim1 = computed(() => `
  M20 ${baseY.value} Q110 ${baseY.value - 10},200 ${baseY.value} L200 155 L20 155 Z;
  M20 ${baseY.value} Q110 ${baseY.value + 10},200 ${baseY.value - 6} L200 155 L20 155 Z;
  M20 ${baseY.value} Q110 ${baseY.value - 10},200 ${baseY.value} L200 155 L20 155 Z
`);

const waveAnim2 = computed(() => `
  M20 ${baseY.value + 8} Q110 ${baseY.value + 2},200 ${baseY.value + 8} L200 155 L20 155 Z;
  M20 ${baseY.value + 8} Q110 ${baseY.value + 14},200 ${baseY.value} L200 155 L20 155 Z;
  M20 ${baseY.value + 8} Q110 ${baseY.value + 2},200 ${baseY.value + 8} L200 155 L20 155 Z
`);
</script>

<style>
.loader {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.truckWrapper {
    width: 320px;
    height: 150px;
    display: flex;
    flex-direction: column;
    position: relative;
    justify-content: flex-end;
    overflow: hidden;
}

.truckBody {
    width: 280px;
    animation: motion 1s linear infinite;
}

@keyframes motion {
    0% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(3px);
    }

    100% {
        transform: translateY(0);
    }
}

.truckTires {
    width: 230px;
    display: flex;
    justify-content: space-between;
    position: absolute;
    bottom: -4px;
    left: 45px;
}

.wheel {
    width: 40px;
    height: 40px;
}

.road {
    width: 100%;
    height: 2px;
    background-color: #282828;
    border-radius: 3px;
    position: relative;
}

.road::before,
.road::after {
    content: "";
    position: absolute;
    height: 100%;
    background-color: #282828;
    animation: roadAnimation 1.4s linear infinite;
}

.road::before {
    width: 30px;
    right: -40%;
    border-left: 12px solid white;
}

.road::after {
    width: 15px;
    right: -55%;
    border-left: 6px solid white;
}

@keyframes roadAnimation {
    0% {
        transform: translateX(0);
    }

    100% {
        transform: translateX(-350px);
    }
}
</style>
