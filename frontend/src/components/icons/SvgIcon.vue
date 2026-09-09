<template>
    <!-- Eye -->
    <svg v-if="name === 'eye'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24"
        stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5s8.268 2.943 9.542 7
         c-1.274 4.057-5.065 7-9.542 7s-8.268-2.943-9.542-7z" />
    </svg>

    <!-- Eye Off -->
    <svg v-else-if="name === 'eye-off'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19
         c-4.477 0-8.268-2.943-9.542-7
         a9.974 9.974 0 012.469-4.247M9.88 9.88
         a3 3 0 104.24 4.24" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M3 3l18 18" />
    </svg>

    <!-- Lock -->
    <svg v-else-if="name === 'lock'" xmlns="http://www.w3.org/2000/svg" class="w-20 h-20" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round"
            d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
    </svg>

    <!-- Check -->
    <svg v-else-if="name === 'check'" xmlns="http://www.w3.org/2000/svg" class="w-16 h-16" fill="none"
        viewBox="0 0 24 24" stroke="c   urrentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
    </svg>

    <!-- Mail -->
    <svg v-else-if="name === 'mail'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24"
        stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14
         a2 2 0 002-2V7a2 2 0 00-2-2H5
         a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>

    <!-- Trash / Eliminar -->
    <svg v-else-if="name === 'trash'" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24"
        stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 
       2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 
       0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>

    <!-- Pencil / Editar -->
    <svg v-else-if="name === 'pencil'" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 
       0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
    </svg>

    <!-- Copy / Copiar -->
    <svg v-else-if="name === 'copy'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
        stroke-width="1.5" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round"
            d="M8 16H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v2" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M8 8h8v8a2 2 0 0 1-2 2H8V8z" />
    </svg>

    <!-- Arrow Left / Retroceder -->
    <svg v-else-if="name === 'arrow-left'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
        stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
    </svg>

    <!-- Chevron Left / Paginación anterior -->
    <svg v-else-if="name === 'chevron-left'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd"
            d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
            clip-rule="evenodd" />
    </svg>

    <!-- Chevron Right / Paginación siguiente -->
    <svg v-else-if="name === 'chevron-right'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"
        fill="currentColor">
        <path fill-rule="evenodd"
            d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
            clip-rule="evenodd" />
    </svg>

    <!-- Logout / Cerrar sesión -->
    <svg v-else-if="name === 'logout'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
        stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
    </svg>

    <!-- Close -->
    <svg v-else-if="name === 'close'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
        stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>

    <!-- Plus / Agregar -->
    <svg v-else-if="name === 'plus'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
        stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
    </svg>

    <!-- Search / Lupa -->
    <svg v-else-if="name === 'search'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
        stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round"
            d="M21 21l-4.35-4.35m1.85-5.4a7.25 7.25 0 11-14.5 0 7.25 7.25 0 0114.5 0z" />
    </svg>

    <!-- OK / Mantención OK -->
    <svg v-else-if="name === 'ok'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
        stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round"
            d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>

    <!-- Proxima Mantención -->
    <svg v-else-if="name === 'proxima'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
        stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round"
            d="M12 9v3.75m0 3.75h.01M3.6 18h16.8c1.2 0 2-1.3 1.4-2.4L13.4 3.4a1.5 1.5 0 00-2.8 0L2.2 15.6C1.6 16.7 2.4 18 3.6 18z" />
    </svg>

    <!-- Mantención Vencida / Requiere Mantención -->
    <svg v-else-if="name === 'vencida'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
        stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round"
            d="M12 9v4m0 4h.01M12 2.25a9.75 9.75 0 100 19.5 9.75 9.75 0 000-19.5z" />
    </svg>

    <!-- Dashboard -->
    <svg v-else-if="name === 'dashboard'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round"
            d="M3 11.5L12 3l9 8.5v9a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 20.5v-9z" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 21V13h6v8" />
    </svg>

    <!-- Dispositivos -->
    <svg v-else-if="name === 'dispositivos'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <rect x="3" y="4" width="18" height="14" rx="2" ry="2" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M8 20h8M12 16v4" />
    </svg>

    <!-- Empresas -->
    <svg v-else-if="name === 'empresas'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round"
            d="M3 21V7a2 2 0 012-2h4a2 2 0 012 2v14H3zM15 21V11a2 2 0 012-2h4a2 2 0 012 2v10h-6z" />
    </svg>

    <!-- Alertas -->
    <svg v-else-if="name === 'alertas'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <polyline points="22 12 16 12 14 15 10 15 8 12 2 12"></polyline>
        <path
            d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z">
        </path>
    </svg>

    <!-- Motor de Reglas -->
    <svg v-else-if="name === 'motor'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24"
        stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M8 6v12l4-4 4 4V6" />
    </svg>

    <!-- Fuentes de Datos -->
    <svg v-else-if="name === 'fuentes'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <ellipse cx="12" cy="5" rx="8" ry="3" stroke-linecap="round" stroke-linejoin="round" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M4 5v14c0 1.657 3.582 3 8 3s8-1.343 8-3V5" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M4 12c0 1.657 3.582 3 8 3s8-1.343 8-3" />
    </svg>


    <!-- Usuarios -->
    <svg v-else-if="name === 'usuarios'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="8" r="4" stroke-linecap="round" stroke-linejoin="round" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M6 20c0-3.314 2.686-6 6-6s6 2.686 6 6" />
    </svg>


    <!-- Reportes / Informes -->
    <svg v-else-if="name === 'reportes'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round"
            d="M6 2h12a2 2 0 012 2v16a2 2 0 01-2 2H6a2 2 0 01-2-2V4a2 2 0 012-2z" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M14 2v6h6" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h8M8 16h8M8 20h4" />
    </svg>


    <!-- Mantenciones -->
    <svg v-else-if="name === 'mantenciones'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" />
    </svg>

    <!-- Configuración -->
    <svg v-else-if="name === 'configuracion'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="3" stroke-linecap="round" stroke-linejoin="round" />
        <path stroke-linecap="round" stroke-linejoin="round"
            d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09a1.65 1.65 0 00-1-1.51 1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09a1.65 1.65 0 001.51-1 1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" />
    </svg>
    <!-- Telefono -->
    <svg v-else-if="name === 'telefono'" xmlns="http://www.w3.org/2000/svg" class="w-10 h-10" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round"
            d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
    </svg>
    <!-- Tables -->
    <svg v-else-if="name === 'tables'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M3 3h18v4H3V3zm0 6h18v4H3V9zm0 6h18v4H3v-4z" />
    </svg>
    <!-- Ingresar -->
    <svg v-else-if="name === 'ingresar'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
    </svg>
    <!-- Chevron Down -->
    <svg v-else-if="name === 'chevron-down'" xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 sm:w-4 sm:h-4"
        fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
    </svg>
    <!-- Calendar Range -->
    <svg v-else-if="name === 'calendar-range'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round"
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
    <!-- Dashboard -->
    <svg v-else-if="name === 'dashboard-pro'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
        <path stroke-linecap="round" stroke-linejoin="round"
            d="M3 13h7V3H3v10zM3 21h7v-6H3v6zM14 21h7V11h-7v10zM14 3v6h7V3h-7z" />
    </svg>
    <!-- Reportes Pro -->
    <svg v-else-if="name === 'reportes-pro'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
        <path stroke-linecap="round" stroke-linejoin="round" d="M3 3h18v18H3z" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M3 9h18M9 3v18" />
    </svg>
    <!-- Facturas Pro -->
    <svg v-else-if="name === 'facturas-pro'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
        <path stroke-linecap="round" stroke-linejoin="round" d="M7 3h10l4 4v14H3V3z" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M14 3v5h5" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h8M8 16h5" />
    </svg>
    <!-- Descarga (sensor) -->
    <svg v-else-if="name === 'descarga-sensor'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v14m0 0l-4-4m4 4l4-4M4 21h16" />
    </svg>
    <!-- Carga Manual -->
    <svg v-else-if="name === 'carga-manual'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 21V7m0 0l-4 4m4-4l4 4M4 3h16" />
    </svg>
    <!-- Carga Factura -->
    <svg v-else-if="name === 'carga-factura'" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4 4h16v16H4z" />
    </svg>

</template>

<script>
export default {
    name: 'SvgIcon',
    props: {
        name: {
            type: String,
            required: true
        }
    }
}
</script>
