<template>
  <article class="fuel-report-sheet" aria-label="Informe de combustible">
    <header class="fuel-report-brand">
      <img :src="sinergyLogo" class="fuel-report-logo" alt="Sinergy Group" width="2800" height="900" />
      <p>Monitoreo GPS y Telemetría IoT</p>
    </header>
    <div class="fuel-report-title">
      <h1>INFORME DE COMBUSTIBLE</h1>
      <p>SAFCO · {{ report.device.nombre }} | {{ reportDate(report.start) }} a {{ reportDate(report.end) }}</p>
    </div>

    <section>
      <h2>Datos generales</h2>
      <table class="fuel-report-general">
        <tbody>
          <tr><th scope="row">Reporte</th><td>Movimientos de combustible registrados</td></tr>
          <tr><th scope="row">Estanque</th><td>{{ report.device.nombre }}</td></tr>
          <tr><th scope="row">Rango consultado</th><td>{{ reportDate(report.start) }} a {{ reportDate(report.end) }} (ambos días incluidos)</td></tr>
          <tr><th scope="row">Registros</th><td>{{ report.rows.length }}</td></tr>
          <tr><th scope="row">Generado</th><td>{{ reportTimestamp(report.generatedAt) }}, {{ reportTimestamp(report.generatedAt, true) }}</td></tr>
        </tbody>
      </table>
    </section>

    <section>
      <h2>Resumen del período</h2>
      <div class="fuel-report-summary">
        <div><strong>{{ reportNumber(report.totalLiters) }} L</strong><span>Litros registrados</span></div>
        <div><strong>{{ reportNumber(report.rows.length) }}</strong><span>Registros</span></div>
        <div><strong>{{ reportNumber(report.averageLiters) }} L</strong><span>Promedio por registro</span></div>
        <div><strong>{{ reportNumber(report.equipmentCount) }}</strong><span>Equipos identificados</span></div>
      </div>
    </section>

    <section>
      <h2>Estanque incluido</h2>
      <table>
        <thead><tr><th scope="col">Estanque</th><th scope="col">ID</th><th scope="col">Registros</th><th scope="col">Litros registrados</th><th scope="col">iButton distintos</th></tr></thead>
        <tbody><tr><td>{{ report.device.nombre }}</td><td>{{ report.device.id }}</td><td>{{ report.rows.length }}</td><td>{{ reportNumber(report.totalLiters) }} L</td><td>{{ report.ibuttonCount }}</td></tr></tbody>
      </table>
    </section>

    <section>
      <h2>Detalle de combustible</h2>
      <table class="fuel-report-detail">
        <colgroup><col style="width: 4%" /><col style="width: 12%" /><col style="width: 10%" /><col style="width: 10%" /><col style="width: 18%" /><col style="width: 18%" /><col style="width: 14%" /><col style="width: 14%" /></colgroup>
        <thead><tr><th scope="col">#</th><th scope="col">Fecha</th><th scope="col">Hora</th><th scope="col">Litros</th><th scope="col">iButton ID</th><th scope="col">Apodo iButton</th><th scope="col">COD Equipo</th><th scope="col">ACC Negocio</th></tr></thead>
        <tbody>
          <tr v-for="(row, index) in report.rows" :key="row.id ?? `${row.fecha}-${index}`">
            <td>{{ index + 1 }}</td><td>{{ reportTimestamp(row.fecha) }}</td><td>{{ reportTimestamp(row.fecha, true) }}</td>
            <td class="fuel-report-numeric">{{ reportNumber(row.litros) }}</td><td>{{ row.ibutton || 'Sin iButton' }}</td><td>{{ row.ibutton_alias }}</td>
            <td>{{ row.dato1_nombre || 'Sin asignar' }}</td><td>{{ row.dato2_nombre || 'Sin asignar' }}</td>
          </tr>
          <tr v-if="!report.rows.length"><td colspan="8" class="fuel-report-empty">No hay registros para el estanque y las fechas seleccionadas.</td></tr>
        </tbody>
      </table>
      <p class="fuel-report-total">Total del período: <strong>{{ reportNumber(report.totalLiters) }} L</strong></p>
    </section>
    <footer class="fuel-report-footer">
      <p>Fechas y horas de los movimientos: America/Santiago.</p>
      <p>El informe presenta los registros disponibles al momento de generarlo. Los litros registrados no representan el saldo disponible del estanque.</p>
    </footer>
  </article>
</template>

<script setup>
import { reportDate, reportTimestamp, reportNumber } from '@/utils/fuelReport';
import sinergyLogo from '@/assets/sinergy-group.png';
defineProps({ report: { type: Object, required: true } });
</script>

<style>
.fuel-report-sheet { box-sizing: border-box; max-width: 210mm; margin: 0 auto; padding: 12mm 14mm; background: white; color: #10236b; font-family: Arial, sans-serif; font-size: 11px; line-height: 1.5; }
.fuel-report-sheet * { box-sizing: border-box; }
.fuel-report-brand { text-align: center; border-bottom: 2px solid #ff6b00; padding-bottom: 15px; }
.fuel-report-logo { display: block; width: 270px; max-width: 85%; height: auto; margin: 0 auto 12px; }
.fuel-report-brand p { margin: 4px 0 0; color: #4664a3; font-size: 9px; font-style: italic; }
.fuel-report-title { text-align: center; padding: 16px 0 4px; }
.fuel-report-title h1 { font-size: 19px; font-weight: 700; margin: 0 0 5px; }
.fuel-report-title p { margin: 0; }
.fuel-report-sheet section { margin-top: 25px; }
.fuel-report-sheet h2 { margin: 0 0 12px; padding-bottom: 6px; border-bottom: 2px solid #ff6b00; font-size: 13px; font-weight: 700; break-after: avoid; }
.fuel-report-sheet table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 10px; }
.fuel-report-sheet th, .fuel-report-sheet td { border: 1px solid #d8dfed; padding: 8px 7px; text-align: left; overflow-wrap: anywhere; }
.fuel-report-sheet thead th { background: #122471; color: white; font-weight: 700; text-align: center; }
.fuel-report-sheet tbody tr:nth-child(odd) { background: #f5f8fc; }
.fuel-report-general th { width: 25%; font-weight: 700; }
.fuel-report-summary { display: grid; grid-template-columns: repeat(4, 1fr); border: 1px solid #d8dfed; }
.fuel-report-summary div { padding: 15px 5px; border: 1px solid #d8dfed; text-align: center; }
.fuel-report-summary div:nth-child(even) { background: #f5f8fc; }
.fuel-report-summary strong { display: block; font-size: 19px; margin-bottom: 9px; overflow-wrap: anywhere; }
.fuel-report-summary span { font-size: 10px; font-weight: 700; }
.fuel-report-summary div:nth-child(2) strong { color: #008c87; }
.fuel-report-summary div:nth-child(3) strong { color: #ec6200; }
.fuel-report-summary div:nth-child(4) strong { color: #2563eb; }
.fuel-report-detail { font-size: 9px !important; }
.fuel-report-sheet .fuel-report-numeric { text-align: right; }
.fuel-report-sheet .fuel-report-empty { text-align: center; padding: 22px; }
.fuel-report-total { text-align: right; margin: 10px 0; }
.fuel-report-footer { margin-top: 24px; border-top: 1px solid #d8dfed; padding-top: 10px; font-size: 9px; color: #52617a; }
@media screen and (max-width: 600px) {
  .fuel-report-sheet { padding: 18px 10px; }
  .fuel-report-summary { grid-template-columns: repeat(2, 1fr); }
  .fuel-report-sheet th, .fuel-report-sheet td { padding: 6px 3px; }
}
</style>
