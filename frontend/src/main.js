import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './assets/styles/theme.css'

const app = createApp(App)
const pinia = createPinia()

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
// 配置 Element Plus，将消息提示位置下移，避免遮挡按钮
app.use(ElementPlus, {
  message: {
    offset: 160  // 将消息提示向下偏移80px，避免遮挡导航栏和按钮
  }
})


app.mount('#app')
