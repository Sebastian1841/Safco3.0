const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const ExcelJS = require('exceljs');
const JSZip = require('jszip');
const { loadReportSource } = require('./loadReportSource.cjs');

const source = loadReportSource(path.join(__dirname, '../src/utils/fuelReport.js'));
const helperUrl = `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`;
const modulePromise = import(helperUrl);
const excelSource = loadReportSource(path.join(__dirname, '../src/utils/fuelReportExcel.js'))
  .replace("'exceljs'", JSON.stringify(pathToFileURL(require.resolve('exceljs')).href))
  .replace("'./fuelReport'", JSON.stringify(helperUrl));
const excelModulePromise = import(`data:text/javascript;base64,${Buffer.from(excelSource).toString('base64')}`);
const logo = new Uint8Array(fs.readFileSync(path.join(__dirname, '../src/assets/sinergy-group.png')));

async function exportReport(rows) {
  const { createFuelReport } = await modulePromise;
  const { createFuelReportExcel } = await excelModulePromise;
  const report = createFuelReport(rows, { id: 2, nombre: 'Estanque Móvil / SAFCO' }, '2026-08-01', '2026-08-31', new Date('2026-09-01T03:30:00Z'));
  const buffer = await createFuelReportExcel(report, logo).xlsx.writeBuffer();
  const workbook = await new ExcelJS.Workbook().xlsx.load(buffer);
  return { report, buffer, workbook, sheet: workbook.getWorksheet('Combustible') };
}

test('Excel real conserva todos los movimientos, litros numéricos y fechas de Santiago', async () => {
  const rows = Array.from({ length: 120 }, (_, id) => ({ id, fecha: '2026-09-01T03:59:59Z', dispositivo_id: 2, litros: 10.25,
    ibutton: '00001234567890123456', dato1_nombre: `EQUIPO-${id}`, dato2_nombre: '=1+1' }));
  rows.push({ id: 999, fecha: '2026-08-10T15:00:00Z', dispositivo_id: 1, litros: 999 });
  const { sheet, report } = await exportReport(rows);
  for (let index = 0; index < 120; index++) {
    const row = index + 22;
    assert.equal(sheet.getCell(row, 1).value, index + 1);
    assert.equal(sheet.getCell(row, 3).value.toISOString(), '2026-08-31T00:00:00.000Z');
    const time = sheet.getCell(row, 7).value;
    assert.equal(time.getUTCHours(), 23);
    assert.equal(time.getUTCMinutes(), 59);
    assert.equal(time.getUTCSeconds(), 59);
    assert.equal(sheet.getCell(row, 10).value, 10.25);
    assert.equal(sheet.getCell(row, 14).value, '00001234567890123456');
    assert.equal(sheet.getCell(row, 18).value, 'Sin apodo');
    assert.equal(sheet.getCell(row, 22).value, `EQUIPO-${index}`);
    assert.equal(sheet.getCell(row, 25).value, '=1+1');
    assert.equal(sheet.getCell(row, 25).type, ExcelJS.ValueType.String);
  }
  assert.equal(sheet.getCell('A14').value, 1230);
  assert.equal(sheet.getCell('H14').value, 120);
  assert.equal(sheet.getCell('J142').value, 1230);
  assert.equal(sheet.getCell('V10').value.toISOString(), '2026-08-31T23:30:00.000Z');
  const { fuelReportExcelFilename } = await excelModulePromise;
  assert.equal(fuelReportExcelFilename(report), 'informe-combustible-estanque-movil-safco-2026-08-01_2026-08-31.xlsx');
});

test('formato de referencia: bandas, cuatro indicadores, logo centrado original y sin gráficos', async () => {
  const { sheet, workbook, buffer } = await exportReport([]);
  assert.equal(sheet.views[0].showGridLines, false);
  for (const [address, title] of [['A8', 'Datos generales'], ['A12', 'Resumen del período'], ['A16', 'Estanque incluido'], ['A20', 'Detalle de combustible']]) {
    assert.equal(sheet.getCell(address).value, title);
    assert.equal(sheet.getCell(address).fill.fgColor.argb, 'FF122471');
    assert.equal(sheet.getCell(address).font.color.argb, 'FFFFFFFF');
  }
  ['A13', 'H13', 'O13', 'V13'].forEach((address, index) => {
    assert.equal(sheet.getCell(address).fill.fgColor.argb, ['FF122471', 'FF11B7A6', 'FFFF6B00', 'FF2563EB'][index]);
  });
  assert.equal(sheet.getCell('A4').border.bottom.color.argb, 'FFFF6B00');
  assert.ok(sheet.model.merges.includes('A8:AB8'));
  assert.ok(sheet.model.merges.includes('V10:AB10'));
  const images = sheet.getImages();
  assert.equal(images.length, 1);
  assert.deepEqual(new Uint8Array(workbook.getImage(images[0].imageId).buffer), logo);
  const { tl, ext } = images[0].range;
  const leftPixels = tl.nativeCol * 56 + tl.nativeColOff / 9525;
  assert.ok(Math.abs(leftPixels + ext.width / 2 - 28 * 56 / 2) < 0.1);
  assert.ok(Math.abs(ext.width / ext.height - 2800 / 900) < 0.01);
  const zip = await JSZip.loadAsync(buffer);
  assert.equal(Object.keys(zip.files).filter(name => name.startsWith('xl/charts/')).length, 0);
});

test('período vacío produce Excel válido, ceros y mensaje explícito', async () => {
  const { sheet } = await exportReport([]);
  assert.match(sheet.getCell('A22').value, /No hay registros/);
  assert.equal(sheet.getCell('A14').value, 0);
  assert.equal(sheet.getCell('O14').value, 0);
  assert.equal(sheet.getCell('J23').value, 0);
});

test('cancelar una exportación Excel evita iniciar la descarga', async () => {
  const { downloadFuelReportExcel } = await excelModulePromise;
  const controller = new AbortController();
  controller.abort();
  assert.equal(await downloadFuelReportExcel(null, 'http://invalid.test/logo.png', controller.signal), false);
});

test('vista previa y Excel comparten valores, apodos, celdas combinadas y estilos', async () => {
  const rows = [{ id: 1, dispositivo_id: 2, fecha: '2026-09-01T03:59:59Z', litros: 12.5, ibutton: '2900000126F9AA01' }];
  const { report, sheet } = await exportReport(rows);
  const source = loadReportSource(path.join(__dirname, '../src/utils/fuelReportExcelLayout.js'));
  const { createFuelReportExcelLayout, formatExcelPreviewCell } = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`);
  const layout = createFuelReportExcelLayout(report);
  for (const row of layout.rows) {
    for (const cell of row.cells) {
      const saved = sheet.getCell(row.number, cell.first);
      if (cell.numFmt === 'hh:mm:ss') assert.equal(saved.value.toISOString().slice(11, 19), formatExcelPreviewCell(cell));
      else assert.deepEqual(saved.value ?? '', cell.value ?? '');
      assert.equal(saved.fill.fgColor.argb, cell.fill.fgColor.argb);
      assert.equal(saved.font.color.argb, cell.font.color.argb);
      assert.equal(saved.font.bold || false, cell.font.bold);
      assert.equal(sheet.getCell(row.number, cell.last).master.address, saved.address);
    }
  }
  assert.equal(sheet.getCell('R22').value, 'Jaime Benavides');
  assert.equal(sheet.getCell('N22').value, '2900000126F9AA01');
  const detail = layout.rows[21].cells;
  assert.equal(formatExcelPreviewCell(detail[1]), '2026-08-31');
  assert.equal(formatExcelPreviewCell(detail[2]), '23:59:59');
  assert.equal(formatExcelPreviewCell(detail[3]), '12,50');
  assert.equal(formatExcelPreviewCell(detail[5]), 'Jaime Benavides');
});
