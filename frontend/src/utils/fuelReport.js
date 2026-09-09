import { ibuttonNickname } from '../config/ibuttonAliases';

const DAY_MS = 86400000;
export const REPORT_TIME_ZONE = 'America/Santiago';

function dateValue(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) return NaN;
  const timestamp = Date.parse(`${value}T00:00:00Z`);
  return Number.isFinite(timestamp) && new Date(timestamp).toISOString().slice(0, 10) === value
    ? timestamp : NaN;
}

export function validateReportFilters(start, end, deviceId) {
  const from = dateValue(start);
  const to = dateValue(end);
  if (!Number.isFinite(from) || !Number.isFinite(to)) return 'Selecciona una fecha inicial y final válidas.';
  if (from > to) return 'La fecha inicial no puede ser posterior a la fecha final.';
  if (!Number.isInteger(Number(deviceId)) || Number(deviceId) <= 0) return 'Selecciona un estanque.';
  return '';
}

// La API recorta consultas mayores a 366 días. Dividir evita perder historia.
export function splitReportRange(start, end) {
  if (validateReportFilters(start, end, 1)) throw new Error('Rango de fechas inválido.');
  const ranges = [];
  const last = dateValue(end);
  for (let from = dateValue(start); from <= last; from += 366 * DAY_MS) {
    ranges.push({
      fecha_inicio: new Date(from).toISOString().slice(0, 10),
      fecha_fin: new Date(Math.min(from + 365 * DAY_MS, last)).toISOString().slice(0, 10),
    });
  }
  return ranges;
}

export function reportQueryRanges(start, end) {
  if (validateReportFilters(start, end, 1)) throw new Error('Rango de fechas inválido.');
  // La API usa UTC-3 fijo. Pedir días de margen y filtrar en Santiago
  // conserva también la última hora del día durante el horario de invierno.
  const from = new Date(dateValue(start) - DAY_MS).toISOString().slice(0, 10);
  const to = new Date(dateValue(end) + DAY_MS).toISOString().slice(0, 10);
  return splitReportRange(from, to);
}

export function reportToday(now = new Date()) {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: REPORT_TIME_ZONE, year: 'numeric', month: '2-digit', day: '2-digit',
  }).formatToParts(now);
  const value = type => parts.find(part => part.type === type).value;
  return `${value('year')}-${value('month')}-${value('day')}`;
}

export function reportDate(value) {
  if (!Number.isFinite(dateValue(value))) return '—';
  const [year, month, day] = value.split('-');
  return `${day}-${month}-${year}`;
}

export function reportTimestamp(value, timeOnly = false) {
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return '—';
  return new Intl.DateTimeFormat('es-CL', {
    timeZone: REPORT_TIME_ZONE,
    ...(timeOnly
      ? { hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23' }
      : { year: 'numeric', month: '2-digit', day: '2-digit' }),
  }).format(date);
}

export function reportNumber(value) {
  return new Intl.NumberFormat('es-CL', { maximumFractionDigits: 2 }).format(value);
}

export function reportIbutton(value) {
  const text = String(value ?? '').trim();
  return !text || ['n/a', 'none', 'null', '_no_ibutton_'].includes(text.toLowerCase()) ? '' : text;
}

export function createFuelReport(records, device, start, end, generatedAt = new Date()) {
  const error = validateReportFilters(start, end, device?.id);
  if (error) throw new Error(error);
  if (!Array.isArray(records)) throw new Error('El servidor no entregó una lista de registros válida.');
  const selected = records.filter(row => Number(row.dispositivo_id) === Number(device.id));
  const rows = selected.map(row => {
    const liters = row.litros === null || row.litros === '' || row.litros === undefined ? NaN : Number(row.litros);
    if (!Number.isFinite(liters) || !Number.isFinite(Date.parse(row.fecha))) {
      throw new Error('Hay registros con fecha o litros inválidos. Revisa los datos antes de generar el informe.');
    }
    const ibutton = reportIbutton(row.ibutton);
    return { ...row, litros: liters, ibutton, ibutton_alias: ibuttonNickname(ibutton) };
  }).filter(row => {
    const day = reportToday(new Date(row.fecha));
    return day >= start && day <= end;
  }).sort((a, b) => Date.parse(a.fecha) - Date.parse(b.fecha) || Number(a.id) - Number(b.id));
  const totalLiters = rows.reduce((total, row) => total + row.litros, 0);
  if (!Number.isFinite(totalLiters)) throw new Error('No se pudo calcular el total de litros.');
  return {
    device: { id: Number(device.id), nombre: device.nombre }, start, end,
    generatedAt: generatedAt.toISOString(), rows, totalLiters,
    averageLiters: rows.length ? totalLiters / rows.length : 0,
    equipmentCount: new Set(rows.filter(row => row.dato1_id != null).map(row => String(row.dato1_id))).size,
    ibuttonCount: new Set(rows.map(row => row.ibutton).filter(Boolean)).size,
  };
}
