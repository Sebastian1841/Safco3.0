import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../Views/SafcoDashboard.vue'
import Tables from '../Views/SafcoTables.vue'
import InputData from '../Views/SafcoInputData.vue'
import Factura from '../Views/FacturasCopec.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/tables', name: 'Tables', component: Tables },
  { path: '/input-data', name: 'InputData', component: InputData },
  { path: '/factura', name: 'Factura', component: Factura }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
