<template>
  <div class="container">
    
    <div class="stats-card">
      <!-- 标题部分 -->
      <div class="header-section">
        <h2 class="card-title">📊 统计分析</h2>
      </div>

      <!-- 日期和时间范围选择 -->
      <div class="controls-section">
        <div class="form-group">
          <div class="date-picker-wrapper">
            <div class="date-icon-container">
              <span class="date-icon">📅</span>
            </div>
            <input 
              v-if="dateType === 'month'"
              type="month" 
              id="month" 
              v-model="selectedMonth" 
              @change="handleMonthChange" 
              class="form-control"
            />
            <input 
              v-if="dateType === 'week'"
              type="week" 
              id="week" 
              v-model="selectedWeek" 
              @change="handleWeekChange" 
              class="form-control"
            />
          </div>
        </div>
        <!-- 显示当前选择的日期范围 -->
        <div class="date-range-display" v-if="dateType === 'week' && selectedWeek">
          <span>{{ formatWeekRange(selectedWeek) }}</span>
        </div>
        <!-- 月份/周切换按钮 -->
        <div class="date-type-toggle">
          <button 
            class="date-type-btn" 
            :class="{ active: dateType === 'month' }" 
            @click="setDateType('month')"
          >
            按月查看
          </button>
          <button 
            class="date-type-btn" 
            :class="{ active: dateType === 'week' }"
            @click="setDateType('week')"
          >
            按周查看
          </button>
        </div>
      </div>

      <!-- 汇总信息卡片 -->
      <div class="summary-section">
        <div class="summary-cards">
          <div class="summary-card income" @click="highlightIncome">
            <div class="card-icon">💰</div>
            <div class="card-content">
              <div class="card-label">总收入</div>
              <div class="card-value">
                <span class="currency">¥</span>
                <span v-if="isLoading">--</span>
                <span v-else>{{ totalIncome.toFixed(2) }}</span>
              </div>
            </div>
            <div class="card-highlight" :class="{ active: highlightedSection === 'income' }"></div>
          </div>
          <div class="summary-card expense" @click="highlightExpense">
            <div class="card-icon">💸</div>
            <div class="card-content">
              <div class="card-label">总支出</div>
              <div class="card-value">
                <span class="currency">¥</span>
                <span v-if="isLoading">--</span>
                <span v-else>{{ totalExpense.toFixed(2) }}</span>
              </div>
            </div>
            <div class="card-highlight" :class="{ active: highlightedSection === 'expense' }"></div>
          </div>
          <div class="summary-card balance" 
               :class="{'positive': remainingMoney >= 0, 'negative': remainingMoney < 0}"
               @click="resetHighlight">
            <div class="card-icon">📊</div>
            <div class="card-content">
              <div class="card-label">结余</div>
              <div class="card-value">
                <span class="currency">¥</span>
                <span v-if="isLoading">--</span>
                <span v-else>{{ remainingMoney.toFixed(2) }}</span>
              </div>
            </div>
            <div class="card-highlight" :class="{ active: highlightedSection === 'none' }"></div>
          </div>
        </div>
        <!-- 把图片放在右侧 -->
      
      </div>

      <!-- 图表容器 -->
      <div class="charts-container" :class="{ 'highlight-income': highlightedSection === 'income', 'highlight-expense': highlightedSection === 'expense' }">
        <transition name="fade" mode="out-in">
          <div v-if="isLoading" class="loading-container">
            <div class="loading-spinner"></div>
            <div class="loading-text">加载数据中...</div>
          </div>
          <div v-else class="charts-wrapper">
            <div class="chart-wrapper income-chart">
              <h3 class="chart-title">收入分布</h3>
              <div class="chart-canvas-container">
                <canvas ref="incomeChart"></canvas>
                <div v-if="!hasIncomeData" class="no-data">暂无收入数据</div>
              </div>
            </div>
            
            <!-- 将图表切换器放到中间 -->
            <div class="centered-chart-toggle">
              <div class="chart-toggle">
                <button 
                  class="toggle-btn" 
                  :class="{ active: chartType === 'pie' }" 
                  @click="setChartType('pie')"
                >
                  饼图
                </button>
                <button 
                  class="toggle-btn" 
                  :class="{ active: chartType === 'bar' }" 
                  @click="setChartType('bar')"
                >
                  柱状图
                </button>
              </div>
            </div>
            
            <div class="chart-wrapper expense-chart">
              <h3 class="chart-title">支出分布</h3>
              <div class="chart-canvas-container">
                <canvas ref="expenseChart"></canvas>
                <div v-if="!hasExpenseData" class="no-data">暂无支出数据</div>
              </div>
            </div>
          </div>
        </transition>
      </div>

      <!-- 分类详情 -->
      <div v-if="selectedCategory" class="category-details">
        <div class="detail-header">
          <h3>{{ selectedCategory.name }} 详情</h3>
          <button class="close-btn" @click="selectedCategory = null">×</button>
        </div>
        <div class="detail-content">
          <div class="detail-amount">{{ selectedCategory.value.toFixed(2) }}元</div>
          <div class="detail-percent">占比 {{ selectedCategory.percent.toFixed(1) }}%</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from "vue";
import Chart from "chart.js/auto";

export default {
  name: "MonthlyStatistics",
  setup() {
    const dateType = ref("month"); // 默认按月份查看
    const selectedMonth = ref("");
    const selectedWeek = ref("");
    const records = ref([]);
    const incomeChart = ref(null);
    const expenseChart = ref(null);
    let incomeChartInstance = null;
    let expenseChartInstance = null;
    const isLoading = ref(false);
    const chartType = ref('pie');
    const highlightedSection = ref('none');
    const selectedCategory = ref(null);
    const hasIncomeData = ref(false);
    const hasExpenseData = ref(false);

    const totalIncome = ref(0);
    const totalExpense = ref(0);
    const remainingMoney = computed(() => totalIncome.value - totalExpense.value);

    const categoryMap = {
      1: "餐饮",
      2: "话费",
      3: "理发",
      4: "交通",
      5: "洗衣",
      6: "超市购物",
      7: "零钱",
      8: "房租",
    };

    // 图表颜色配置
    const chartColors = [
      '#FFB347', // 主题色
      '#FF9B9B',
      '#96CDEF',
      '#9EE09E',
      '#FFA07A',
      '#DDA0DD',
      '#87CEEB',
      '#98FB98'
    ];

    const highlightIncome = () => {
      highlightedSection.value = 'income';
    };

    const highlightExpense = () => {
      highlightedSection.value = 'expense';
    };

    const resetHighlight = () => {
      highlightedSection.value = 'none';
    };

    const setChartType = (type) => {
      if (chartType.value === type) return;
      
      chartType.value = type;
      
      // 销毁现有图表
      if (incomeChartInstance) {
        incomeChartInstance.destroy();
        incomeChartInstance = null;
      }
      if (expenseChartInstance) {
        expenseChartInstance.destroy();
        expenseChartInstance = null;
      }
      
      // 重新渲染图表
      nextTick(() => {
        updateCharts();
      });
    };

    const fetchRecords = async () => {
      isLoading.value = true;
      try {
        const response = await axios.get("http://localhost:5002/api/get_records");
        records.value = response.data;
        setTimeout(() => {
          // 确保DOM已更新
          nextTick(() => {
            updateCharts();
            isLoading.value = false;
          });
        }, 600); // 添加短暂延迟以显示加载动画
      } catch (error) {
        console.error("获取记录失败：" + (error.response ? error.response.data.error : error.message));
        isLoading.value = false;
      }
    };

    const createChart = (chartElement, data, type = 'pie') => {
      if (!chartElement) {
        console.warn('图表容器不存在');
        return null;
      }
      
      const ctx = chartElement.getContext('2d');
      if (!ctx) {
        console.warn('无法获取图表上下文');
        return null;
      }
      
      // 确保Canvas尺寸重置为正方形（对饼图尤其重要）
      if (type === 'pie') {
        const parentWidth = chartElement.parentElement.clientWidth;
        const size = Math.min(parentWidth - 20, 250); // 减去一些边距，保证不超过容器
        chartElement.style.width = `${size}px`;
        chartElement.style.height = `${size}px`;
        chartElement.width = size;
        chartElement.height = size;
      }
      
      // 清除旧的内容
      ctx.clearRect(0, 0, chartElement.width, chartElement.height);
      
      const chartOptions = {
        responsive: true,
        maintainAspectRatio: true, // 保持宽高比
        aspectRatio: 1, // 设置为1，确保为正方形
        animation: {
          duration: 1000,
          easing: 'easeOutQuart'
        },
        plugins: {
          legend: {
            position: type === 'pie' ? 'right' : 'top',
            labels: {
              color: 'var(--text-main)',
              font: {
                size: 12,
                family: "'PingFang SC', 'Helvetica Neue', sans-serif"
              },
              padding: 15,
              usePointStyle: true,
              pointStyle: 'circle'
            },
            // 对于饼图，调整图例到右侧
            ...(type === 'pie' ? {
              align: 'center',
              fullSize: true,
            } : {})
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const label = context.label || '';
                const value = type === 'pie' ? context.parsed : context.parsed.y;
                const total = type === 'pie' 
                  ? context.dataset.data.reduce((a, b) => a + b, 0)
                  : data.values.reduce((a, b) => a + b, 0);
                const percentage = ((value / total) * 100).toFixed(1);
                return `${label}: ${value.toFixed(2)}元 (${percentage}%)`;
              }
            },
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            titleFont: {
              size: 14,
              family: "'PingFang SC', 'Helvetica Neue', sans-serif"
            },
            bodyFont: {
              size: 13,
              family: "'PingFang SC', 'Helvetica Neue', sans-serif"
            },
            padding: 10,
            cornerRadius: 6,
            displayColors: true
          }
        },
        onClick: (event, elements, chart) => {
          if (elements.length > 0) {
            const index = elements[0].index;
            const datasetIndex = elements[0].datasetIndex;
            const value = type === 'pie' 
              ? chart.data.datasets[datasetIndex].data[index]
              : chart.data.datasets[datasetIndex].data[index];
            const name = chart.data.labels[index];
            const total = type === 'pie'
              ? chart.data.datasets[datasetIndex].data.reduce((a, b) => a + b, 0)
              : data.values.reduce((a, b) => a + b, 0);
            const percent = (value / total) * 100;
            
            selectedCategory.value = {
              name,
              value,
              percent
            };
          }
        },
        // 饼图特有设置
        ...(type === 'pie' ? {
          layout: {
            padding: {
              left: 10,
              right: 10,
              top: 0,
              bottom: 0
            }
          },
          cutout: '0%', // 不要中间挖空
          radius: '80%' // 饼图半径占容器的80%
        } : {})
      };

      // 为柱状图添加额外设置
      if (type === 'bar') {
        chartOptions.scales = {
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(200, 200, 200, 0.2)'
            },
            ticks: {
              color: 'var(--text-subtle)',
              font: {
                size: 11
              }
            }
          },
          x: {
            grid: {
              display: false
            },
            ticks: {
              color: 'var(--text-subtle)',
              font: {
                size: 11
              }
            }
          }
        };
        chartOptions.plugins.legend.display = false;
      }

      const config = {
        type: type,
        data: {
          labels: data.labels,
          datasets: type === 'pie' ? [{
            data: data.values,
            backgroundColor: chartColors,
            borderColor: 'rgba(255, 255, 255, 0.8)',
            borderWidth: 2,
            hoverOffset: 15
          }] : [{
            label: '金额',
            data: data.values,
            backgroundColor: chartColors,
            borderRadius: 6,
            maxBarThickness: 40,
            borderColor: 'rgba(255, 255, 255, 0.8)',
            borderWidth: 1
          }]
        },
        options: chartOptions
      };

      try {
        return new Chart(ctx, config);
      } catch (error) {
        console.error('创建图表时出错:', error);
        return null;
      }
    };

    const updateCharts = () => {
      if ((dateType.value === 'month' && !selectedMonth.value) || 
          (dateType.value === 'week' && !selectedWeek.value)) return;

      // 销毁旧实例
      if (incomeChartInstance) {
        incomeChartInstance.destroy();
        incomeChartInstance = null;
      }
      if (expenseChartInstance) {
        expenseChartInstance.destroy();
        expenseChartInstance = null;
      }

      // 根据选择的日期类型过滤数据
      let filtered = [];
      if (dateType.value === 'month' && selectedMonth.value) {
        // 按月份过滤数据
        filtered = records.value.filter(
          (record) => record.date.substring(0, 7) === selectedMonth.value
        );
      } else if (dateType.value === 'week' && selectedWeek.value) {
        // 按周过滤数据 - 格式如 "2023-W12"
        const [year, week] = selectedWeek.value.split('-W');
        // 计算该周的开始和结束日期
        const startDate = getDateOfWeek(parseInt(year), parseInt(week));
        const endDate = new Date(startDate);
        endDate.setDate(startDate.getDate() + 6); // 一周7天
        
        // 根据日期范围过滤
        filtered = records.value.filter((record) => {
          const recordDate = new Date(record.date);
          return recordDate >= startDate && recordDate <= endDate;
        });
      }

      // 初始化数据
      const incomeSums = {};
      const expenseSums = {};
      Object.keys(categoryMap).forEach((id) => {
        incomeSums[id] = 0;
        expenseSums[id] = 0;
      });

      // 计算总额
      totalIncome.value = 0;
      totalExpense.value = 0;
      filtered.forEach((record) => {
        const id = record.category_id;
        if (record.amount >= 0) {
          incomeSums[id] = (incomeSums[id] || 0) + record.amount;
          totalIncome.value += record.amount;
        } else {
          expenseSums[id] = (expenseSums[id] || 0) + Math.abs(record.amount);
          totalExpense.value += Math.abs(record.amount);
        }
      });

      // 准备图表数据
      const incomeData = {
        labels: [],
        values: []
      };
      const expenseData = {
        labels: [],
        values: []
      };

      Object.entries(incomeSums).forEach(([id, sum]) => {
        if (sum > 0) {
          incomeData.labels.push(categoryMap[id] || `类别 ${id}`);
          incomeData.values.push(sum);
        }
      });

      Object.entries(expenseSums).forEach(([id, sum]) => {
        if (sum > 0) {
          expenseData.labels.push(categoryMap[id] || `类别 ${id}`);
          expenseData.values.push(sum);
        }
      });

      hasIncomeData.value = incomeData.values.length > 0;
      hasExpenseData.value = expenseData.values.length > 0;

      // 创建图表 - 确保在DOM完全更新后执行
      nextTick(() => {
        if (hasIncomeData.value && incomeChart.value) {
          incomeChartInstance = createChart(incomeChart.value, incomeData, chartType.value);
        }
        
        if (hasExpenseData.value && expenseChart.value) {
          expenseChartInstance = createChart(expenseChart.value, expenseData, chartType.value);
        }
      });
    };

    const handleMonthChange = () => {
      isLoading.value = true;
      selectedCategory.value = null;
      
      // 销毁旧实例
      if (incomeChartInstance) {
        incomeChartInstance.destroy();
        incomeChartInstance = null;
      }
      if (expenseChartInstance) {
        expenseChartInstance.destroy();
        expenseChartInstance = null;
      }
      
      setTimeout(() => {
        updateCharts();
        isLoading.value = false;
      }, 600);
    };

    const handleWeekChange = () => {
      isLoading.value = true;
      selectedCategory.value = null;
      
      // 销毁旧实例
      if (incomeChartInstance) {
        incomeChartInstance.destroy();
        incomeChartInstance = null;
      }
      if (expenseChartInstance) {
        expenseChartInstance.destroy();
        expenseChartInstance = null;
      }
      
      setTimeout(() => {
        updateCharts();
        isLoading.value = false;
      }, 600);
    };

    const setDateType = (type) => {
      if (type === dateType.value) return; // 如果类型没变，不做处理
      
      dateType.value = type;
      
      // 重新初始化日期
      const now = new Date();
      if (type === 'month') {
        selectedMonth.value = now.toISOString().slice(0, 7);
        handleMonthChange();
      } else if (type === 'week') {
        const currentYear = now.getFullYear();
        const currentWeek = getWeekNumber(now);
        selectedWeek.value = `${currentYear}-W${currentWeek.toString().padStart(2, '0')}`;
        handleWeekChange();
      }
    };

    watch(selectedMonth, () => {
      if (dateType.value === 'month') {
        handleMonthChange();
      }
    });
    
    watch(selectedWeek, () => {
      if (dateType.value === 'week') {
        handleWeekChange();
      }
    });

    onMounted(() => {
      const now = new Date();
      // 设置默认月份
      selectedMonth.value = now.toISOString().slice(0, 7);
      
      // 计算当前周
      const currentYear = now.getFullYear();
      // 使用ISO周数格式 (1-53)
      const currentWeek = getWeekNumber(now);
      selectedWeek.value = `${currentYear}-W${currentWeek.toString().padStart(2, '0')}`;
      
      fetchRecords();
    });

    // 获取日期所在的ISO周数
    const getWeekNumber = (date) => {
      const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
      const dayNum = d.getUTCDay() || 7;
      d.setUTCDate(d.getUTCDate() + 4 - dayNum);
      const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
      return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
    };
    
    // 格式化周范围显示
    const formatWeekRange = (weekString) => {
      if (!weekString) return '';
      
      // 解析周字符串，例如 "2023-W12"
      const [year, week] = weekString.split('-W');
      
      // 计算该周的开始和结束日期
      const startDate = getDateOfWeek(parseInt(year), parseInt(week));
      const endDate = new Date(startDate);
      endDate.setDate(startDate.getDate() + 6); // 一周7天
      
      // 格式化日期显示
      const options = { month: 'short', day: 'numeric' };
      return `${startDate.toLocaleDateString('zh-CN', options)} - ${endDate.toLocaleDateString('zh-CN', options)}`;
    };

    onUnmounted(() => {
      if (incomeChartInstance) {
        incomeChartInstance.destroy();
      }
      if (expenseChartInstance) {
        expenseChartInstance.destroy();
      }
    });

    // 根据年份和周数计算该周的第一天日期（周一）
    const getDateOfWeek = (year, week) => {
      // 计算1月1日是星期几
      const firstDayOfYear = new Date(year, 0, 1);
      // 计算第一个周一的日期
      const firstMonday = new Date(year, 0, 1 + (8 - firstDayOfYear.getDay()) % 7);
      // 计算指定周的周一日期
      const targetDate = new Date(firstMonday);
      targetDate.setDate(firstMonday.getDate() + (week - 1) * 7);
      return targetDate;
    };

    return {
      dateType,
      selectedMonth,
      selectedWeek,
      totalIncome,
      totalExpense,
      remainingMoney,
      incomeChart,
      expenseChart,
      handleMonthChange,
      handleWeekChange,
      isLoading,
      chartType,
      setChartType,
      setDateType,
      highlightedSection,
      highlightIncome,
      highlightExpense,
      resetHighlight,
      selectedCategory,
      hasIncomeData,
      hasExpenseData,
      formatWeekRange
    };
  },
};
</script>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100dvh;
  min-height: 100vh;
  background: var(--bg-base);
  padding: 1rem;
  box-sizing: border-box;
  overflow-x: hidden;
}

.stats-card {
  background: var(--bg-card);
  padding: 1.5rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
  width: 90%;
  max-width: 900px;
  margin: 0 auto;
  animation: fadeIn 0.5s ease;
  position: relative;
  max-height: 92vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.header-section {
  text-align: center;
  margin-bottom: 0.5rem;
}

.controls-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.8rem;
  margin-bottom: 1rem;
  width: 100%;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

/* 汇总和图片并排显示的布局 */
.summary-section {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 0.5rem;
  width: 100%;
  height: 100%;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.8rem;
  flex: 3;
}

.image-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  max-width: 150px;
}

.welcome-image {
  width: 100%;
  max-width: 120px;
  animation: float 3s ease-in-out infinite;
  filter: drop-shadow(0 10px 15px rgba(0, 0, 0, 0.3));
  transition: transform 0.5s ease;
}

.welcome-image:hover {
  transform: scale(1.05) translateY(-5px);
}

.card-title {
  margin: 0.5rem 0;
  font-size: 2rem;
  font-weight: 600;
  text-align: center;
  font-family: "STHupo", "Microsoft YaHei", sans-serif;
  color: var(--text-main);
  letter-spacing: 5px;
  position: relative;
}

.card-title::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 3px;
  background: var(--primary);
  border-radius: 3px;
}

/* 表单组样式 */
.form-group {
  display: flex;
  justify-content: center;
  width: 100%;
}

.date-picker-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: var(--bg-input);
  border-radius: 12px;
  border: 1px solid var(--input-border);
  overflow: hidden;
  box-shadow: var(--box-shadow);
  transition: all 0.3s ease;
  width: 100%;
}

.date-picker-wrapper:hover {
  box-shadow: var(--slected-box-shadow);
  transform: translateY(-2px);
}

.date-picker-wrapper:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(var(--rgb-primary), 0.2);
}

.date-icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 0.8rem;
  background-color: rgba(var(--rgb-primary), 0.08);
  height: 100%;
  border-right: 1px solid rgba(var(--rgb-primary), 0.1);
}

.date-icon {
  font-size: 1.2rem;
}

.date-label {
  position: absolute;
  right: 10px;
  font-size: 0.85rem;
  color: var(--text-subtle);
  pointer-events: none;
}

.form-control {
  flex: 1;
  padding: 0.8rem;
  font-size: 0.95rem;
  border: none;
  background: transparent;
  color: var(--text-main);
  outline: none;
  appearance: none;
  font-family: inherit;
}

.form-control::-webkit-calendar-picker-indicator {
  background-color: transparent;
  cursor: pointer;
  font-size: 1.1rem;
  opacity: 0.7;
  transition: opacity 0.2s ease;
  filter: invert(var(--is-dark, 0));
}

.form-control::-webkit-calendar-picker-indicator:hover {
  opacity: 1;
}

/* 汇总卡片样式 */
.summary-card {
  background: var(--bg-input);
  padding: 1rem;
  border-radius: 12px;
  box-shadow: var(--box-shadow);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.summary-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--slected-box-shadow);
}

.card-icon {
  font-size: 1.5rem;
  margin-right: 0.7rem;
  transition: transform 0.3s ease;
}

.summary-card:hover .card-icon {
  transform: scale(1.1);
}

.card-content {
  flex: 1;
}

.card-label {
  font-size: 0.8rem;
  color: var(--text-subtle);
  margin-bottom: 0.2rem;
  transition: color 0.3s ease;
}

.summary-card:hover .card-label {
  color: var(--text-main);
}

.card-value {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-main);
  display: flex;
  align-items: baseline;
}

.currency {
  font-size: 0.9rem;
  margin-right: 2px;
  opacity: 0.8;
}

.income .card-value {
  color: rgba(82,175,82,0.9);
}

.expense .card-value {
  color: rgba(255,104,104,0.9);
}

.balance.positive .card-value {
  color: rgba(82,175,82,0.9);
}

.balance.negative .card-value {
  color: rgba(255,104,104,0.9);
}

.card-highlight {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: transparent;
  transition: all 0.3s ease;
}

.income .card-highlight.active {
  background: rgba(82,175,82,0.9);
  height: 5px;
}

.expense .card-highlight.active {
  background: rgba(255,104,104,0.9);
  height: 5px;
}

.balance .card-highlight.active {
  background: var(--primary);
  height: 5px;
}

/* 图表切换器 */
.chart-toggle {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
  width: 100%;
}

.centered-chart-toggle {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0 10px;
}

.toggle-btn {
  padding: 0.6rem 1rem;
  background: var(--primary);
  border: 1px solid var(--input-border);
  border-radius: 8px;
  color: var(--text-main);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  text-align: center;
}

.toggle-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.toggle-btn.active {
  background: var(--primary-hover);
  color: #fff;
  font-weight: 600;
  box-shadow: var(--slected-box-shadow);
}

/* 图表容器样式 */
.charts-container {
  position: relative;
  min-height: 50px;
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.charts-wrapper {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  gap: 1rem;
  width: 100%;
  align-items: center;
}

.highlight-income .income-chart {
  transform: scale(1.05);
  box-shadow: var(--slected-box-shadow);
  z-index: 10;
}

.highlight-income .expense-chart {
  opacity: 0.6;
  transform: scale(0.95);
}

.highlight-expense .expense-chart {
  transform: scale(1.05);
  box-shadow: var(--slected-box-shadow);
  z-index: 10;
}

.highlight-expense .income-chart {
  opacity: 0.6;
  transform: scale(0.95);
}

.chart-wrapper {
  background: var(--bg-input);
  padding: 1rem;
  border-radius: 12px;
  box-shadow: var(--box-shadow);
  position: relative;
  transition: all 0.4s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.chart-title {
  text-align: center;
  margin-bottom: 0.8rem;
  color: var(--text-main);
  font-size: 1.1rem;
  font-weight: 600;
  position: relative;
  width: 100%;
}

.chart-title::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 2px;
  background: var(--primary);
  border-radius: 2px;
}

/* 图表canvas容器 */
.chart-canvas-container {
  width: 100%;
  position: relative;
  aspect-ratio: 1/1;
  max-width: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.chart-canvas-container canvas {
  width: 100% !important;
  height: 100% !important;
}

/* 加载动画 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  width: 100%;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 179, 71, 0.3);
  border-radius: 50%;
  border-top-color: var(--primary);
  animation: spin 1s linear infinite;
  margin-bottom: 0.8rem;
}

.loading-text {
  margin-top: 1rem;
  color: var(--text-main);
  font-size: 1rem;
}

/* 无数据提示 */
.no-data {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: var(--text-subtle);
  font-size: 1rem;
  text-align: center;
  background: rgba(0, 0, 0, 0.1);
  padding: 8px 16px;
  border-radius: 8px;
  white-space: nowrap;
}

/* 类别详情弹窗 */
.category-details {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  width: 70%;
  max-width: 350px;
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
  z-index: 100;
  padding: 1.2rem;
  animation: slideUp 0.3s ease;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
  border-bottom: 1px solid var(--input-border);
  padding-bottom: 0.5rem;
}

.detail-header h3 {
  margin: 0;
  color: var(--text-main);
  font-size: 1.1rem;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-main);
  font-size: 1.4rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.detail-content {
  text-align: center;
}

.detail-amount {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 0.4rem;
}

.detail-percent {
  font-size: 1.1rem;
  color: var(--text-subtle);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes float {
  0% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
  100% { transform: translateY(0); }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes slideUp {
  from { transform: translate(-50%, 100%); opacity: 0; }
  to { transform: translate(-50%, 0); opacity: 1; }
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* 滚动条样式 */
.stats-card::-webkit-scrollbar {
  width: 6px;
}

.stats-card::-webkit-scrollbar-track {
  background: rgba(0,0,0,0.05);
  border-radius: 10px;
}

.stats-card::-webkit-scrollbar-thumb {
  background: var(--primary);
  border-radius: 10px;
}

.stats-card::-webkit-scrollbar-thumb:hover {
  background: var(--primary-hover);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-card {
    padding: 1.2rem;
    width: 95%;
    max-height: 92vh;
  }

  .card-title {
    font-size: 1.4rem;
    letter-spacing: 2px;
  }

  /* 移动端将图片和汇总卡片分开 */
  .summary-section {
    flex-direction: column-reverse;
    align-items: center;
  }

  .image-container {
    max-width: 100%;
    margin-bottom: 1rem;
  }

  .welcome-image {
    width: 80px;
  }

  .summary-cards {
    grid-template-columns: 1fr;
    gap: 0.8rem;
    width: 100%;
  }

  .charts-wrapper {
    grid-template-columns: 1fr;
    gap: 1.2rem;
  }

  .chart-canvas-container {
    max-width: 250px;
  }
  
  .category-details {
    width: 90%;
    bottom: 1rem;
  }

  .controls-section {
    flex-direction: column;
  }

  .centered-chart-toggle {
    order: -1;
    margin-bottom: 1rem;
  }
  
  .chart-toggle {
    flex-direction: row;
  }

}

/* 中等屏幕设备 */
@media (min-width: 769px) and (max-width: 1024px) {
  .chart-canvas-container {
    max-width: 280px;
  }
  
  .summary-section {
    gap: 0.6rem;
  }
  
  .summary-card {
    padding: 0.8rem;
  }
  
  .card-icon {
    font-size: 1.4rem;
  }
  
  .card-value {
    font-size: 1.1rem;
  }
}

/* 适应超高分辨率设备 */
@media (min-width: 1400px) {
  .stats-card {
    max-width: 1200px;
  }

  .chart-canvas-container {
    max-width: 350px;
  }

  .image-container {
    max-width: 180px;
  }

  .welcome-image {
    max-width: 150px;
  }
}

.summary-controls {
  width: 100%;
  padding: 0.5rem 0;
  margin-bottom: 0.8rem;
  display: flex;
  justify-content: center;
}

.summary-controls .form-group {
  width: 90%;
  margin: 0 auto;
}

/* 左侧汇总卡片垂直排列 */
.summary-section {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 0.5rem;
  width: 100%;
  height: 100%;
}

/* 日期类型切换按钮 */
.date-type-toggle {
  display: flex;
  justify-content: center;
  margin-top: 0.5rem;
  gap: 0.5rem;
}

.date-type-btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--input-border);
  border-radius: 8px;
  background: var(--bg-input);
  color: var(--text-subtle);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.date-type-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--slected-box-shadow);
  color: var(--text-main);
}

.date-type-btn.active {
  background: rgba(var(--rgb-primary), 0.1);
  color: var(--primary);
  border-color: var(--primary);
  font-weight: 500;
}

/* 日期范围显示 */
.date-range-display {
  text-align: center;
  font-size: 0.9rem;
  color: var(--text-subtle);
  margin-top: -0.4rem;
  margin-bottom: 0.2rem;
  background: rgba(var(--rgb-primary), 0.05);
  padding: 0.3rem 1rem;
  border-radius: 16px;
  display: inline-block;
}

</style>
