import { createApp } from 'vue'
import 'remixicon/fonts/remixicon.css'
import './style.css'
import App from './App.vue'
import router from './router'
import pinia from './stores'

const app = createApp(App)

app.use(router)
app.use(pinia)

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue 错误:', err)
  console.error('组件:', vm)
  console.error('信息:', info)
}

app.mount('#app')
