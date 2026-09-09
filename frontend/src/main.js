import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import './assets/tailwind.css'

const app = createApp(App)

// ===============================
// 🚀 DIRECTIVA click-outside
// ===============================
const clickOutsideDirective = {
  beforeMount(el, binding) {
    el.__clickOutsideHandler__ = (e) => {
      if (!(el === e.target || el.contains(e.target))) {
        binding.value(e)
      }
    }
    document.addEventListener('click', el.__clickOutsideHandler__)
  },
  unmounted(el) {
    document.removeEventListener('click', el.__clickOutsideHandler__)
  }
}

app.directive("click-outside", clickOutsideDirective)

// ===============================
// 🚀 Montar app
// ===============================
app.use(router).mount('#app')
