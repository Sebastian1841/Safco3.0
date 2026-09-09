import { jsPDF } from 'jspdf';
import { autoTable } from 'jspdf-autotable';
import { reportDate, reportTimestamp, reportNumber } from './fuelReport';

const BLUE = [18, 36, 113];
const ORANGE = [255, 107, 0];
const BORDER = [216, 223, 237];

export function fuelReportFilename(report) {
  const tank = report.device.nombre.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-zA-Z0-9]+/g, '-').replace(/^-|-$/g, '').toLowerCase() || `estanque-${report.device.id}`;
  return `informe-combustible-${tank}-${report.start}_${report.end}.pdf`;
}

// Texto y tablas nativos: las filas pasan a la siguiente página sin capturas
// de pantalla gigantes, y el texto se puede seleccionar y buscar en el PDF.
export function createFuelReportPdf(report, logoData) {
  const pdf = new jsPDF({ unit: 'mm', format: 'a4', compress: true });
  const margin = 15;
  const width = 180;
  let y = 17;
  pdf.setProperties({ title: 'Informe de combustible - SAFCO', subject: report.device.nombre, author: 'Sinergy Group' });
  const logo = pdf.getImageProperties(logoData);
  const logoWidth = 70;
  const logoHeight = logoWidth * logo.height / logo.width;
  pdf.addImage(logoData, 'PNG', (210 - logoWidth) / 2, y, logoWidth, logoHeight);
  y += logoHeight + 5;
  pdf.setFont('helvetica', 'italic').setFontSize(7).setTextColor(...BLUE);
  pdf.text('Monitoreo GPS y Telemetría IoT', 105, y, { align: 'center' });
  y += 6;
  pdf.setDrawColor(...ORANGE).setLineWidth(0.5).line(margin, y, 195, y);
  y += 9;
  pdf.setFont('helvetica', 'bold').setFontSize(15);
  pdf.text('INFORME DE COMBUSTIBLE', 105, y, { align: 'center' });
  y += 6;
  pdf.setFont('helvetica', 'normal').setFontSize(8);
  const subtitle = pdf.splitTextToSize(`SAFCO · ${report.device.nombre} | ${reportDate(report.start)} a ${reportDate(report.end)}`, width);
  pdf.text(subtitle, 105, y, { align: 'center' });
  y += subtitle.length * 4 + 6;

  function section(title) {
    if (y > 253) { pdf.addPage(); y = 18; }
    pdf.setTextColor(...BLUE).setFont('helvetica', 'bold').setFontSize(10);
    pdf.text(title, margin, y);
    pdf.setDrawColor(...ORANGE).setLineWidth(0.4).line(margin, y + 3, 195, y + 3);
    y += 7;
  }
  function table(options) {
    autoTable(pdf, {
      startY: y, margin: { top: 16, right: margin, bottom: 17, left: margin }, tableWidth: width,
      theme: 'grid', rowPageBreak: 'avoid',
      styles: { font: 'helvetica', fontSize: 8, textColor: BLUE, lineColor: BORDER, lineWidth: 0.2, cellPadding: 2.4, overflow: 'linebreak' },
      headStyles: { fillColor: BLUE, textColor: [255, 255, 255], halign: 'center', fontStyle: 'bold' },
      alternateRowStyles: { fillColor: [245, 248, 252] },
      ...options,
    });
    y = pdf.lastAutoTable.finalY + 10;
  }

  section('Datos generales');
  table({ body: [
    ['Reporte', 'Movimientos de combustible registrados'],
    ['Estanque', report.device.nombre],
    ['Rango consultado', `${reportDate(report.start)} a ${reportDate(report.end)} (ambos días incluidos)`],
    ['Registros', String(report.rows.length)],
    ['Generado', `${reportTimestamp(report.generatedAt)}, ${reportTimestamp(report.generatedAt, true)}`],
  ], columnStyles: { 0: { cellWidth: 44, fontStyle: 'bold' } } });

  section('Resumen del período');
  table({ body: [
    [`${reportNumber(report.totalLiters)} L`, reportNumber(report.rows.length), `${reportNumber(report.averageLiters)} L`, reportNumber(report.equipmentCount)],
    ['Litros registrados', 'Registros', 'Promedio por registro', 'Equipos identificados'],
  ], styles: { fontSize: 8, textColor: BLUE, lineColor: BORDER, lineWidth: 0.2, cellPadding: 3, halign: 'center', cellWidth: 45 },
  didParseCell(data) {
    if (data.row.index === 0) Object.assign(data.cell.styles, { fontSize: 14, fontStyle: 'bold', textColor: [BLUE, [0, 140, 135], ORANGE, [37, 99, 235]][data.column.index] });
  } });

  section('Estanque incluido');
  table({ head: [['Estanque', 'ID', 'Registros', 'Litros registrados', 'iButton distintos']],
    body: [[report.device.nombre, report.device.id, report.rows.length, `${reportNumber(report.totalLiters)} L`, report.ibuttonCount]],
  });

  section('Detalle de combustible');
  table({ head: [['#', 'Fecha', 'Hora', 'Litros', 'iButton ID', 'Apodo iButton', 'COD Equipo', 'ACC Negocio']],
    body: report.rows.length ? report.rows.map((row, index) => [
      index + 1, reportTimestamp(row.fecha), reportTimestamp(row.fecha, true), reportNumber(row.litros),
      row.ibutton || 'Sin iButton', row.ibutton_alias, row.dato1_nombre || 'Sin asignar', row.dato2_nombre || 'Sin asignar',
    ]) : [[{ content: 'No hay registros para el estanque y las fechas seleccionadas.', colSpan: 8, styles: { halign: 'center' } }]],
    columnStyles: { 0: { cellWidth: 7 }, 1: { cellWidth: 21 }, 2: { cellWidth: 18 }, 3: { cellWidth: 18, halign: 'right' }, 4: { cellWidth: 32 }, 5: { cellWidth: 30 }, 6: { cellWidth: 27 }, 7: { cellWidth: 27 } },
  });
  if (y > 253) { pdf.addPage(); y = 18; }
  pdf.setFont('helvetica', 'bold').setFontSize(10).setTextColor(...BLUE);
  pdf.text(`Total del período: ${reportNumber(report.totalLiters)} L`, 195, y, { align: 'right' });
  y += 7;
  pdf.setFont('helvetica', 'normal').setFontSize(7).setTextColor(82, 97, 122);
  pdf.text(pdf.splitTextToSize('Fechas y horas de los movimientos: America/Santiago. El informe presenta los registros disponibles al momento de generarlo. Los litros registrados no representan el saldo disponible del estanque.', width), margin, y);
  const pages = pdf.getNumberOfPages();
  for (let page = 1; page <= pages; page++) {
    pdf.setPage(page);
    pdf.setFont('helvetica', 'normal').setFontSize(7).setTextColor(82, 97, 122);
    pdf.text(`SAFCO · Página ${page} de ${pages}`, 195, 289, { align: 'right' });
  }
  return pdf;
}

export async function downloadFuelReport(report, logoUrl, signal) {
  // Solo se carga la imagen local empaquetada con el frontend.
  const response = await fetch(logoUrl, { signal });
  if (!response.ok) throw new Error('No se pudo cargar el logo del informe.');
  const logoData = new Uint8Array(await response.arrayBuffer());
  if (signal?.aborted) return false;
  const pdf = createFuelReportPdf(report, logoData);
  if (signal?.aborted) return false;
  await pdf.save(fuelReportFilename(report), { returnPromise: true });
  return true;
}
