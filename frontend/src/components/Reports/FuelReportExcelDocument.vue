<template>
  <div class="fuel-excel-preview">
    <div class="fuel-excel-toolbar">
      <span>Hoja: Combustible · {{ Math.round(scale * 100) }} %</span>
      <button type="button" class="fuel-report-secondary" :aria-pressed="!fitWidth" @click="fitWidth = !fitWidth">
        {{ fitWidth ? 'Tamaño real' : 'Ajustar al ancho' }}
      </button>
    </div>
    <div ref="viewport" class="fuel-excel-viewport" tabindex="0" aria-label="Vista previa de Excel, hoja Combustible">
      <div class="fuel-excel-scaled" :style="{ width: `${layout.width * scale}px`, height: `${height * scale}px` }">
        <article class="fuel-excel-sheet" aria-label="Informe de combustible en Excel"
          :style="{ width: `${layout.width}px`, transform: `scale(${scale})` }">
          <img :src="sinergyLogo" alt="Sinergy Group" class="fuel-excel-logo" :style="logoStyle" />
          <table aria-label="Contenido del archivo Excel">
            <colgroup><col v-for="column in layout.columnCount" :key="column" :style="{ width: `${layout.columnWidth}px` }" /></colgroup>
            <tbody>
              <tr v-for="row in layout.rows" :key="row.number" :style="{ height: `${row.height}pt` }">
                <td v-if="!row.cells.length" :colspan="layout.columnCount" />
                <td v-for="cell in row.cells" :key="cell.first" :colspan="cell.last - cell.first + 1" :style="cellStyle(cell)"
                  :data-cell="`${row.number}:${cell.first}`">
                  <div :style="{ height: `${Math.max(0, row.height * 4 / 3 - 2)}px`, justifyContent: cell.alignment.horizontal === 'center' ? 'center' : cell.alignment.horizontal === 'right' ? 'flex-end' : 'flex-start' }">
                    <span>{{ formatCell(cell) }}</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onBeforeUnmount } from 'vue';
import { createFuelReportExcelLayout, formatExcelPreviewCell } from '@/utils/fuelReportExcelLayout';
import sinergyLogo from '@/assets/sinergy-group.png';

const props = defineProps({ report: { type: Object, required: true } });
const layout = computed(() => createFuelReportExcelLayout(props.report));
const viewport = ref(null);
const availableWidth = ref(900);
const fitWidth = ref(true);
const scale = computed(() => fitWidth.value ? Math.min(1, availableWidth.value / layout.value.width) : 1);
const height = computed(() => layout.value.rows.reduce((total, row) => total + row.height * 4 / 3, 0));
const logoStyle = computed(() => Object.fromEntries(Object.entries(layout.value.logo).map(([key, value]) => [key, `${value}px`])));
const formatCell = formatExcelPreviewCell;
const color = argb => argb ? `#${argb.slice(-6)}` : 'transparent';
function cellStyle(cell) {
  const style = {
    color: color(cell.font.color.argb), backgroundColor: color(cell.fill.fgColor.argb),
    fontFamily: `${cell.font.name}, Arial, sans-serif`, fontSize: `${cell.font.size}pt`,
    fontWeight: cell.font.bold ? 'bold' : 'normal', fontStyle: cell.font.italic ? 'italic' : 'normal',
    textAlign: cell.alignment.horizontal, padding: cell.alignment.indent ? '0 10px' : '0',
  };
  for (const edge of ['top', 'bottom', 'left', 'right']) {
    const border = cell.border?.[edge];
    style[`border-${edge}`] = border ? `1px solid ${color(border.color.argb)}` : '0';
  }
  return style;
}
let observer;
let resizeFrame;
onMounted(() => {
  availableWidth.value = viewport.value.clientWidth;
  observer = new ResizeObserver(entries => {
    const width = entries[0].contentRect.width;
    if (Math.abs(width - availableWidth.value) < 0.5) return;
    cancelAnimationFrame(resizeFrame);
    resizeFrame = requestAnimationFrame(() => { availableWidth.value = width; });
  });
  observer.observe(viewport.value);
});
onBeforeUnmount(() => { observer?.disconnect(); cancelAnimationFrame(resizeFrame); });
</script>

<style scoped>
.fuel-excel-toolbar { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 12px; color: #52617a; font-size: 12px; }
.fuel-excel-viewport { width: 100%; overflow: auto; background: white; }
.fuel-excel-scaled { overflow: hidden; }
.fuel-excel-sheet { position: relative; transform-origin: top left; background: white; }
.fuel-excel-logo { position: absolute; max-width: none; z-index: 1; }
.fuel-excel-sheet table { width: 100%; border-collapse: collapse; table-layout: fixed; }
.fuel-excel-sheet td { padding: 0; box-sizing: border-box; vertical-align: middle; }
.fuel-excel-sheet td > div { display: flex; align-items: center; overflow: hidden; }
.fuel-excel-sheet td span { white-space: pre-wrap; overflow-wrap: anywhere; line-height: normal; }
</style>
