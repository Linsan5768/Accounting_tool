<script setup>
import { watch } from 'vue'
import { useTheme } from '@/composables/useTheme.js'

const { themeName } = useTheme()

// 只在主题真正改变时才触发切换
watch(themeName, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    document.documentElement.classList.toggle('dark', newVal === 'dark')
  }
}, { immediate: false }) // 移除 immediate 选项，避免组件挂载时就触发
</script>

<template>
  <div class="container">
    <div class="card">
      <img src="@/assets/image1.png" alt="插图" class="welcome-image" />

      <h1>Hi 👋 欢迎回来！</h1>
      <p class="subtext">
        从今天开始，记录每一笔支出，为生活负责。
      </p>

      <div class="button-group">
        <router-link to="/add" class="button">📝 马上来记一笔</router-link>
        <router-link to="/records" class="button">📜 查看历史记录</router-link>
        <router-link to="/statistics" class="button">📊 月度消费统计</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  padding-top: 100px;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100dvh;
  min-height: 100vh;
  background: var(--bg-base);
}


.card {
  background: var(--bg-card);
  padding: 3rem 2.5rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
  text-align: center;
  width: 90%;
  max-width: 400px;
  animation: fadeIn 1s ease;
  margin-bottom: 200px;
  border-radius: 10px;
}



.welcome-image {
  width: 160px;
  margin: 0 auto auto;
  animation: float 3s ease-in-out infinite;
}

h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: auto;
  
}

.subtext {
  font-size: 1.1rem;
  color: var(--text-subtle);
  margin-bottom: 2rem;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.button {
  display: block;
  padding: 12px;
  text-decoration: none;
  background: var(--primary);
  color: var(--text-subtle);
  font-weight: bold;
  border-radius: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  font-size: 16px;
  text-align: center;
}

.button:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.4);
}

@keyframes float {
  0% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
  100% { transform: translateY(0); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>