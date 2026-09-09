<template>
  <Teleport to="body">
    <div id="fuel-report-modal" class="fuel-report-overlay" @click.self="close">
      <div ref="dialog" class="fuel-report-dialog" role="dialog" aria-modal="true" aria-labelledby="fuel-report-heading"
        tabindex="-1">
        <header class="fuel-report-modal-header fuel-report-controls">
          <div><h2 id="fuel-report-heading">Generar informe de combustible</h2><p>Selecciona el período y el estanque que quieres consultar.</p></div>
          <button type="button" class="fuel-report-close" aria-label="Cerrar informe" @click="close">×</button>
        </header>
        <form class="fuel-report-form fuel-report-controls" @submit.prevent="generate">
          <fieldset :disabled="loading || downloading" class="fuel-report-fields">
            <label>Fecha inicial<input ref="firstInput" v-model="start" type="date" required /></label>
            <label>Fecha final<input v-model="end" type="date" required /></label>
            <label>Estanque
              <select v-model="deviceId" aria-label="Estanque" required :disabled="devicesLoading">
                <option value="" disabled>{{ devicesLoading ? 'Cargando estanques…' : 'Selecciona un estanque' }}</option>
                <option v-for="device in devices" :key="device.id" :value="String(device.id)">{{ device.nombre }}</option>
              </select>
            </label>
          </fieldset>
          <div class="fuel-report-form-actions">
            <p>Genera la vista previa y elige descargarla en PDF o Excel.</p>
            <button type="submit" class="fuel-report-primary" :disabled="loading || downloading || devicesLoading || !devices.length">
              {{ loading ? 'Generando…' : 'Generar informe' }}
            </button>
          </div>
          <p v-if="error" class="fuel-report-error" role="alert">{{ error }}</p>
          <button v-if="devicesError" type="button" class="fuel-report-secondary" @click="loadDevices">Reintentar carga de estanques</button>
          <p v-if="loading || downloading" class="fuel-report-status" role="status">{{ progress }}</p>
          <p v-else-if="downloadMessage" class="fuel-report-status" role="status">{{ downloadMessage }}</p>
        </form>

        <div v-if="report" class="fuel-report-preview" :aria-busy="loading">
          <div class="fuel-report-preview-formats" role="group" aria-label="Formato de vista previa">
            <span>Vista previa</span>
            <button type="button" :class="previewFormat === 'pdf' ? 'fuel-report-primary' : 'fuel-report-secondary'" :aria-pressed="previewFormat === 'pdf'" @click="previewFormat = 'pdf'">PDF</button>
            <button type="button" :class="previewFormat === 'xlsx' ? 'fuel-report-primary' : 'fuel-report-secondary'" :aria-pressed="previewFormat === 'xlsx'" @click="previewFormat = 'xlsx'">Excel</button>
          </div>
          <FuelReportExcelDocument v-if="previewFormat === 'xlsx'" :report="report" />
          <FuelReportDocument v-else :report="report" />
        </div>
        <div v-else class="fuel-report-placeholder fuel-report-controls">
          <svg viewBox="0 0 48 48" fill="none" aria-hidden="true"><path d="M12 5h17l8 8v30H12zM29 5v9h8M18 23h13M18 29h13M18 35h9" stroke="currentColor" stroke-width="2" /></svg>
          <h3>Tu informe aparecerá aquí</h3>
          <p>Datos generales, resumen del período y detalle de combustible.</p>
        </div>
        <footer class="fuel-report-modal-footer fuel-report-controls">
          <span>{{ report ? 'Revisa el informe y elige el formato de descarga.' : 'PDF o Excel con todos los registros del período.' }}</span>
          <div><button type="button" class="fuel-report-secondary" @click="close">Cerrar</button>
            <button type="button" class="fuel-report-primary" :disabled="!report || loading || downloading" @click="saveReport('pdf')">{{ downloading === 'pdf' ? 'Descargando PDF…' : 'Descargar PDF' }}</button>
            <button type="button" class="fuel-report-primary" :disabled="!report || loading || downloading" @click="saveReport('xlsx')">{{ downloading === 'xlsx' ? 'Descargando Excel…' : 'Descargar Excel' }}</button></div>
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';
import axios from 'axios';
import FuelReportDocument from './FuelReportDocument.vue';
import FuelReportExcelDocument from './FuelReportExcelDocument.vue';
import sinergyLogo from '@/assets/sinergy-group.png';
import { reportToday, validateReportFilters, reportQueryRanges, createFuelReport } from '@/utils/fuelReport';

const props = defineProps({ initialStart: String, initialEnd: String, initialDeviceId: [Number, String] });
const emit = defineEmits(['close']);
const backendUrl = process.env.VUE_APP_BACKEND_URL || 'http://localhost:8081';
const today = reportToday();
const start = ref(props.initialStart || `${today.slice(0, 7)}-01`);
const end = ref(props.initialEnd || today);
const deviceId = ref(props.initialDeviceId ? String(props.initialDeviceId) : '');
const devices = ref([]);
const devicesLoading = ref(false);
const devicesError = ref(false);
const loading = ref(false);
const downloading = ref(false);
const downloadMessage = ref('');
const error = ref('');
const progress = ref('');
const report = ref(null);
const previewFormat = ref('pdf');
const dialog = ref(null);
const firstInput = ref(null);
const controller = new AbortController();
let previousFocus;
let previousOverflow;

watch([start, end, deviceId], () => { report.value = null; downloadMessage.value = ''; if (!devicesError.value) error.value = ''; });

async function loadDevices() {
  devicesLoading.value = true;
  devicesError.value = false;
  error.value = '';
  try {
    const response = await axios.get(`${backendUrl}/dispositivos`, { signal: controller.signal, timeout: 30000 });
    if (!Array.isArray(response.data) || !response.data.length) throw new Error('No hay estanques disponibles.');
    devices.value = response.data;
    if (!devices.value.some(device => String(device.id) === deviceId.value)) deviceId.value = '';
  } catch (err) {
    if (controller.signal.aborted) return;
    devicesError.value = true;
    error.value = 'No se pudieron cargar los estanques. Comprueba la conexión y vuelve a intentarlo.';
  } finally { devicesLoading.value = false; }
}

async function generate() {
  if (loading.value || downloading.value || devicesLoading.value) return;
  error.value = validateReportFilters(start.value, end.value, deviceId.value);
  if (error.value) return;
  const device = devices.value.find(item => String(item.id) === deviceId.value);
  if (!device) { error.value = 'Selecciona un estanque disponible.'; return; }
  loading.value = true;
  report.value = null;
  downloadMessage.value = '';
  try {
    const ranges = reportQueryRanges(start.value, end.value);
    const rows = [];
    for (let index = 0; index < ranges.length; index++) {
      progress.value = `Consultando período ${index + 1} de ${ranges.length}…`;
      const response = await axios.get(`${backendUrl}/datos`, {
        params: ranges[index], signal: controller.signal, timeout: 60000,
      });
      if (!Array.isArray(response.data)) throw new Error('El servidor no entregó una lista de registros válida.');
      for (const row of response.data) {
        if (Number(row.dispositivo_id) === Number(device.id)) rows.push(row);
      }
    }
    if (!controller.signal.aborted) {
      report.value = createFuelReport(rows, device, start.value, end.value);
    }
  } catch (err) {
    if (controller.signal.aborted) return;
    error.value = axios.isAxiosError(err)
      ? 'No se pudo obtener el informe completo. Comprueba la conexión y vuelve a intentarlo.'
      : err.message;
  } finally { loading.value = false; }
}

async function saveReport(format) {
  if (!report.value || loading.value || downloading.value || controller.signal.aborted) return;
  if (!['pdf', 'xlsx'].includes(format)) return;
  downloading.value = format;
  const label = format === 'xlsx' ? 'Excel' : 'PDF';
  error.value = '';
  downloadMessage.value = '';
  progress.value = `Preparando el archivo ${label}…`;
  const snapshot = report.value;
  try {
    const download = format === 'xlsx'
      ? (await import(/* webpackChunkName: "fuel-report-excel" */ '@/utils/fuelReportExcel')).downloadFuelReportExcel
      : (await import(/* webpackChunkName: "fuel-report-pdf" */ '@/utils/fuelReportPdf')).downloadFuelReport;
    if (controller.signal.aborted) return;
    if (await download(snapshot, sinergyLogo, controller.signal)) {
      downloadMessage.value = `Se inició la descarga del ${label}. Revisa las descargas de tu navegador.`;
    }
  } catch (err) {
    if (!controller.signal.aborted) error.value = `No se pudo descargar el ${label}. La vista previa sigue disponible; pulsa Descargar ${label} para reintentar.`;
  } finally { downloading.value = false; }
}

function close() { controller.abort(); emit('close'); }
function handleKeydown(event) {
  if (event.key === 'Escape') { event.preventDefault(); close(); return; }
  if (event.key !== 'Tab') return;
  const targets = [...dialog.value.querySelectorAll('button:not(:disabled), input:not(:disabled), select:not(:disabled), [tabindex="0"]')]
    .filter(element => !element.matches(':disabled') && element.getClientRects().length);
  const first = targets[0];
  const last = targets[targets.length - 1];
  if (!dialog.value.contains(document.activeElement)) {
    event.preventDefault(); (event.shiftKey ? last : first)?.focus(); return;
  }
  if (event.shiftKey && (document.activeElement === first || document.activeElement === dialog.value)) {
    event.preventDefault(); last?.focus();
  } else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
}

onMounted(async () => {
  previousFocus = document.activeElement;
  previousOverflow = document.body.style.overflow;
  document.body.style.overflow = 'hidden';
  document.addEventListener('keydown', handleKeydown);
  await nextTick();
  firstInput.value?.focus();
  loadDevices();
});
onBeforeUnmount(() => {
  controller.abort();
  document.body.style.overflow = previousOverflow;
  document.removeEventListener('keydown', handleKeydown);
  previousFocus?.focus();
});
</script>

<style>
.fuel-report-overlay { position: fixed; inset: 0; z-index: 1000; background: #101827b8; padding: 24px; display: flex; align-items: center; justify-content: center; }
.fuel-report-dialog { background: white; border-radius: 12px; width: 100%; max-width: 1000px; max-height: 94vh; overflow-y: auto; box-shadow: 0 20px 70px #0005; color: #1f2937; }
.fuel-report-modal-header { display: flex; justify-content: space-between; align-items: flex-start; padding: 22px 24px; border-bottom: 1px solid #e5e7eb; gap: 16px; }
.fuel-report-modal-header h2 { font-size: 20px; font-weight: 700; margin: 0; color: #122471; }
.fuel-report-modal-header p, .fuel-report-form-actions p { margin: 5px 0 0; font-size: 13px; color: #64748b; }
.fuel-report-close { font-size: 28px; line-height: 1; padding: 4px 8px; border-radius: 5px; }
.fuel-report-close:hover { background: #eef2f7; }
.fuel-report-form { padding: 20px 24px; }
.fuel-report-fields { display: grid; grid-template-columns: 1fr 1fr 1.2fr; gap: 16px; border: 0; margin: 0; padding: 0; }
.fuel-report-fields label { display: flex; flex-direction: column; gap: 6px; font-weight: 600; font-size: 13px; }
.fuel-report-fields input, .fuel-report-fields select { width: 100%; min-width: 0; padding: 9px 10px; border: 1px solid #cbd5e1; border-radius: 6px; background: white; font: inherit; font-weight: 400; }
.fuel-report-dialog :focus-visible { outline: 2px solid #2563eb; outline-offset: 3px; }
.fuel-report-form-actions { display: flex; justify-content: space-between; align-items: center; gap: 15px; margin-top: 16px; }
.fuel-report-primary, .fuel-report-secondary { padding: 9px 14px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; }
.fuel-report-primary { background: #142777; color: white; }
.fuel-report-primary:hover:not(:disabled) { background: #203b9b; }
.fuel-report-secondary { border: 1px solid #cbd5e1; background: white; }
.fuel-report-primary:disabled, .fuel-report-secondary:disabled { opacity: .45; cursor: not-allowed; }
.fuel-report-error { margin-top: 14px; background: #fef2f2; color: #b91c1c; padding: 12px; border-radius: 6px; font-size: 13px; }
.fuel-report-status { padding-top: 12px; color: #142777; font-size: 13px; }
.fuel-report-placeholder { text-align: center; padding: 45px 20px; background: #f5f7fb; border-block: 1px solid #e2e8f0; color: #64748b; }
.fuel-report-placeholder svg { width: 45px; margin: 0 auto 10px; color: #879bb9; }
.fuel-report-placeholder h3 { font-size: 16px; font-weight: 600; color: #334155; }
.fuel-report-placeholder p { font-size: 13px; margin-top: 6px; }
.fuel-report-preview { background: #e9edf3; padding: 22px; }
.fuel-report-preview-formats { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.fuel-report-preview-formats span { font-size: 13px; font-weight: 600; margin-right: 8px; }
.fuel-report-modal-footer { padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; gap: 14px; border-top: 1px solid #e2e8f0; }
.fuel-report-modal-footer span { font-size: 12px; color: #64748b; max-width: 460px; }
.fuel-report-modal-footer > div { display: flex; flex-wrap: wrap; gap: 8px; flex-shrink: 0; }
@media screen and (max-width: 640px) {
  .fuel-report-overlay { padding: 8px; }
  .fuel-report-dialog { max-height: 97vh; }
  .fuel-report-fields { grid-template-columns: 1fr; }
  .fuel-report-modal-header, .fuel-report-form, .fuel-report-modal-footer { padding: 16px; }
  .fuel-report-form-actions, .fuel-report-modal-footer { flex-direction: column; align-items: stretch; }
  .fuel-report-preview { padding: 8px; }
  .fuel-report-modal-footer > div { justify-content: flex-end; }
}
</style>
