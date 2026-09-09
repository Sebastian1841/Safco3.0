import { reportDate, reportToday, reportTimestamp } from './fuelReport';

const BLUE = 'FF122471';
const ORANGE = 'FFFF6B00';
const TEAL = 'FF11B7A6';
const LIGHT_BLUE = 'FF2563EB';
const WHITE = 'FFFFFFFF';
const BORDER = 'FFD8DFED';
const PALE = 'FFF5F8FC';
const LITERS = '#,##0.00" L"';
const COLUMN_COUNT = 28;
const COLUMN_WIDTH = 8;
const FOUR_GROUPS = [7, 7, 7, 7];
const TANK_GROUPS = [8, 3, 5, 6, 6];
const DETAIL_GROUPS = [2, 4, 3, 4, 4, 4, 3, 4];

// Interpretar los formatos que usa esta hoja para presentar las mismas
// celdas en el navegador; el XLSX conserva sus valores y tipos nativos.
export function formatExcelPreviewCell(cell) {
  const { value, numFmt } = cell;
  if (value == null) return '';
  if (value instanceof Date) {
    const iso = value.toISOString();
    return numFmt === 'yyyy-mm-dd' ? iso.slice(0, 10)
      : `${reportDate(iso.slice(0, 10))}, ${iso.slice(11, 19)}`;
  }
  if (numFmt === 'hh:mm:ss') {
    const seconds = Math.round(value * 86400);
    return [Math.floor(seconds / 3600) % 24, Math.floor(seconds / 60) % 60, seconds % 60]
      .map(part => String(part).padStart(2, '0')).join(':');
  }
  if (typeof value === 'number') {
    const decimals = numFmt?.includes('.00') ? 2 : 0;
    const text = new Intl.NumberFormat('es-CL', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }).format(value);
    return numFmt?.includes('" L"') ? `${text} L` : text;
  }
  return String(value);
}

// Excel no almacena zona horaria. Guardar la fecha/hora civil de Santiago
// como un valor de calendario evita que cambie al abrirlo en otro equipo.
function excelLocalDate(timestamp) {
  return new Date(`${reportToday(new Date(timestamp))}T${reportTimestamp(timestamp, true)}Z`);
}

export function createFuelReportExcelLayout(report) {
  if (report.rows.length > 1048550) throw new Error('El informe supera la cantidad de filas de una hoja Excel.');
  const layout = { columnCount: COLUMN_COUNT, columnWidth: COLUMN_WIDTH * 7, width: COLUMN_COUNT * COLUMN_WIDTH * 7, rows: [], logo: null };
  function getRow(number) {
    while (layout.rows.length < number) layout.rows.push({ number: layout.rows.length + 1, height: 18, cells: [] });
    return layout.rows[number - 1];
  }

  function cell(row, first, last, value, options = {}) {
    const target = { first, last };
    getRow(row).cells.push(target);
    target.value = value;
    target.font = { name: 'Calibri', size: 11, color: { argb: options.color || BLUE }, bold: !!options.bold, italic: !!options.italic };
    if (options.size) target.font.size = options.size;
    target.alignment = { vertical: 'middle', horizontal: options.align || 'left', wrapText: true, indent: options.align === 'center' ? 0 : 1 };
    target.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: options.fill || WHITE } };
    if (options.border !== false) {
      const edge = { style: 'thin', color: { argb: BORDER } };
      target.border = { top: edge, bottom: edge, left: edge, right: edge };
    }
    if (options.numFmt) target.numFmt = options.numFmt;
    return target;
  }
  function band(row, title) {
    getRow(row).height = 22;
    cell(row, 1, COLUMN_COUNT, title, { fill: BLUE, color: WHITE, bold: true, border: false });
  }
  function grouped(row, values, widths, options = {}) {
    let first = 1;
    values.forEach((value, index) => {
      cell(row, first, first + widths[index] - 1, value, { ...options, ...options.items?.[index] });
      first += widths[index];
    });
  }

  // Ancla en píxeles (EMU): centrado sobre A:AB, con el PNG original 2800×900.
  // El ancho serializado en XLSX ya incluye el relleno: 8 = 56 px en
  // Excel con la fuente normal Calibri 11 (42 puntos, comprobado en Excel).
  const columnPixels = COLUMN_WIDTH * 7;
  const logoWidth = 220;
  const left = (COLUMN_COUNT * columnPixels - logoWidth) / 2;
  for (let row = 1; row <= 3; row++) getRow(row).height = 22;
  layout.logo = { left, top: 8, width: logoWidth, height: logoWidth * 900 / 2800 };
  cell(4, 1, COLUMN_COUNT, 'Monitoreo GPS y Telemetría IoT', { align: 'center', italic: true, size: 9, border: false })
    .border = { bottom: { style: 'thin', color: { argb: ORANGE } } };
  cell(5, 1, COLUMN_COUNT, 'INFORME DE COMBUSTIBLE', { align: 'center', bold: true, size: 16, border: false });
  getRow(5).height = 26;
  const period = `${reportDate(report.start)} a ${reportDate(report.end)}`;
  const generated = `${reportTimestamp(report.generatedAt)}, ${reportTimestamp(report.generatedAt, true)}`;
  cell(6, 1, COLUMN_COUNT, `${report.device.nombre} | ${period} | Generado: ${generated}`, { align: 'center', bold: true, size: 10, border: false });
  getRow(6).height = 28;
  for (const row of [7, 11, 15, 19]) getRow(row).height = 8;

  band(8, 'Datos generales');
  grouped(9, ['Reporte', 'Período', 'Estanque', 'Generado'], FOUR_GROUPS, { align: 'center', bold: true, size: 10 });
  grouped(10, ['Movimientos de combustible', period, String(report.device.nombre), excelLocalDate(report.generatedAt)], FOUR_GROUPS,
    { align: 'center', fill: PALE, items: { 3: { numFmt: 'dd-mm-yyyy, hh:mm:ss' } } });
  getRow(10).height = 30;

  band(12, 'Resumen del período');
  const colors = [BLUE, TEAL, ORANGE, LIGHT_BLUE];
  grouped(13, ['Litros registrados', 'Registros', 'Promedio por registro', 'Equipos identificados'], FOUR_GROUPS,
    { align: 'center', bold: true, color: WHITE, items: colors.map(fill => ({ fill })) });
  grouped(14, [report.totalLiters, report.rows.length, report.averageLiters, report.equipmentCount], FOUR_GROUPS,
    { align: 'center', bold: true, size: 14, fill: 'FFEFF6FF', items: colors.map((color, index) => ({ color, numFmt: index % 2 === 0 ? LITERS : '#,##0' })) });
  getRow(14).height = 28;

  band(16, 'Estanque incluido');
  grouped(17, ['Estanque', 'ID', 'Registros', 'Litros registrados', 'iButton distintos'], TANK_GROUPS, { fill: BLUE, color: WHITE, bold: true });
  grouped(18, [String(report.device.nombre), report.device.id, report.rows.length, report.totalLiters, report.ibuttonCount], TANK_GROUPS,
    { fill: PALE, items: { 0: { bold: true }, 1: { color: ORANGE, bold: true, align: 'center' }, 3: { numFmt: LITERS } } });
  getRow(18).height = 30;

  band(20, 'Detalle de combustible');
  grouped(21, ['#', 'Fecha', 'Hora', 'Litros', 'iButton ID', 'Apodo iButton', 'COD Equipo', 'ACC Negocio'], DETAIL_GROUPS, { fill: BLUE, color: WHITE, bold: true });
  report.rows.forEach((record, index) => {
    const row = index + 22;
    const localDate = excelLocalDate(record.fecha);
    const time = (localDate.getUTCHours() * 3600 + localDate.getUTCMinutes() * 60 + localDate.getUTCSeconds()) / 86400;
    grouped(row, [index + 1, new Date(`${reportToday(new Date(record.fecha))}T00:00:00Z`), time, record.litros,
      String(record.ibutton || 'Sin iButton'), record.ibutton_alias, String(record.dato1_nombre || 'Sin asignar'), String(record.dato2_nombre || 'Sin asignar')], DETAIL_GROUPS,
    { fill: index % 2 === 0 ? PALE : WHITE, items: {
      0: { align: 'right', numFmt: '0' }, 1: { numFmt: 'yyyy-mm-dd' }, 2: { numFmt: 'hh:mm:ss' },
      3: { align: 'right', numFmt: '#,##0.00' }, 4: { numFmt: '@' }, 5: { numFmt: '@' }, 6: { numFmt: '@' }, 7: { numFmt: '@' },
    } });
    // Las celdas combinadas no ajustan altura automáticamente en Excel.
    const longest = Math.max(...[record.ibutton, record.ibutton_alias, record.dato1_nombre, record.dato2_nombre].map(value => String(value || '').length));
    getRow(row).height = Math.min(409, Math.max(22, Math.ceil(longest / 25) * 15));
  });
  if (!report.rows.length) {
    cell(22, 1, COLUMN_COUNT, 'No hay registros para el estanque y las fechas seleccionadas.', { align: 'center', fill: PALE });
    getRow(22).height = 30;
  }
  const totalRow = 22 + Math.max(report.rows.length, 1);
  cell(totalRow, 1, 9, 'Total del período', { bold: true, fill: PALE });
  cell(totalRow, 10, 13, report.totalLiters, { bold: true, align: 'right', numFmt: LITERS, fill: PALE });
  cell(totalRow, 14, COLUMN_COUNT, '', { fill: PALE });
  getRow(totalRow).height = 26;
  cell(totalRow + 2, 1, COLUMN_COUNT, 'Fechas y horas: America/Santiago. Los litros registrados corresponden a movimientos y no representan el saldo disponible del estanque.', { size: 10, border: false });
  getRow(totalRow + 2).height = 28;
  return layout;
}

