<template>
  <div id="app">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="menu-container">
        <button class="menu-btn" @click="toggleMenu" aria-label="菜单">
          𓃑
        </button>
        <div class="menu-content" :class="{ 'menu-open': isMenuOpen }">
          <router-link class="menu-item" to="/" @click="closeMenu">主页</router-link>
          <router-link class="menu-item" to="/add" @click="closeMenu">开始记账</router-link>
          <router-link class="menu-item" to="/records" @click="closeMenu">历史记录</router-link>
          <router-link class="menu-item" to="/statistics" @click="closeMenu">统计分析</router-link>
        </div>
        <!-- 移动端覆盖层 -->
        <div class="menu-overlay" v-if="isMenuOpen" @click="closeMenu"></div>
      </div>
      <div class="theme-switch-wrapper">
        <label class="theme-switch">
          <input type="checkbox" v-model="isDark" @change="handleThemeChange" />
          <span class="slider" :data-icon="isDark ? '☽' : '✹'"></span>
        </label>
      </div>
    </nav>

    <!-- 路由页面 -->
    <router-view />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 菜单状态
const isMenuOpen = ref(false)

// 切换菜单
const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
  document.body.style.overflow = isMenuOpen.value ? 'hidden' : ''
}

// 关闭菜单
const closeMenu = () => {
  isMenuOpen.value = false
  document.body.style.overflow = ''
}

// 主题管理
const isDark = ref(false)

// 初始化主题
onMounted(() => {
  // 从 localStorage 获取主题设置
  const storedTheme = localStorage.getItem('theme')
  // 只在有存储的主题设置时才设置
  if (storedTheme) {
    isDark.value = storedTheme === 'dark'
    document.documentElement.classList.toggle('dark', isDark.value)
  }
})

// 用户点击切换主题
const handleThemeChange = () => {
  // 更新 DOM 类名
  document.documentElement.classList.toggle('dark', isDark.value)
  // 保存到 localStorage
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}
</script>


<style>
:root {
  --bg-base: #fef6f0;
  --bg-card: rgb(252, 241, 233);
  --text-main: #444;
  --text-subtle: #666;
  --primary: #ffb347;
  --primary-hover: rgb(255, 160, 51);
  --slected-box-shadow: 5px 5px 12px rgb(255, 185, 81);
  --box-shadow: 5px 5px 10px rgba(108, 108, 108, 0.7);
  --slected-bt: 5px 5px 10px rgba(251, 151, 0, 0.568);
  --slider-shadow: 2px 2px 10px rgba(0, 0, 0, 0.7);
  --slider-text: rgb(255, 246, 234);
  --menu: #ffb2471a;
  --text-color: rgba(68, 68, 68, 0.15);
}

.dark {
  --bg-base: #1e1e1e;
  --bg-card: #2d2d2d;
  --text-main: #e4e4e4;
  --text-subtle: #a0a0a0;
  --primary: #666666;
  --primary-hover: #777777;
  --input-border: #4d4d4d;
  --bg-input: #2a2a2a;
  --slected-box-shadow: 5px 5px 13px rgba(255, 255, 255, 0.5);
  --box-shadow: 2px 2px 13px rgba(255, 255, 255, 0.4);
  --slected-bt: 0 0 12px rgba(150, 150, 150, 0.5);
  --slider-shadow: 5px 5px 10px rgb(0, 0, 0);
  --slider-text: #1e1e1e;
  --menu: rgba(45, 45, 45, 0.536);
  --text-color: rgba(228, 228, 228, 0.15);
}

html, body {
  height: 100%;
  margin: 0;
  overflow: hidden;
  font-family: 'Poppins', 'PingFang SC', 'Helvetica Neue', sans-serif;
  background-color: var(--bg-base);
  color: var(--text-main);
}

#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 导航栏基础样式 */
.navbar {
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  background-color: var(--bg-base);
  z-index: 100;
  position: relative;
}

/* 菜单容器 */
.menu-container {
  position: relative;
  z-index: 1000;
}

/* 菜单按钮 */
.menu-btn {
  font-size: 1.5rem;
  background: none;
  border: none;
  color: var(--text-main);
  cursor: pointer;
  padding: 10px 16px;
  transition: transform 0.3s ease;
  z-index: 1001;
  position: relative;
}

.menu-btn:hover {
  transform: scale(1.1);
}

/* 菜单内容 - PC端水平显示，移动端垂直显示 */
.menu-content {
  position: absolute;
  background-color: var(--bg-card);
  border-radius: 10px;
  box-shadow: var(--box-shadow);
  overflow: hidden;
  transition: all 0.3s ease-in-out;
  z-index: 1000;
  
  /* PC端默认为水平布局，隐藏在一侧 */
  display: flex;
  flex-direction: row;
  padding: 0;
  
  /* 默认状态（隐藏） */
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
}

/* 菜单打开状态 */
.menu-content.menu-open {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

/* 菜单项 */
.menu-item {
  padding: 12px 20px;
  text-decoration: none;
  color: var(--text-main);
  font-size: 1.1rem;
  transition: all 0.2s ease;
  white-space: nowrap;
  text-align: center;
}

.menu-item:hover {
  background-color: var(--primary);
  color: white;
}

/* 菜单覆盖层，点击时关闭菜单 */
.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 999;
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 主题切换开关 */
.theme-switch-wrapper {
  position: relative;
  z-index: 1000;
}

.theme-switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 32px;
}

.theme-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  background-color: var(--text-subtle);
  border-radius: 999px;
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  transition: background-color 0.4s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
}

.slider::before {
  content: attr(data-icon);
  position: absolute;
  height: 24px;
  width: 24px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  border-radius: 50%;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.4s ease, background-color 0.4s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.8);
  color: var(--text-main);
}

.theme-switch input:checked + .slider::before {
  transform: translateX(28px);
  background-color: #222;
  color: #f1f1f1;
}

/* 媒体查询 - 响应式设计 */
@media (max-width: 768px) {
  /* 移动端菜单样式 */
  .menu-content {
    position: fixed;
    top: 0;
    left: 0;
    height: 100%;
    width: 250px;
    flex-direction: column;
    border-radius: 0;
    box-shadow: 5px 0 15px rgba(0, 0, 0, 0.2);
    transform: translateX(-100%);
    padding-top: 70px;
  }
  
  .menu-content.menu-open {
    transform: translateX(0);
  }
  
  .menu-item {
    width: 100%;
    text-align: left;
    border-bottom: 1px solid var(--input-border);
    padding: 15px 20px;
  }
  
  .theme-switch-wrapper {
    margin-left: auto;
  }
}
</style>