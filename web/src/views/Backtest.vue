<template>
  <div class="backtest">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>策略推演</span>
        </div>
      </template>
      
      <el-form :inline="true" :model="backtestForm" label-width="100px">
        <el-form-item label="ETF代码">
          <el-input v-model="backtestForm.code" placeholder="输入ETF代码（如510300）" style="width: 200px" />
        </el-form-item>
        <el-form-item label="策略类型">
          <el-select v-model="backtestForm.strategyType" placeholder="选择策略" style="width: 150px" @change="handleStrategyTypeChange">
            <el-option label="MACD策略" value="macd" />
            <el-option label="布林带策略" value="bollinger" />
            <el-option label="组合策略" value="combined" />
          </el-select>
        </el-form-item>
        <el-form-item label="策略子类型">
          <el-select v-model="backtestForm.strategySubtype" placeholder="选择子策略" style="width: 150px">
            <el-option v-for="(name, subtype) in strategies[backtestForm.strategyType]?.subtypes || {}" :key="subtype" :label="name" :value="subtype" />
          </el-select>
        </el-form-item>
        <el-form-item label="推演年限">
          <el-select v-model="backtestForm.years" placeholder="选择年限" style="width: 120px">
            <el-option label="1年" :value="1" />
            <el-option label="3年" :value="3" />
            <el-option label="5年" :value="5" />
            <el-option label="10年" :value="10" />
          </el-select>
        </el-form-item>
        <el-form-item label="初始资金">
          <el-input-number v-model="backtestForm.initialCash" :min="10000" :step="10000" style="width: 150px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="startBacktest" :loading="backtestLoading" :disabled="backtestRunning">
            {{ backtestRunning ? '推演中...' : '开始推演' }}
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>

      <el-progress v-if="backtestRunning" :percentage="backtestProgress" :status="backtestProgressStatus" style="margin: 20px 0">
        <span>{{ backtestMessage }}</span>
      </el-progress>

      <el-divider v-if="backtestResult" />

      <div v-if="backtestResult" class="backtest-results">
        <el-descriptions title="回测结果" :column="2" border>
          <el-descriptions-item label="初始资金">{{ backtestResult.initial_cash?.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="最终价值">{{ backtestResult.final_value?.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="收获金额">
            <span :style="{ color: (backtestResult.final_value - backtestResult.initial_cash) >= 0 ? 'green' : 'red' }">
              {{ (backtestResult.final_value - backtestResult.initial_cash)?.toFixed(2) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="总收益率">
            <span :style="{ color: backtestResult.total_return >= 0 ? 'green' : 'red' }">
              {{ (backtestResult.total_return * 100)?.toFixed(2) }}%
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="最大回撤率">
            <span style="color: red">
              {{ (backtestResult.max_drawdown * 100)?.toFixed(2) }}%
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="最大回撤金额">
            <span style="color: red">
              {{ backtestResult.max_drawdown_money?.toFixed(2) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="夏普比率">
            <span :style="{ color: backtestResult.sharpe_ratio >= 1 ? 'green' : 'orange' }">
              {{ backtestResult.sharpe_ratio?.toFixed(4) || '-' }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="交易总次数">{{ backtestResult.total_trades }}</el-descriptions-item>
          <el-descriptions-item label="盈利次数">{{ backtestResult.won_trades }}</el-descriptions-item>
          <el-descriptions-item label="亏损次数">{{ backtestResult.lost_trades }}</el-descriptions-item>
          <el-descriptions-item label="胜率">
            <span :style="{ color: backtestResult.win_rate >= 0.5 ? 'green' : 'orange' }">
              {{ (backtestResult.win_rate * 100)?.toFixed(2) }}%
            </span>
          </el-descriptions-item>
        </el-descriptions>

        <el-alert
          :title="getBacktestRating()"
          :type="getBacktestRatingType()"
          :closable="false"
          style="margin-top: 20px"
        />
      </div>
    </el-card>

    <el-card v-if="backtestResult && backtestResult.trades_list && backtestResult.trades_list.length > 0" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>交易明细</span>
          <el-tag type="info">{{ backtestResult.trades_list.length }} 笔交易</el-tag>
        </div>
      </template>
      
      <el-table :data="backtestResult.trades_list" style="width: 100%" table-layout="auto">
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="buy_date" label="买入日期" width="120" />
        <el-table-column prop="buy_price" label="买入价格" width="100" :formatter="formatPrice" />
        <el-table-column prop="buy_value" label="买入金额" width="120" :formatter="formatPrice" />
        <el-table-column prop="sell_date" label="卖出日期" width="120" />
        <el-table-column prop="sell_price" label="卖出价格" width="100" :formatter="formatPrice" />
        <el-table-column prop="sell_value" label="卖出金额" width="120" :formatter="formatPrice" />
        <el-table-column prop="profit" label="盈亏金额" width="120">
          <template #default="{ row }">
            <span :style="{ color: row.profit >= 0 ? 'green' : 'red' }">
              {{ row.profit.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_pct" label="盈亏比例" width="120">
          <template #default="{ row }">
            <span :style="{ color: row.profit_pct >= 0 ? 'green' : 'red' }">
              {{ row.profit_pct.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="数量" width="100" :formatter="formatNumber" />
      </el-table>
    </el-card>

    <el-card v-if="backtestResult" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>策略说明</span>
        </div>
      </template>
      <div class="strategy-description">
        <p><strong>{{ strategies[backtestForm.strategyType]?.name }}</strong> - {{ strategies[backtestForm.strategyType]?.subtypes?.[backtestForm.strategySubtype] }}</p>
        <p v-html="getStrategyDescription()"></p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { backtestAPI } from '@/api/endpoints'
import { ElMessage } from 'element-plus'

const backtestForm = ref({
  code: '510300',
  strategyType: 'combined',
  strategySubtype: 'standard',
  years: 10,
  initialCash: 100000
})

const strategies = ref({})
const backtestLoading = ref(false)
const backtestRunning = ref(false)
const backtestProgress = ref(0)
const backtestProgressStatus = ref('success')
const backtestMessage = ref('')
const backtestResult = ref(null)

let progressTimer = null

const loadStrategies = async () => {
  try {
    const response = await backtestAPI.getStrategies()
    if (response.success) {
      strategies.value = response.data
    }
  } catch (error) {
    console.error('加载策略列表失败:', error)
  }
}

const handleStrategyTypeChange = () => {
  const subtypes = strategies.value[backtestForm.value.strategyType]?.subtypes || {}
  backtestForm.value.strategySubtype = Object.keys(subtypes)[0]
}

const startBacktest = async () => {
  if (!backtestForm.value.code) {
    ElMessage.warning('请输入ETF代码')
    return
  }

  backtestLoading.value = true
  backtestRunning.value = true
  backtestProgress.value = 0
  backtestMessage.value = '正在创建回测任务...'
  backtestResult.value = null
  
  try {
    const endDate = new Date()
    const startDate = new Date()
    startDate.setFullYear(startDate.getFullYear() - backtestForm.value.years)
    
    const startDateStr = `${startDate.getFullYear()}${String(startDate.getMonth() + 1).padStart(2, '0')}${String(startDate.getDate()).padStart(2, '0')}`
    
    const response = await backtestAPI.run({
      code: backtestForm.value.code,
      strategy_type: backtestForm.value.strategyType,
      strategy_subtype: backtestForm.value.strategySubtype,
      start_date: startDateStr,
      initial_cash: backtestForm.value.initialCash
    })
    
    if (response.success && response.data.task_id) {
      const taskId = response.data.task_id
      pollProgress(taskId)
    }
  } catch (error) {
    console.error('创建回测任务失败:', error)
    ElMessage.error('创建回测任务失败')
    backtestRunning.value = false
  } finally {
    backtestLoading.value = false
  }
}

const pollProgress = async (taskId) => {
  progressTimer = setInterval(async () => {
    try {
      const response = await backtestAPI.getProgress(taskId)
      
      if (response.success) {
        const data = response.data
        backtestProgress.value = data.progress
        backtestMessage.value = data.message
        
        if (data.status === 'completed') {
          clearInterval(progressTimer)
          backtestRunning.value = false
          backtestResult.value = data.result
          backtestProgressStatus.value = 'success'
          backtestMessage.value = '推演完成'
          ElMessage.success('策略推演完成')
        } else if (data.status === 'failed') {
          clearInterval(progressTimer)
          backtestRunning.value = false
          backtestProgressStatus.value = 'exception'
          backtestMessage.value = `推演失败: ${data.error}`
          ElMessage.error(`推演失败: ${data.error}`)
        }
      }
    } catch (error) {
      console.error('查询进度失败:', error)
      clearInterval(progressTimer)
      backtestRunning.value = false
      backtestProgressStatus.value = 'exception'
      backtestMessage.value = '查询进度失败'
    }
  }, 1000)
}

const resetForm = () => {
  backtestForm.value = {
    code: '510300',
    strategyType: 'combined',
    strategySubtype: 'standard',
    years: 10,
    initialCash: 100000
  }
  backtestResult.value = null
  backtestProgress.value = 0
  backtestMessage.value = ''
  if (progressTimer) {
    clearInterval(progressTimer)
  }
  backtestRunning.value = false
}

const getBacktestRating = () => {
  if (!backtestResult.value) return ''
  
  const profit = backtestResult.value.final_value - backtestResult.value.initial_cash
  const returnRate = backtestResult.value.total_return * 100
  const winRate = backtestResult.value.win_rate * 100
  
  if (profit > 0 && returnRate > 10 && winRate > 50) {
    return '🎉 优秀：收益良好且胜率高'
  } else if (profit > 0 && returnRate > 5) {
    return '✓ 良好：策略有效，表现稳健'
  } else if (profit > 0) {
    return '➕ 及格：小幅盈利，需优化参数'
  } else if (profit > -5000) {
    return '⚠ 一般：小幅亏损，需调整策略'
  } else {
    return '❌ 较差：策略在此时期表现不佳'
  }
}

const getBacktestRatingType = () => {
  if (!backtestResult.value) return 'info'
  
  const profit = backtestResult.value.final_value - backtestResult.value.initial_cash
  
  if (profit > 0) {
    return 'success'
  } else if (profit > -5000) {
    return 'warning'
  } else {
    return 'error'
  }
}

const getStrategyDescription = () => {
  const descriptions = {
    'macd': {
      'basic': 'MACD金叉买入（快线上穿慢线），死叉卖出（快线下穿慢线）',
      'enhanced': 'MACD金叉买入，死叉卖出，可添加成交量确认'
    },
    'bollinger': {
      'breakthrough': '价格突破布林带上轨时买入，跌破下轨或止盈止损时卖出',
      'mean_reversion': '价格触及布林带下轨附近时买入，触及上轨附近时卖出',
      'squeeze': '布林带收缩后价格向上突破时买入，跌破趋势线时卖出'
    },
    'combined': {
      'standard': 'MACD金叉 + 价格在布林带中轨之上时买入，MACD死叉或价格低于下轨时卖出',
      'aggressive': '布林带收缩 + MACD金叉 + 价格高于趋势线时买入',
      'conservative': 'MACD金叉 + MACD>0 + 均线多头排列 + RSI在30-70之间时买入，多重条件确认'
    }
  }
  
  return descriptions[backtestForm.value.strategyType]?.[backtestForm.value.strategySubtype] || ''
}

const formatPrice = (row, column, cellValue) => {
  if (cellValue === null || cellValue === undefined) {
    return '-'
  }
  return Number(cellValue).toFixed(3)
}

const formatNumber = (row, column, cellValue) => {
  if (cellValue === null || cellValue === undefined) {
    return '-'
  }
  return Number(cellValue).toFixed(0)
}

onMounted(() => {
  loadStrategies()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.backtest-results {
  margin-top: 20px;
}

.backtest-results .el-descriptions {
  margin-top: 20px;
}

.strategy-description {
  line-height: 1.8;
}

.strategy-description p {
  margin: 10px 0;
}
</style>
