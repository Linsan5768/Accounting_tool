<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useTheme } from '@/composables/useTheme.js'
import eggImage5 from '@/assets/image5.png' // 初始图片
import eggImage from '@/assets/image.png'
import eggImage1 from '@/assets/image1.png'
import eggImage3 from '@/assets/image3.png'
import eggImage4 from '@/assets/image4.png'

const { themeName } = useTheme()

// 只在主题真正改变时才触发切换
watch(themeName, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    document.documentElement.classList.toggle('dark', newVal === 'dark')
  }
}, { immediate: false })

// 容器和彩蛋相关状态
const container = ref(null)
const eggStyle = ref({})
const eggVisible = ref(true)
// 初始彩蛋图片为 eggImage5
const eggSrc = ref(eggImage5)
// 定义可选图片数组（点击后随机切换为其中之一）
const eggImages = [eggImage, eggImage1, eggImage3, eggImage4]

// 用于统计点击次数
const clickCount = ref(0)
// 背景模式下存放铺满 container 的彩蛋数据
const backgroundEggs = ref([])

// 单个彩蛋随机定位与旋转逻辑
const updateEggPosition = () => {
  if (container.value) {
    const eggWidth = 120
    const eggHeight = 120
    const containerWidth = container.value.clientWidth
    const containerHeight = container.value.clientHeight
    // 保证图片不会超出容器边界
    const maxLeft = containerWidth - eggWidth
    const maxTop = containerHeight - eggHeight
    const randomLeft = Math.floor(Math.random() * maxLeft)
    const randomTop = Math.floor(Math.random() * maxTop)
    const randomAngle = Math.random() * 360
    eggStyle.value = {
      position: 'absolute',
      left: `${randomLeft}px`,
      top: `${randomTop}px`,
      width: `${eggWidth}px`,
      height: `${eggHeight}px`,
      pointerEvents: 'auto', // 允许点击
      zIndex: 0,
      transform: `rotate(${randomAngle}deg)`
    }
  }
}

// 生成背景模式下铺满 container 的彩蛋图片数据
const generateBackgroundEggs = () => {
  if (!container.value) return;
  const eggWidth = 120;
  const eggHeight = 120;
  const containerWidth = container.value.clientWidth;
  const containerHeight = container.value.clientHeight;
  // 计算列数与行数，确保铺满 container
  const columns = Math.ceil(containerWidth / eggWidth);
  const rows = Math.ceil(containerHeight / eggHeight);
  let eggs = [];
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < columns; c++) {
      // 基本位置
      const left = c * eggWidth;
      const top = r * eggHeight;
      // 加入随机偏移（可选）
      const offsetX = Math.random() * 20 - 10; // -10 ~ 10
      const offsetY = Math.random() * 20 - 10;
      // 随机角度
      const randomAngle = Math.random() * 360;
      // 随机选取图片
      const randomIndex = Math.floor(Math.random() * eggImages.length);
      const src = eggImages[randomIndex];
      eggs.push({
        src,
        style: {
          position: 'absolute',
          left: `${left + offsetX}px`,
          top: `${top + offsetY}px`,
          width: `${eggWidth}px`,
          height: `${eggHeight}px`,
          pointerEvents: 'none', // 背景图片不需要交互
          zIndex: 0,
          transform: `rotate(${randomAngle}deg)`
        }
      });
    }
  }
  backgroundEggs.value = eggs;
}

// 页面加载后设置初始单个彩蛋的随机位置
onMounted(() => {
  nextTick(() => {
    updateEggPosition()
  })
})

// 点击彩蛋时，累计点击次数
// 3次前：随机切换图片和位置；达到 3 次后进入背景模式
const handleEggClick = () => {
  clickCount.value++
  if (clickCount.value < 3) {
    // 切换图片和重新定位
    const randomIndex = Math.floor(Math.random() * eggImages.length)
    eggSrc.value = eggImages[randomIndex]
    updateEggPosition()
    console.log("彩蛋点击，切换为:", eggSrc.value)
  } else {
    // 第 3 次及以上进入背景模式
    eggVisible.value = false
    nextTick(() => {
      generateBackgroundEggs()
    })
  }
}
</script>

<template>
  <div class="container" ref="container">
    <!-- 单个彩蛋：点击次数小于3时显示 -->
    <img
      v-if="eggVisible"
      :src="eggSrc"
      :style="eggStyle"
      alt="Easter Egg"
      class="easter-egg"
      @click="handleEggClick"
    />
    <!-- 背景模式：点击次数达到3次后铺满 container -->
    <template v-if="!eggVisible">
      <img
        v-for="(egg, index) in backgroundEggs"
        :key="index"
        :src="egg.src"
        :style="egg.style"
        alt="Easter Egg Background"
        class="background-egg"
      />
    </template>
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
  position: relative; /* 作为绝对定位参照 */
  padding-top: 100px;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100dvh;
  min-height: 100vh;
  background: var(--bg-base);
  overflow: hidden;
}

.card {
  position: relative; /* 确保卡片在彩蛋之上 */
  z-index: 1;
  background: var(--bg-card);
  padding: 3rem 2.5rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
  text-align: center;
  width: 90%;
  max-width: 400px;
  animation: fadeIn 1s ease;
  margin-bottom: 200px;
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

.easter-egg {
  cursor: pointer;
  transition: box-shadow 0.3s ease, transform 0.3s ease;
}

.easter-egg:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}

.background-egg {
  /* 背景模式彩蛋图片 */
  pointer-events: none;
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