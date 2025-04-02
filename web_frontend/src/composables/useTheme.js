// src/composables/useTheme.js
import { ref, computed, watch } from 'vue'
import { themes } from '@/styles/theme.js'

// 1. 从 localStorage 或系统偏好初始化
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
const saved = localStorage.getItem('theme') || (prefersDark ? 'dark' : 'light')

const themeName = ref(saved)
const isDark = computed(() => themeName.value === 'dark')
const theme = computed(() => themes[themeName.value])

// 2. 响应式保存至本地存储
watch(themeName, (val) => {
  localStorage.setItem('theme', val)
})

// 3. 导出统一接口
export function useTheme() {
  return { themeName, isDark, theme }
}