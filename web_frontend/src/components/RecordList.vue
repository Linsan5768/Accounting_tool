<template>
  <div class="container">
    <div class="record-card">
      <img src="@/assets/image3.png" alt="插图" class="welcome-image" />
      <h2 class="card-title">历史记录</h2>
      
      <!-- 表格区域 -->
      <div class="table-container">
        <table class="record-table">
          <thead>
            <tr class="table-row">
              <th class="table-cell cell-date">日期</th>
              <th class="table-cell cell-amount">金额</th>
              <th class="table-cell cell-category">类别</th>
              <th class="table-cell cell-remarks">备注</th>
              <th class="table-cell cell-action">
                <button class="filter-btn" @click="toggleBottomSheet('filter')">
                  <span class="filter-icon">⚙</span> 筛选
                </button>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in filteredRecords" :key="record.id" class="table-row">
              <td class="table-cell cell-date">{{ record.date }}</td>
              <td class="table-cell cell-amount" :class="{'negative': record.amount < 0, 'positive': record.amount >= 0}">
                {{ record.amount.toFixed(2) }} 元
              </td>
              <td class="table-cell cell-category">{{ record.category }}</td>
              <td class="table-cell cell-remarks">{{ record.remarks }}</td>
              <td class="table-cell cell-action">
                <button class="edit-btn" @click="editRecord(record)">✎</button>
                <button class="delete-btn" @click="deleteRecord(record.id)">⌫</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 底部弹窗 -->
      <transition name="slide-up" appear>
        <div v-if="showBottomSheet" class="bottom-sheet">
          <div class="sheet-header">
            <button class="complete-btn" @click="applySearchSettings">✓</button>
            <div class="header-center">
              <button 
                :class="['filter-tab-btn', { active: currentSheet === 'date' }]" 
                @click="switchFilterType('date')">
                日期
              </button>
              <button 
                :class="['filter-tab-btn', { active: currentSheet === 'amount' }]" 
                @click="switchFilterType('amount')">
                金额
              </button>
              <button 
                :class="['filter-tab-btn', { active: currentSheet === 'category' }]" 
                @click="switchFilterType('category')">
                类别
              </button>
            </div>
            <div class="header-right">
              <button class="reset-btn" @click="resetFilterSettings">↻</button>
              <button class="cancel-btn" @click="toggleBottomSheet()">⊗</button>
            </div>
          </div>
          
          <!-- 内容容器，带过渡效果 -->
          <div class="content-wrapper">
            <!-- 日期筛选内容 -->
            <transition name="slide-horizontal">
              <div v-if="currentSheet === 'date'" class="sheet-content" key="date">
                <h3>请选择日期筛选</h3>
                <div class="date-filter-container">
                  <button 
                    :class="{ selected: tempSearchType === 'day' }" 
                    @click="selectSearchType('day')"
                    class="date-filter-btn">
                    按单日
                  </button>
                  <button 
                    :class="{ selected: tempSearchType === 'range' }" 
                    @click="selectSearchType('range')"
                    class="date-filter-btn">
                    按时间段
                  </button>
                  <button 
                    :class="{ selected: tempSearchType === 'month' }" 
                    @click="selectSearchType('month')"
                    class="date-filter-btn">
                    按年月
                  </button>
                </div>
                <div class="sheet-inputs">
                  <div v-if="tempSearchType === 'day'" class="input-group">
                    <input type="date" id="sheet-single-date" v-model="tempSingleDate" class="centered-date-input" />
                  </div>
                  <div v-else-if="tempSearchType === 'range'" class="input-group">
                    <div class="range-wrapper">
                      <input type="date" id="sheet-start-date" v-model="tempStartDate" class="centered-date-input" />
                      <span class="range-arrow">→</span>
                      <input type="date" id="sheet-end-date" v-model="tempEndDate" class="centered-date-input" />
                    </div>
                  </div>
                  <div v-else-if="tempSearchType === 'month'" class="input-group">
                    <input type="month" id="sheet-month" v-model="tempFilterMonth" class="centered-date-input" />
                  </div>
                </div>
              </div>
            </transition>
            
            <!-- 金额筛选内容 -->
            <transition name="slide-horizontal">
              <div v-if="currentSheet === 'amount'" class="sheet-content" key="amount">
                <h3>请选择金额筛选条件</h3>
                <div class="sheet-options amount-options">
                  <button :class="{ selected: tempAmountFilter === 'income' }" @click="selectAmountFilter('income')">
                    <span class="option-icon">↑</span>收入
                  </button>
                  <button :class="{ selected: tempAmountFilter === 'expense' }" @click="selectAmountFilter('expense')">
                    <span class="option-icon">↓</span>支出
                  </button>
                  <button :class="{ selected: tempAmountFilter === 'all' }" @click="selectAmountFilter('all')">
                    <span class="option-icon">⇅</span>全部
                  </button>
                </div>
              </div>
            </transition>
            
            <!-- 类别筛选内容 -->
            <transition name="slide-horizontal">
              <div v-if="currentSheet === 'category'" class="sheet-content" key="category">
                <h3>按类别筛选</h3>
                <div class="category-container">
                  <button 
                    :class="{ selected: tempCategoryFilter === '' }" 
                    @click="selectCategoryFilter('')"
                    class="category-btn all-btn">
                    <span class="all-btn-icon">☰</span>
                    显示全部类别
                  </button>
                  <div class="category-grid">
                    <button 
                      v-for="category in categories" 
                      :key="category"
                      :class="{ selected: tempCategoryFilter === category }" 
                      @click="selectCategoryFilter(category)"
                      class="category-btn">
                      {{ category }}
                    </button>
                  </div>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </transition>
      
      <!-- 编辑记录弹窗 -->
      <transition name="fade">
        <div v-if="showEditModal" class="modal-overlay">
          <div class="edit-modal">
            <h3>编辑记录</h3>
            <form @submit.prevent="updateRecord">
              <div class="form-group">
                <label for="edit-date">日期:</label>
                <input 
                  type="date" 
                  id="edit-date" 
                  v-model="editingRecord.date" 
                  class="edit-input"
                  required
                />
              </div>
              <div class="form-group">
                <label for="edit-amount">金额:</label>
                <input 
                  type="number" 
                  id="edit-amount" 
                  v-model="editingRecord.amount" 
                  class="edit-input"
                  step="0.01"
                  required
                />
              </div>
              <div class="form-group">
                <label for="edit-category">类别:</label>
                <select id="edit-category" v-model="editingRecord.category" class="edit-input">
                  <option v-for="category in categories" :key="category" :value="category">
                    {{ category }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label for="edit-remarks">备注:</label>
                <input 
                  type="text" 
                  id="edit-remarks" 
                  v-model="editingRecord.remarks" 
                  class="edit-input"
                />
              </div>
              <div class="edit-actions">
                <button type="button" class="cancel-edit-btn" @click="cancelEdit">取消</button>
                <button type="submit" class="save-btn">保存</button>
              </div>
            </form>
          </div>
        </div>
      </transition>
      
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: "RecordList",
  data() {
    return {
      records: [],
      // 日期筛选相关变量
      searchType: 'month',
      singleDate: '',
      startDate: '',
      endDate: '',
      filterMonth: '',
      tempSearchType: 'month',
      tempSingleDate: '',
      tempStartDate: '',
      tempEndDate: '',
      tempFilterMonth: '',
      // 金额筛选相关变量
      amountFilter: 'all', // 'income'、'expense'、'all'
      tempAmountFilter: 'all',
      // 类别筛选相关变量
      categoryFilter: '',
      tempCategoryFilter: '',
      categories: [],
      // 底部弹窗控制
      showBottomSheet: false,
      currentSheet: 'date',  // 'date'、'amount' 或 'category'
      previousSheet: '',  // 记录上一个选择的类型，用于动画方向判断
      // 编辑记录相关变量
      showEditModal: false,
      editingRecord: {
        id: null,
        date: '',
        amount: 0,
        category: '',
        remarks: ''
      }
    }
  },
  created() {
    this.fetchRecords();
  },
  computed: {
    filteredRecords() {
      let filtered = this.records.filter(record => {
        const recordDate = record.date;
        let dateMatch = true;
        // 日期筛选
        if(this.searchType === 'day' && this.singleDate) {
          dateMatch = recordDate === this.singleDate;
        } else if(this.searchType === 'range') {
          if(this.startDate && this.endDate) {
            dateMatch = recordDate >= this.startDate && recordDate <= this.endDate;
          } else if(this.startDate) {
            dateMatch = recordDate >= this.startDate;
          } else if(this.endDate) {
            dateMatch = recordDate <= this.endDate;
          }
        } else if(this.searchType === 'month' && this.filterMonth) {
          dateMatch = recordDate.startsWith(this.filterMonth);
        }
        
        // 类别筛选
        let categoryMatch = true;
        if (this.categoryFilter) {
          categoryMatch = record.category === this.categoryFilter;
        }
        
        return dateMatch && categoryMatch;
      });
      
      // 金额筛选
      if(this.amountFilter === 'income') {
        filtered = filtered.filter(record => record.amount >= 0);
      } else if(this.amountFilter === 'expense') {
        filtered = filtered.filter(record => record.amount < 0);
      }
      
      filtered.sort((a, b) => new Date(a.date) - new Date(b.date));
      return filtered;
    }
  },
  methods: {
    async fetchRecords() {
      try {
        const response = await axios.get('http://localhost:5002/api/get_records');
        this.records = response.data;
        const catSet = new Set();
        response.data.forEach(record => {
          if (record.category) {
            catSet.add(record.category);
          }
        });
        this.categories = Array.from(catSet);
      } catch (error) {
        alert('获取记录失败：' + (error.response ? error.response.data.error : error.message));
      }
    },
    async deleteRecord(recordId) {
      try {
        await axios.delete(`http://localhost:5002/api/delete_record/${recordId}`);
        this.records = this.records.filter(record => record.id !== recordId);
        window.alert("记录删除成功！");
      } catch (error) {
        window.alert("删除失败：" + (error.response ? error.response.data.error : error.message));
      }
    },
    // 切换底部弹窗
    toggleBottomSheet(type) {
      if (type) {
        if (this.showBottomSheet) {
          // 已经打开，切换到默认筛选类型
          this.previousSheet = this.currentSheet;
          this.currentSheet = 'date';
        } else {
          // 新打开
          this.previousSheet = '';
          this.currentSheet = 'date';
          this.showBottomSheet = true;
        }
        
        // 初始化临时值
        this.initTempValues();
      } else {
        // 关闭窗口
        this.showBottomSheet = false;
      }
    },
    // 切换筛选类型
    switchFilterType(type) {
      if (type !== this.currentSheet) {
        this.previousSheet = this.currentSheet;
        this.currentSheet = type;
        this.initTempValues();
      }
    },
    // 初始化临时值
    initTempValues() {
      if (this.currentSheet === 'date') {
        this.tempSearchType = this.searchType;
        this.tempSingleDate = this.singleDate;
        this.tempStartDate = this.startDate;
        this.tempEndDate = this.endDate;
        this.tempFilterMonth = this.filterMonth;
      } else if (this.currentSheet === 'amount') {
        this.tempAmountFilter = this.amountFilter;
      } else if (this.currentSheet === 'category') {
        this.tempCategoryFilter = this.categoryFilter;
      }
    },
    // 重置所有筛选设置
    resetFilterSettings() {
      // 重置所有筛选条件，不仅限于当前标签页的筛选条件
      // 日期筛选
      this.tempSearchType = '';
      this.tempSingleDate = '';
      this.tempStartDate = '';
      this.tempEndDate = '';
      this.tempFilterMonth = '';
      // 金额筛选
      this.tempAmountFilter = 'all';
      // 类别筛选
      this.tempCategoryFilter = '';
    },
    // 应用筛选设置
    applySearchSettings() {
      // 应用日期筛选设置
      if (this.currentSheet === 'date') {
        this.searchType = this.tempSearchType;
        if (this.searchType === 'day') {
          this.singleDate = this.tempSingleDate;
          this.startDate = '';
          this.endDate = '';
          this.filterMonth = '';
        } else if (this.searchType === 'range') {
          this.startDate = this.tempStartDate;
          this.endDate = this.tempEndDate;
          this.singleDate = '';
          this.filterMonth = '';
        } else if (this.searchType === 'month') {
          this.filterMonth = this.tempFilterMonth;
          this.singleDate = '';
          this.startDate = '';
          this.endDate = '';
        }
      } 
      // 应用金额筛选设置
      else if (this.currentSheet === 'amount') {
        this.amountFilter = this.tempAmountFilter;
      }
      // 应用类别筛选设置
      else if (this.currentSheet === 'category') {
        this.categoryFilter = this.tempCategoryFilter;
      }
      
      this.showBottomSheet = false;
    },
    // 日期筛选相关方法
    selectSearchType(type) {
      this.tempSearchType = type;
    },
    // 金额筛选相关方法
    selectAmountFilter(type) {
      this.tempAmountFilter = type;
    },
    // 类别筛选相关方法
    selectCategoryFilter(category) {
      this.tempCategoryFilter = category;
    },
    // 编辑记录相关方法
    editRecord(record) {
      this.editingRecord = { ...record };
      this.showEditModal = true;
    },
    cancelEdit() {
      this.showEditModal = false;
      this.editingRecord = {
        id: null,
        date: '',
        amount: 0,
        category: '',
        remarks: ''
      };
    },
    async updateRecord() {
      try {
        console.log("正在提交编辑请求:", this.editingRecord);
        
        // 确保日期格式正确
        if (!this.editingRecord.date || typeof this.editingRecord.date !== 'string') {
          throw new Error("日期格式不正确");
        }
        
        // 确保金额为数字
        const amount = parseFloat(this.editingRecord.amount);
        if (isNaN(amount)) {
          throw new Error("金额必须是有效数字");
        }
        
        const response = await axios.put(`http://localhost:5002/api/update_record/${this.editingRecord.id}`, {
          date: this.editingRecord.date,
          amount: amount,
          category: this.editingRecord.category,
          remarks: this.editingRecord.remarks || ""
        });
        
        console.log("更新成功，服务器返回:", response.data);
        
        // 更新本地记录
        const index = this.records.findIndex(r => r.id === this.editingRecord.id);
        if (index !== -1) {
          this.records[index] = { ...this.editingRecord };
        }
        
        // 关闭模态框
        this.showEditModal = false;
        window.alert("记录更新成功！");
        
        // 刷新数据
        this.fetchRecords();
      } catch (error) {
        console.error("更新失败:", error);
        let errorMessage = "更新失败";
        
        if (error.response) {
          console.error("服务器返回错误:", error.response.data);
          errorMessage += ": " + (error.response.data.error || JSON.stringify(error.response.data));
        } else if (error.request) {
          console.error("请求未收到响应:", error.request);
          errorMessage += ": 服务器未响应，请检查网络连接";
        } else {
          console.error("请求配置错误:", error.message);
          errorMessage += ": " + error.message;
        }
        
        window.alert(errorMessage);
      }
    }
  }
}
</script>

<style>
html, body {
  height: 100%;
  margin: 0;
  overflow: hidden;
  font-family: 'Poppins', 'PingFang SC', 'Helvetica Neue', sans-serif;
  background: #ffffff;
}

.container {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--bg-base);
}

.record-card {
  background: var(--bg-card);
  padding: 3rem 2.5rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.8);
  text-align: center;
  width: 800px;
  height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  position: relative;
  transition: all 0.4s ease;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 筛选按钮样式 */
.filter-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary);
  color: var(--text-main);
  border: none;
  padding: 6px 12px;
  margin-left: 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: var(--box-shadow);
  font-family: 'PingFang SC', 'Helvetica Neue', sans-serif;
}

.filter-btn:hover {
  background-color: var(--primary-hover);
  box-shadow: var(--slected-bt);
  transform: translateY(-2px);
}

.filter-icon {
  margin-right: 5px;
  font-size: 1rem;
}

/* 底部弹窗样式 */
.bottom-sheet {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 40%;  /* 降低高度，减少空旷感 */
  background: var(--menu);
  backdrop-filter: blur(10px); /* 增加模糊效果 */
  -webkit-backdrop-filter: blur(10px);
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
  padding: 1.5rem 1rem 1rem;
  will-change: transform, opacity;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  box-shadow: 0 -5px 20px rgba(0,0,0,0.15); /* 添加上方阴影 */
  border-top: 1px solid rgba(255,255,255,0.1); /* 添加细微边框 */
}

/* 内容包装器，用于控制内部元素的动画 */
.content-wrapper {
  position: relative;
  width: 100%;
  flex: 1;
  overflow: hidden;
}

/* 弹窗头部样式 */
.sheet-header {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.2rem;
  position: relative;
  border-bottom: 1px solid rgba(0,0,0,0.1); /* 添加分隔线 */
  padding-bottom: 0.8rem;
}

/* 头部中央标签按钮 */
.header-center {
  display: flex;
  gap: 5px;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.filter-tab-btn {
  padding: 6px 12px;
  background: transparent;
  border: none;
  border-radius: 16px;
  color: var(--text-main);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  opacity: 0.7;
  font-family: 'PingFang SC', 'Helvetica Neue', sans-serif;
}

.filter-tab-btn.active {
  background-color: var(--primary);
  color: #000;
  opacity: 1;
  font-weight: 600;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.filter-tab-btn:hover {
  opacity: 1;
}

/* 完成按钮样式 - 圆形 */
.complete-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: #4CAF50; /* 绿色 */
  color: white;
  border: none;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(76, 175, 80, 0.4);
  position: absolute;
  left: 10px;
  top: 0px;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  font-size: 0.9rem;
  line-height: 1;
  padding: 0;
}

.complete-btn:hover {
  background-color: #43A047;
  transform: translateY(-2px) scale(1.1);
  box-shadow: 0 4px 10px rgba(76, 175, 80, 0.5);
}

.complete-btn:active {
  transform: translateY(1px) scale(0.95);
  box-shadow: 0 1px 3px rgba(76, 175, 80, 0.3);
}

/* 头部右侧按钮容器 */
.header-right {
  display: flex;
  gap: 8px;
  margin-left: auto;
  margin-right: 10px;
}

/* 重置按钮样式 */
.reset-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: #2196F3; /* 蓝色 */
  color: white;
  border: none;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(33, 150, 243, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.9rem;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  line-height: 1;
  padding: 0;
}

.reset-btn:hover {
  background-color: #1E88E5;
  transform: translateY(-2px) scale(1.1) rotate(90deg);
  box-shadow: 0 4px 10px rgba(33, 150, 243, 0.5);
}

.reset-btn:active {
  transform: translateY(1px) scale(0.95);
  box-shadow: 0 1px 3px rgba(33, 150, 243, 0.3);
}

/* 取消按钮样式 */
.cancel-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: #F44336; /* 红色 */
  color: white;
  border: none;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(244, 67, 54, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.9rem;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  line-height: 1;
  padding: 0;
}

.cancel-btn:hover {
  background-color: #E53935;
  transform: translateY(-2px) scale(1.1) rotate(90deg);
  box-shadow: 0 4px 10px rgba(244, 67, 54, 0.5);
}

.cancel-btn:active {
  transform: translateY(1px) scale(0.95);
  box-shadow: 0 1px 3px rgba(244, 67, 54, 0.3);
}

/* 弹窗内容居中 */
.sheet-content {
  width: 90%;
  max-width: 500px;
  text-align: center;
  font-size: 1.1rem;
  font-weight: 600;
  background: rgba(255,255,255,0.08);
  padding: 1rem;
  border-radius: 12px;
  box-shadow: inset 0 0 8px rgba(0,0,0,0.1);
  margin: 0 auto;
  min-height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
}

/* 类别选项容器 */
.category-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  margin-top: 0.5rem;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
  gap: 12px;
  width: 100%;
  margin-top: 15px;
  padding: 15px;
  background: rgba(255,255,255,0.08);
  border-radius: 12px;
  max-height: 160px;
  overflow-y: auto;
  box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.05);
}

.category-btn {
  margin: 0;
  font-size: 0.95rem;
  padding: 0.6rem 0.4rem;
  border: none;
  border-radius: 8px;
  background-color: var(--primary-hover);
  color: #000;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
  font-family: 'PingFang SC', 'Helvetica Neue', sans-serif;
  font-weight: 500;
  min-width: 60px;
  max-width: 100%;
  height: 36px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  justify-content: center;
  align-items: center;
}

.category-btn:hover {
  transform: translateY(-2px);
  box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.4);
  background-color: var(--primary);
}

.category-btn.selected {
  background-color: var(--primary);
  transform: translateY(2px);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
  font-weight: bold;
}

.category-btn.all-btn {
  background: var(--primary-hover);
  color: var(--text-main);
  margin-bottom: 10px;
  width: 90%;
  max-width: 220px;
  padding: 0.75rem 1.2rem;
  font-weight: 600;
  font-size: 1rem;
  height: auto;
  position: relative;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  border: 2px solid var(--input-border);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--box-shadow);
}

.category-btn.all-btn:hover {
  background: var(--primary);
  transform: translateY(-3px);
  box-shadow: var(--slected-box-shadow);
}

.category-btn.all-btn.selected {
  background: var(--primary);
  transform: translateY(3px);
  box-shadow: inset 0 4px 8px rgba(0, 0, 0, 0.5), 0 1px 2px rgba(0, 0, 0, 0.2);
  border: 2px solid var(--text-subtle);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  font-weight: 700;
  letter-spacing: 0.5px;
  padding-top: 0.85rem;
  padding-bottom: 0.65rem;
}

.dark .category-btn.all-btn {
  background: #555555;
  border-color: #666666;
  color: #e4e4e4;
}

.dark .category-btn.all-btn:hover {
  background: #666666;
  border-color: #777777;
  box-shadow: 0 4px 12px rgba(150, 150, 150, 0.2);
}

.dark .category-btn.all-btn.selected {
  background: #444444;
  border-color: #888888;
  box-shadow: inset 0 3px 6px rgba(0, 0, 0, 0.4);
}

.all-btn-icon {
  font-size: 1.3rem;
  opacity: 0.9;
  transition: all 0.3s ease;
  margin-right: 8px;
}

/* 标题样式 */
.sheet-content h3 {
  margin-top: 0;
  margin-bottom: 0.8rem;
  font-size: 1.2rem;
}

/* 将选项区域设为 flex 容器，实现等距分布 */
.sheet-options {
  display: flex;
  justify-content: space-evenly;
  align-items: center;
  width: 100%;
  margin: 1.5rem 0;
  gap: 12px;
}

.sheet-options button {
  margin: 0;
  font-size: 1rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 8px;
  background-color: var(--primary-hover);
  color: #000;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  min-width: 90px;
  font-family: 'PingFang SC', 'Helvetica Neue', sans-serif;
  font-weight: 500;
  letter-spacing: 0.5px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  flex: 1;
  max-width: 120px;
}

/* 按钮悬停效果 */
.sheet-options button:hover {
  background-color: var(--primary);
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
}

/* 选中状态下，按钮一直保持按下效果 */
.sheet-options button.selected {
  background-color: var(--primary);
  transform: translateY(3px);
  box-shadow: inset 0 4px 8px rgba(0, 0, 0, 0.3), 0 1px 2px rgba(0, 0, 0, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  font-weight: 700;
  padding-top: 0.85rem;
  padding-bottom: 0.65rem;
}

/* 输入区域容器 */
.sheet-inputs {
  margin-top: 1rem;
  width: 100%;
}

.input-group {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

/* 日期输入框样式（居中） */
.centered-date-input {
  background-color: var(--primary);
  border: none;
  border-radius: 8px;
  padding: 0.7rem 1rem; /* 增大内边距 */
  text-align: center;
  color: #000;
  font-size: 1.1rem; /* 增大字体 */
  font-weight: 500;
  box-shadow: var(--box-shadow);
  width: 80%; /* 固定宽度百分比 */
  max-width: 220px; /* 增大最大宽度 */
  min-width: 180px; /* 设置最小宽度 */
  transition: all 0.2s ease;
  font-family: 'Helvetica Neue', 'PingFang SC', sans-serif;
}

.centered-date-input:focus {
  box-shadow: 0 0 0 2px var(--primary-hover);
  outline: none;
  transform: translateY(-2px);
}

/* 如果范围选择的输入框在同一行，并带有箭头提示 */
.range-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 95%;
  padding: 1rem;
  background: rgba(255,255,255,0.08);
  border-radius: 12px;
  box-shadow: inset 0 0 8px rgba(0,0,0,0.05);
  margin: 0 auto;
}

.range-wrapper .centered-date-input {
  width: 45%;
  min-width: 140px; /* 设定最小宽度 */
  margin: 0;
}

.range-arrow {
  font-size: 1.6rem;
  color: var(--text-main);
  margin: 0 1rem;
  opacity: 0.8;
  flex-shrink: 0;
  font-family: 'Avenir', 'Helvetica Neue', sans-serif;
}

/* 滑动动画 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.33, 1, 0.68, 1);
  will-change: transform, opacity;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

.slide-up-enter-to,
.slide-up-leave-from {
  transform: translateY(0);
  opacity: 1;
}

/* 横向切换动画 */
.slide-horizontal-enter-active,
.slide-horizontal-leave-active {
  transition: all 0.35s cubic-bezier(0.33, 1, 0.68, 1);
  will-change: transform, opacity;
  position: absolute;
  width: 90%;
  left: 5%;
}

.slide-horizontal-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-horizontal-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}

/* 表格样式及其他 */
.table-container {
  flex: 1;
  overflow-y: auto;
  border: 1px solid var(--text-color);
  border-radius: 20px;
  box-shadow: var(--box-shadow);
  max-height: calc(100% - 200px);
}
.record-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}
.record-table thead th {
  position: sticky;
  top: 0;
  background: var(--bg-card);
  z-index: 1;
  padding: 1rem;
  border-bottom: 2px solid var(--text-color);
  white-space: normal;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
.record-table th,
.record-table td {
  padding: 1rem;
  text-align: center;
  border-bottom: 1px solid var(--text-color);
  white-space: normal;
  word-wrap: break-word;
  overflow-wrap: break-word;
  font-family: 'PingFang SC', 'Helvetica Neue', sans-serif;
}
.negative {
  color: rgba(255,104,104,0.7);
  font-weight: 600;
}
.positive {
  color: rgba(82,175,82,0.7);
  font-weight: 600;
}
.delete-btn {
  background-color: var(--primary);
  color: var(--text-main);
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
  box-shadow: var(--box-shadow);
}
.delete-btn:hover {
  background-color: var(--primary-hover);
  box-shadow: var(--slected-bt);
}


/* 编辑按钮样式 */
.edit-btn {
  background-color: var(--primary);
  color: var(--text-main);
  border: none;
  padding: 5px 13px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
  box-shadow: var(--box-shadow);
  margin-right: 20px;
}

.edit-btn:hover {
  background-color: var(--primary-hover);
  box-shadow: var(--slected-bt);
}

/* 编辑模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(10px); /* 增加模糊效果 */
  -webkit-backdrop-filter: blur(10px);
  will-change: transform, opacity;
 
}

.edit-modal {
  background-color: var(--bg-card);
  padding: 1.5rem;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  opacity:90%;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  color: var(--text-main);
  backdrop-filter: blur(10px); /* 增加模糊效果 */
  -webkit-backdrop-filter: blur(10px);
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
  padding: 1.5rem 1rem 1rem;
  will-change: transform, opacity;
}

.edit-modal h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  text-align: center;
  font-size: 1.5rem;
}

.form-group {
  margin-bottom: 1.2rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.edit-input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid var(--input-border, #ddd);
  border-radius: 6px;
  background-color: var(--bg-input, #fff);
  color: var(--text-main);
  font-size: 1rem;
  box-sizing: border-box;
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 1.5rem;
}

.cancel-edit-btn {
  background-color: #ccc;
  color: #333;
  border: none;
  padding: 0.8rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
}

.save-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 0.8rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
}

.cancel-edit-btn:hover {
  background-color: #bbb;
}

.save-btn:hover {
  background-color: #45a049;
}



.welcome-image {
  width: 160px;
  margin: 0 auto;
  animation: float 3s ease-in-out infinite;
}
.card-title {
  margin-top: auto;
  font-size: 2rem;
  font-weight: 600;
  text-align: center;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  color: var(--text-main);
  letter-spacing: 5px;
}
@keyframes float {
  0% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
  100% { transform: translateY(0); }
}
:root {
  --font-family: 'PingFang SC', 'Helvetica Neue', 'Segoe UI', sans-serif;
}

.option-icon {
  font-size: 1.2rem;
  opacity: 0.9;
  transition: all 0.3s ease;
  margin-right: 6px;
  display: inline-block;
}

/* 金额筛选按钮特殊样式，使用与金额文本颜色相匹配的样式 */
.amount-options button:nth-child(1) {
  background-color: rgba(82,175,82,0.7);
}

.amount-options button:nth-child(1):hover {
  background-color: rgba(82,175,82,0.9);
  box-shadow: 0 6px 12px rgba(82,175,82,0.4);
}

.amount-options button:nth-child(1).selected {
  background-color: rgba(82,175,82,1);
}

.amount-options button:nth-child(2) {
  background-color: rgba(255,104,104,0.7);
}

.amount-options button:nth-child(2):hover {
  background-color: rgba(255,104,104,0.9);
  box-shadow: 0 6px 12px rgba(255,104,104,0.4);
}

.amount-options button:nth-child(2).selected {
  background-color: rgba(255,104,104,1);
}

.amount-options button:nth-child(3) {
  background-color: var(--primary-hover);
}

.amount-options button:nth-child(3):hover {
  background-color: var(--primary);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
}

.amount-options button:nth-child(3).selected {
  background-color: var(--primary);
}

/* 日期筛选按钮容器 */
.date-filter-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  width: 100%;
  margin-top: 0.7rem;
  gap: 15px;
}

.date-filter-btn {
  background-color: var(--primary-hover);
  color: #000;
  padding: 10px 16px;
  font-weight: 500;
  font-size: 0.95rem;
  border: none;
  border-radius: 6px;
  transition: all 0.2s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  font-family: 'PingFang SC', 'Helvetica Neue', sans-serif;
  flex: 1;
  max-width: 100px;
  height: 40px;
}

.date-filter-btn:hover {
  background-color: var(--primary);
  transform: translateY(-2px);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.3);
}

.date-filter-btn.selected {
  background-color: var(--primary);
  transform: translateY(1px);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3), 0 1px 2px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-weight: 600;
}

/* 暗色主题下的金额筛选按钮样式 */
.dark .amount-options button:nth-child(1) {
  background-color: rgba(82,175,82,0.8);
  color: #ffffff;
}

.dark .amount-options button:nth-child(1):hover {
  background-color: rgba(82,175,82,0.9);
  box-shadow: 0 6px 12px rgba(82,175,82,0.3);
}

.dark .amount-options button:nth-child(1).selected {
  background-color: rgba(82,175,82,1);
}

.dark .amount-options button:nth-child(2) {
  background-color: rgba(255,104,104,0.8);
  color: #ffffff;
}

.dark .amount-options button:nth-child(2):hover {
  background-color: rgba(255,104,104,0.9);
  box-shadow: 0 6px 12px rgba(255,104,104,0.3);
}

.dark .amount-options button:nth-child(2).selected {
  background-color: rgba(255,104,104,1);
}

.dark .amount-options button:nth-child(3) {
  background-color: #666666;
  color: #e4e4e4;
}

.dark .amount-options button:nth-child(3):hover {
  background-color: #777777;
  box-shadow: 0 6px 12px rgba(150, 150, 150, 0.2);
}

.dark .amount-options button:nth-child(3).selected {
  background-color: #555555;
}

/* 暗色主题下的日期筛选按钮样式 */
.dark .date-filter-btn {
  background-color: #666666;
  color: #e4e4e4;
  border-color: #777777;
}

.dark .date-filter-btn:hover {
  background-color: #777777;
  box-shadow: 0 3px 6px rgba(150, 150, 150, 0.2);
}

.dark .date-filter-btn.selected {
  background-color: #555555;
  border-color: #888888;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
}



/* 淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

</style>