<template>
  <div class="container">
    <div class="form-card">
      <img src="@/assets/image.png" alt="插图" class="start-image" />

      <h2 class="card-title">📒开始记账</h2>
      <form @submit.prevent="submitRecord">

        <!-- 日期选择 -->
        <div class="form-group">
          <div class="date-picker-wrapper">
            <span class="date-icon">📅</span>
            <input type="text" id="date-picker" v-model="form.date" class="form-control" ref="dateInput">
          </div>
        </div>

        <!-- 金额输入 -->
        <div class="form-group">
          <div class="amount-wrapper">
            <span class="amount-icon">💰</span>
            <input 
              type="text" 
              id="amount" 
              v-model="formattedAmount"
              @focus="removeFormatting"
              @blur="formatAmount"
              class="form-control amount-input"
              required
            />
          </div>
        </div>

        <!-- 收入/支出选择（带滑动动画的 bar） -->
        <div class="form-group">
          <div class="toggle-container">
            <div class="toggle-track">
              <div 
                v-for="type in [{id: 'expense', name: '支出', icon: '💸'}, {id: 'income', name: '收入', icon: '💰'}]" 
                :key="type.id"
                @click="selectType(type.id)"
                :class="['type-btn', { active: form.type === type.id }]"
                ref="typeBtns"
              >
                <span class="icon">{{ type.icon }}</span>
                <span class="text">{{ type.name }}</span>
              </div>
              <!-- 滑块动画 -->
              <div class="type-slider" :style="typeSliderStyle"></div>
            </div>
          </div>
        </div>

        <!-- 类别选择（带滑动动画的 bar） -->
        <div class="form-group">
          <div class="category-bar">
            <div class="category-track">
              <div 
                v-for="(cat, index) in categories" 
                :key="cat.id" 
                @click="selectCategory(cat.id, index)"
                :class="['category-btn', { active: form.category_id === cat.id }]"
                ref="categoryBtns"
              >
                <span class="icon">{{ cat.icon }}</span>
                <span class="text">{{ cat.name }}</span>
              </div>
              <!-- 滑块动画 -->
              <div class="category-slider" :style="sliderStyle"></div>
            </div>
          </div>
        </div>

        <!-- 备注部分 -->
        <div class="form-group">
          <div class="remarks-wrapper">
            <span class="tips-icon">📝</span>
            <textarea 
              id="remarks"
              v-model="form.remarks"
              class="form-control remarks-input"
              placeholder="Tips......"
              rows="1"
              @input="autoResize"
            ></textarea>
          </div>
        </div>

        <button type="submit" class="btn-submit" :disabled="loading">
          <span v-if="loading">提交中…</span>
          <span v-else>提交记录</span>
        </button>

        <div v-if="validationError" class="error-message">
          {{ validationError }}
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import flatpickr from "flatpickr"
import "flatpickr/dist/flatpickr.min.css"

export default {
  name: "AddRecord",
  data() {
    return {
      form: {
        date: '',
        amount: 0,
        type: 'expense',
        category_id: '',
        remarks: ''
      },
      formattedAmount: "",
      categories: [],
      loading: false,
      validationError: '',
      sliderStyle: {},
      typeSliderStyle: {}
    }
  },
  methods: {
    formatAmount() {
      let rawValue = this.formattedAmount.replace(/[^\d.]/g, "")
      const parts = rawValue.split(".")
      if (parts.length > 2) rawValue = parts[0] + "." + parts.slice(1).join("")
      if (parts[1] && parts[1].length > 2) rawValue = parts[0] + "." + parts[1].slice(0, 2)
      this.form.amount = Math.abs(parseFloat(rawValue)) || 0
      this.formattedAmount = rawValue.replace(/\B(?=(\d{3})+(?!\d))/g, ",")
    },
    async submitRecord() {
      this.validationError = ""
      this.loading = true
      if (!this.form.amount || this.form.amount <= 0) {
        this.validationError = "请正确输入有效金额，且金额必须大于零！⚠️"
        this.loading = false
        return
      }
      if (!this.form.category_id) {
        this.validationError = "请选择一个类别！📌"
        this.loading = false
        return
      }
      let processedAmount = this.form.type === "expense" ? -this.form.amount : this.form.amount
      try {
        const res = await axios.post("http://localhost:5002/api/add_record", {
          date: this.form.date,
          amount: processedAmount,
          category_id: this.form.category_id,
          remarks: this.form.remarks
        })
        alert(res.data.message || "提交成功 ✅")
        this.form = { date: '', amount: 0, type: 'expense', category_id: '', remarks: '' }
        this.formattedAmount = ""
      } catch (err) {
        alert("添加记录失败：" + (err.response ? err.response.data.error : err.message))
      } finally {
        this.loading = false
      }
    },
    async fetchCategories() {
      try {
        const res = await axios.get('http://localhost:5002/api/get_categories')
        const icons = {
          '餐饮': '🍔','话费': '📱','理发': '💇','交通': '🚴','洗衣': '👔','超市购物': '🏬','零钱': '💰','房租': '🏠'
        }
        this.categories = res.data.map(cat => ({ ...cat, icon: icons[cat.name] || '📌' }))
        if (this.categories.length > 0) this.selectCategory(this.categories[0].id, 0)
      } catch (err) {
        console.error('获取类别失败：', err)
      }
    },
    selectCategory(id, index) {
      this.form.category_id = id
      this.$nextTick(() => {
        const btn = this.$refs.categoryBtns[index]
        if (btn) {
          this.sliderStyle = {
            transform: `translateX(${btn.offsetLeft}px)`,
            width: `${btn.offsetWidth}px`
          }
        }
      })
    },
    selectType(type) {
      this.form.type = type
      this.$nextTick(() => {
        const btn = this.$refs.typeBtns.find(btn => btn.classList.contains('active'))
        if (btn) {
          this.typeSliderStyle = {
            transform: `translateX(${btn.offsetLeft}px)`,
            width: `${btn.offsetWidth}px`
          }
        }
      })
    },
    autoResize(e) {
      const textarea = e.target
      textarea.style.height = 'auto'
      textarea.style.height = textarea.scrollHeight + 'px'
    }
  },
  mounted() {
    this.fetchCategories()
    flatpickr("#date-picker", {
      dateFormat: "Y-m-d",
      defaultDate: this.form.date || new Date(),
      locale: "zh",
      onChange: (selectedDates, dateStr) => {
        this.form.date = dateStr
      }
    })
    // 初始化类型选择器
    this.$nextTick(() => {
      this.selectType(this.form.type)
    })
  },
  watch: {
    'form.type': function () {
      this.selectType(this.form.type)
    }
  }
}
</script>


<style scoped>

:root {
  --bg-card: #ffffffcc;
  --bg-input: #fff;              /* 明亮、对比卡片略深 */
  --input-border: #d0d0d0;
  --text-main: #333;
}

.dark {
  --bg-card: #3a3a3a;
  --bg-input: #4a4a4a;           /* 深色、对比卡片略浅 */
  --input-border: #9c1b1b;
  --text-main: #e20000;
}

.start-image {
  width: 160px;
  display: block;
  margin: 0 auto; /* 简洁写法，垂直方向为 0，水平方向自动居中 */
  animation: float 3s ease-in-out infinite;
}

/* 居中容器 */
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100dvh;
  min-height: 100vh;
  background: var(--bg-base);
  
}

@keyframes subtleFloat {
  0% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
  100% { transform: translateY(0); }
}

/* 卡片样式：加宽 card，让 category-bar 有足够空间 */
.form-card {
  font-family: var(--font-family);
  font-size: 16px;
  background: var(--bg-card);
  color: var(--text-main);
  backdrop-filter: blur(8px);
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
  width: 100%;
  max-width: 800px;
  margin-bottom: 100px;
  transition: all 0.4s ease;
  animation: fadeIn 0.5s ease;
  box-sizing: border-box; /* 确保padding不影响宽度计算 */
}

.card-title {
  margin-top: auto;
  font-size: 2rem;
  font-weight: 600;
  text-align: center;
  font-family: "STHupo", "Microsoft YaHei", sans-serif;
  color: var(--text-main);
  letter-spacing: 5px;
}

/* 输入相关的容器统一样式 */
.toggle-container,
.category-bar,
.date-picker-wrapper,
.amount-wrapper,
.remarks-wrapper {
  width: 100%;
  border-radius: 8px;
  position: relative;
  display: flex;
  box-sizing: border-box;
}

/* 表单组布局 */
.form-group {
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  margin-bottom: 1.2rem;
  box-shadow: var(--box-shadow);
  width: 100%;
  overflow: hidden;
  background: var(--bg-input);
  padding: 0;
}

.form-group:has(.form-control:focus),
.form-group:has(.amount-input:focus),
.form-group:has(.remarks-input:focus) {
  box-shadow: var(--slected-box-shadow);
}
/* 输入框统一样式 */
.form-control, 
.amount-input,
.remarks-input {
  background: var(--bg-input);
  color: var(--text-main);
  border: 1px solid var(--btn-hover-bg);
  border-radius: 8px;
  padding: 0.75rem 0.75rem 0.75rem 40px;
  font-size: 1rem;
  width: 100%;
  height: 45px;
  box-sizing: border-box;
  box-shadow: none;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.remarks-input {
  height: auto;
  min-height: 45px;
}

.remarks-input::placeholder {
  font-size: 1rem;
  font-weight: bold;
  letter-spacing: 0.5px;
  font-family: 'Poppins', 'PingFang SC', 'Helvetica Neue', sans-serif;
  color: var(--text-main);
  transition: color 0.3s ease;
  text-align: left;
}

/* 输入框交互状态 */
.form-control:hover,
.amount-input:hover,
.remarks-input:hover {
  border-color: var(--input-border);
}

.form-control:focus,
.amount-input:focus,
.remarks-input:focus {
  border-color: var(--primary);
  box-shadow: var(--slected-box-shadow);
  outline: none;
}

/* 按钮样式 */
.btn-submit {
  background-color: var(--primary);
  border: none;
  color: #fff;
  box-shadow: var(--box-shadow);
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border-radius: 6px;
  cursor: pointer;
  display: block;
  margin: 3rem auto 0;
  transition: background-color 0.3s;
  animation: subtleFloat 2s ease-in-out infinite;
}

.btn-submit:hover {
  background-color: var(--primary-hover);
  box-shadow: var(--slected-bt);
}

/* 选择器容器统一样式 */
.toggle-container,
.category-bar {
  padding: 4px;
  justify-content: center;
  margin: 0;
  box-shadow: none;
  height: 53px;
  border-radius: 8px;
  overflow-x: auto;
}

.category-bar {
  white-space: nowrap;
}

/* 选择器轨道统一样式 */
.toggle-track,
.category-track {
  display: flex;
  position: relative;
  width: 100%;
  justify-content: space-between;
  padding: 0;
}

.category-track {
  gap: 6px;
}

/* 按钮统一样式 */
.type-btn,
.category-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 0;
  height: 45px;
  position: relative;
  z-index: 2;
  cursor: pointer;
  box-sizing: border-box;
  background: transparent;
  border: none;
  transition: color 0.3s ease;
}

/* 清除多余的样式 */
.category-btn,
.category-btn:hover {
  background: none !important;
  box-shadow: none !important;
  border: none !important;
}

.category-btn:hover {
  color: inherit;
  transform: none !important;
}

/* 按钮文本统一样式 */
.type-btn .text,
.category-btn .text {
  font-weight: 600;
  letter-spacing: 0.3px;
  font-family: 'PingFang SC', 'Helvetica Neue', sans-serif;
  color: var(--text-main);
  transition: color 0.3s ease;
}

.type-btn .text {
  font-size: 0.95rem;
}

.category-btn .text {
  font-size: 0.85rem;
  text-shadow: none;
}

/* 按钮图标统一样式 */
.type-btn .icon,
.category-btn .icon {
  font-size: 1.2rem;
  transition: color 0.3s ease;
}

/* 活动状态统一样式 */
.type-btn.active .text,
.type-btn.active .icon,
.category-btn.active .text,
.category-btn.active .icon,
.category-btn.active {
  color: var(--slider-text);
}

/* 滑块统一样式 */
.type-slider,
.category-slider {
  position: absolute;
  height: 100%;
  background: var(--primary);
  box-shadow: var(--slider-shadow);
  border-radius: 6px;
  transition: transform 0.3s ease-in-out, width 0.3s ease-in-out;
  z-index: 1;
}

/* 输入框容器样式 */
.amount-wrapper,
.remarks-wrapper,
.date-picker-wrapper {
  align-items: center;
  padding: 0;
  background: transparent;
}

/* 输入框图标统一样式 */
.amount-icon,
.tips-icon,
.date-icon {
  position: absolute;
  left: 12px;
  font-size: 1.2rem;
  color: #888;
  pointer-events: none;
}

/* 错误信息样式 */
.error-message {
  font-size: 0.85rem;
  font-weight: bold;
  letter-spacing: 0.5px;
  font-family: 'Poppins', 'PingFang SC', 'Helvetica Neue', sans-serif;
  color: var(--text-main);
  text-shadow: 0 1px 1px rgba(0,0,0,0.5);
  transition: color 0.3s ease;
  text-align: left;
}

@media (max-width: 500px) {
  .form-card {
    padding: 1.5rem;
    margin: 0 1rem;
  }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes float {
  0% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
  100% { transform: translateY(0); }
}
</style>

  
