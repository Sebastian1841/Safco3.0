# SAFCO – Frontend (Vue 3)

Aplicacion SPA para visualizar registros de combustible: tabla con filtros y un dashboard con grafico de barras.

## Arranque rapido

- Con Docker (recomendado)
  1. Desde la raiz del repo: `docker compose up --build`
  2. Frontend queda en: http://localhost:5173
  3. Backend debe estar en: http://localhost:5000 (se define con `VUE_APP_BACKEND_URL` en docker-compose)

- Local (Node 20+)
  1. `cd frontend`
  2. `npm install`
  3. `VUE_APP_BACKEND_URL=http://localhost:5000 npm run serve`
  4. Abre la URL que muestra (por defecto http://localhost:5173)

## Scripts

- `npm run serve`  – servidor de desarrollo
- `npm run build`  – build de produccion
- `npm run lint`   – ESLint

## Estructura relevante

- `src/Views/SafcoDashboard.vue` – vista del dashboard con los mismos filtros que la tabla
- `src/components/Tables/DataTables.vue` – tabla con filtros, busqueda y paginacion
- `src/components/DashboardUi/BarsChart.vue` – grafico de barras del dashboard
- `src/utils/useDataFilters.js` – composable que centraliza la logica de filtros

## Filtros (fuente unica: useDataFilters)

- Estados: `selectedDevices`, `fechaInicio`, `fechaFin`, `selectedRange`.
- Rango rapido: `last_hour`, `last_12_hours`, `last_week`, `last_month`, `last_6_months`, `all`.
- Rango manual: al escribir fechas se limpia `selectedRange` y se usan `fechaInicio/fechaFin` (formato YYYY-MM-DD, hora local).
- Watchers: reinician paginacion y disparan la recarga de datos cuando cambian los filtros.

## Grafico de barras (BarsChart.vue)

- Props: `fechaInicio`, `fechaFin`, `selectedDevices`, `selectedRange`.
- Llamada a backend: envia `fecha_inicio` y `fecha_fin` solo si ambas existen.
- Filtros en frontend:
  - Por `selectedDevices`.
  - Ventanas rapidas: `last_hour` y `last_12_hours` por timestamp real.
- Agregacion mostrada: litros por hora (0..23) con etiquetas `HH:00`.
- Estabilidad Chart.js: siempre destruye la instancia previa antes de crear una nueva y al desmontar el componente.

## Variables de entorno

- `VUE_APP_BACKEND_URL` – URL base del backend (en compose apunta a `http://localhost:5000`).

## Estilos

- Tailwind CSS incluido en la configuracion (ver `package.json` y plugin de Tailwind para Vue CLI).

## Solucion de problemas

- Canvas en uso: error de Chart.js. La implementacion destruye la instancia anterior; si haces refactors, conserva ese patron.
- Errores ESLint tipo "no-multiple-template-root" o "Cannot redeclare": suelen indicar archivos con bloques duplicados. Deja siempre un unico `<template>`, `<script>` y `<style>` por componente.
- Fechas desfasadas: se usan fechas locales `YYYY-MM-DD`. Si necesitas UTC puro para los dias, ajusta el formato y la conversion en el backend o en el grafico.
- Puertos por defecto: Frontend 5173, Backend 5000.

## Notas

- El dashboard y la tabla comparten los mismos filtros via `useDataFilters`. Si cambias los nombres de props o la semantica, mantelos sincronizados.

