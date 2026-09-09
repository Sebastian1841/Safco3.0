import ExcelJS from 'exceljs';
import { createFuelReportExcelLayout } from './fuelReportExcelLayout';

export function fuelReportExcelFilename(report) {
  const tank = report.device.nombre.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-zA-Z0-9]+/g, '-').replace(/^-|-$/g, '').toLowerCase() || `estanque-${report.device.id}`;
  return `informe-combustible-${tank}-${report.start}_${report.end}.xlsx`;
}

export function createFuelReportExcel(report, logoData) {
  const layout = createFuelReportExcelLayout(report);
  const workbook = new ExcelJS.Workbook();
  workbook.creator = 'Sinergy Group';
  workbook.title = 'Informe de combustible - SAFCO';
  workbook.subject = report.device.nombre;
  workbook.created = new Date(report.generatedAt);
  workbook.modified = new Date(report.generatedAt);
  const sheet = workbook.addWorksheet('Combustible', {
    views: [{ showGridLines: false, zoomScale: 85 }],
    properties: { defaultRowHeight: 18 },
  });
  sheet.columns = Array.from({ length: layout.columnCount }, () => ({ width: layout.columnWidth / 7 }));
  for (const row of layout.rows) {
    sheet.getRow(row.number).height = row.height;
    for (const cell of row.cells) {
      if (cell.first !== cell.last) sheet.mergeCells(row.number, cell.first, row.number, cell.last);
      const target = sheet.getCell(row.number, cell.first);
      target.value = cell.value;
      target.style = { font: cell.font, alignment: cell.alignment, fill: cell.fill, border: cell.border, numFmt: cell.numFmt };
    }
  }
  const imageId = workbook.addImage({ buffer: logoData, extension: 'png' });
  const nativeCol = Math.floor(layout.logo.left / layout.columnWidth);
  sheet.addImage(imageId, {
    tl: { nativeCol, nativeColOff: Math.round((layout.logo.left - nativeCol * layout.columnWidth) * 9525), nativeRow: 0, nativeRowOff: layout.logo.top * 9525 },
    ext: { width: layout.logo.width, height: layout.logo.height },
    editAs: 'absolute',
  });
  return workbook;
}

export async function downloadFuelReportExcel(report, logoUrl, signal) {
  if (signal?.aborted) return false;
  const response = await fetch(logoUrl, { signal });
  if (!response.ok) throw new Error('No se pudo cargar el logo del informe.');
  const logoData = new Uint8Array(await response.arrayBuffer());
  if (signal?.aborted) return false;
  const workbook = createFuelReportExcel(report, logoData);
  const buffer = await workbook.xlsx.writeBuffer();
  if (signal?.aborted) return false;
  const url = URL.createObjectURL(new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
  const link = document.createElement('a');
  try {
    link.href = url;
    link.download = fuelReportExcelFilename(report);
    document.body.appendChild(link);
    link.click();
  } finally {
    link.remove();
    // Dar tiempo al navegador para iniciar la lectura antes de liberar el Blob.
    setTimeout(() => URL.revokeObjectURL(url), 60000);
  }
  return true;
}
