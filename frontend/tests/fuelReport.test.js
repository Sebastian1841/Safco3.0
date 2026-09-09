const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { loadReportSource } = require('./loadReportSource.cjs');

// Cargar el módulo ES sin cambiar el formato de los archivos de Vue CLI.
const source = loadReportSource(path.join(__dirname, '../src/utils/fuelReport.js'));
const modulePromise = import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`);
const pdfSource = fs.readFileSync(path.join(__dirname, '../src/utils/fuelReportPdf.js'), 'utf8')
  .replace("import { jsPDF } from 'jspdf';", `import pdfPackage from ${JSON.stringify(pathToFileURL(require.resolve('jspdf')).href)}; const { jsPDF } = pdfPackage;`)
  .replace("import { autoTable } from 'jspdf-autotable';", `import tablePackage from ${JSON.stringify(pathToFileURL(require.resolve('jspdf-autotable')).href)}; const { autoTable } = tablePackage;`)
  .replace("'./fuelReport'", JSON.stringify(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`));
const pdfModulePromise = import(`data:text/javascript;base64,${Buffer.from(pdfSource).toString('base64')}`);

test('valida fechas reales, orden y selección de estanque', async () => {
  const { validateReportFilters: validate } = await modulePromise;
  assert.equal(validate('2026-08-01', '2026-08-31', 1), '');
  for (const args of [['', '2026-08-31', 1], ['2026-02-30', '2026-03-01', 1],
    ['2026-08-31', '2026-08-01', 1], ['2026-08-01', '2026-08-31', '']]) {
    assert.ok(validate(...args));
  }
});

test('consulta agosto completo y divide rangos largos sin huecos ni días duplicados', async () => {
  const { splitReportRange } = await modulePromise;
  assert.deepEqual(splitReportRange('2026-08-01', '2026-08-31'), [
    { fecha_inicio: '2026-08-01', fecha_fin: '2026-08-31' },
  ]);
  assert.equal(splitReportRange('2024-01-01', '2024-12-31').length, 1);
  const chunks = splitReportRange('2024-01-01', '2026-08-31');
  assert.equal(chunks.length, 3);
  assert.equal(chunks[0].fecha_inicio, '2024-01-01');
  assert.equal(chunks.at(-1).fecha_fin, '2026-08-31');
  chunks.forEach((chunk, index) => {
    assert.ok((Date.parse(chunk.fecha_fin) - Date.parse(chunk.fecha_inicio)) / 86400000 + 1 <= 366);
    if (index) assert.equal(Date.parse(chunk.fecha_inicio) - Date.parse(chunks[index - 1].fecha_fin), 86400000);
  });
});

test('calcula solo el estanque seleccionado, ordena y cuenta equipos por ID', async () => {
  const { createFuelReport } = await modulePromise;
  const rows = [
    { id: 2, dispositivo_id: '1', fecha: '2026-08-31T15:00:00Z', litros: '25.5', ibutton: ' N/A ', dato1_id: 7 },
    { id: 3, dispositivo_id: 2, fecha: '2026-08-02T15:00:00Z', litros: 999, dato1_id: 8 },
    { id: 1, dispositivo_id: 1, fecha: '2026-08-01T15:00:00Z', litros: 74.5, ibutton: 'ABC', dato1_id: 7 },
  ];
  const result = createFuelReport(rows, { id: 1, nombre: 'Tanque Fijo' }, '2026-08-01', '2026-08-31');
  assert.equal(result.totalLiters, 100);
  assert.equal(result.averageLiters, 50);
  assert.equal(result.equipmentCount, 1);
  assert.equal(result.ibuttonCount, 1);
  assert.deepEqual(result.rows.map(row => row.id), [1, 2]);
  assert.equal(rows[0].litros, '25.5'); // no muta los registros originales
});

test('un período vacío genera ceros y los registros inválidos no se ocultan como cero', async () => {
  const { createFuelReport } = await modulePromise;
  const args = [{ id: 1, nombre: 'Tanque Fijo' }, '2026-08-01', '2026-08-31'];
  const report = createFuelReport([], ...args);
  assert.equal(report.totalLiters, 0);
  assert.equal(report.averageLiters, 0);
  for (const liters of [null, undefined, '', 'error', Infinity]) {
    assert.throws(() => createFuelReport([{ dispositivo_id: 1, fecha: '2026-08-01T15:00:00Z', litros: liters }], ...args));
  }
  assert.throws(() => createFuelReport([{ dispositivo_id: 1, fecha: 'inválida', litros: 10 }], ...args));
});

test('usa fechas de Santiago y distingue ausencia de iButton', async () => {
  const { reportToday, reportTimestamp, reportIbutton } = await modulePromise;
  assert.equal(reportToday(new Date('2026-08-02T01:00:00Z')), '2026-08-01');
  assert.equal(reportTimestamp('2026-08-02T01:00:00Z', true), '21:00:00');
  for (const value of [null, '', 'N/A', 'None', '_NO_IBUTTON_']) assert.equal(reportIbutton(value), '');
  assert.equal(reportIbutton(' ABC '), 'ABC');
});

test('agrega los apodos existentes sin reemplazar el ID ni alterar los totales', async () => {
  const { createFuelReport } = await modulePromise;
  const ids = [' 016e818a01000082 ', '820000018A816E01', '2900000126F9AA01', '0000000000001234', 'N/A', 'constructor'];
  const rows = ids.map((ibutton, id) => ({ id, ibutton, dispositivo_id: 1, fecha: '2026-08-01T15:00:00Z', litros: 10 }));
  const report = createFuelReport(rows, { id: 1, nombre: 'Fijo' }, '2026-08-01', '2026-08-31');
  assert.deepEqual(report.rows.map(row => row.ibutton_alias), ['Llavero Verde', 'Llavero Verde', 'Jaime Benavides', 'Sin apodo', 'Sin iButton', 'Sin apodo']);
  assert.equal(report.rows[0].ibutton, '016e818a01000082');
  assert.equal(report.totalLiters, 60);
  assert.equal(rows[0].ibutton, ids[0]);
});

test('incluye la última hora de agosto en Chile y excluye los días vecinos', async () => {
  const { reportQueryRanges, createFuelReport } = await modulePromise;
  assert.deepEqual(reportQueryRanges('2026-08-01', '2026-08-31'), [
    { fecha_inicio: '2026-07-31', fecha_fin: '2026-09-01' },
  ]);
  const rows = ['2026-08-01T03:30:00Z', '2026-08-01T04:00:00Z', '2026-09-01T03:59:59Z', '2026-09-01T04:00:00Z']
    .map((fecha, id) => ({ fecha, id, dispositivo_id: 1, litros: 10 }));
  const report = createFuelReport(rows, { id: 1, nombre: 'Fijo' }, '2026-08-01', '2026-08-31');
  assert.deepEqual(report.rows.map(row => row.id), [1, 2]);
  assert.equal(report.totalLiters, 20);
});

test('genera un PDF real con el logo, todas las filas y nombre de archivo seguro', async () => {
  const { createFuelReport } = await modulePromise;
  const { createFuelReportPdf, fuelReportFilename } = await pdfModulePromise;
  const rows = Array.from({ length: 120 }, (_, id) => ({ id, fecha: '2026-08-10T15:00:00Z', dispositivo_id: 2, litros: 10, ibutton: '2900000126F9AA01' }));
  const report = createFuelReport(rows, { id: 2, nombre: 'Estanque Móvil / SAFCO' }, '2026-08-01', '2026-08-31');
  const logo = new Uint8Array(fs.readFileSync(path.join(__dirname, '../src/assets/sinergy-group.png')));
  const pdf = createFuelReportPdf(report, logo);
  assert.equal(fuelReportFilename(report), 'informe-combustible-estanque-movil-safco-2026-08-01_2026-08-31.pdf');
  assert.equal(pdf.lastAutoTable.body.length, 120);
  assert.equal(pdf.lastAutoTable.body[0].cells[5].text.join(' '), 'Jaime Benavides');
  assert.match(pdf.lastAutoTable.body[0].cells[4].text.join(''), /2900000126F9AA01/);
  assert.ok(pdf.getNumberOfPages() > 1);
  assert.equal(Buffer.from(pdf.output('arraybuffer')).subarray(0, 5).toString(), '%PDF-');
});

test('un informe vacío también se puede descargar como PDF válido', async () => {
  const { createFuelReport } = await modulePromise;
  const { createFuelReportPdf } = await pdfModulePromise;
  const report = createFuelReport([], { id: 1, nombre: 'Fijo' }, '2026-08-01', '2026-08-31');
  const logo = new Uint8Array(fs.readFileSync(path.join(__dirname, '../src/assets/sinergy-group.png')));
  const pdf = createFuelReportPdf(report, logo);
  assert.equal(pdf.lastAutoTable.body.length, 1);
  assert.ok(Buffer.from(pdf.output('arraybuffer')).length > 1000);
});
