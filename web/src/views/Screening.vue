<template>
  <div class="screening">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>策略筛选</span>
        </div>
      </template>
      
      <el-form :inline="true" :model="queryParams">
        <el-form-item label="策略类型">
          <el-select v-model="queryParams.strategyType" placeholder="选择策略" style="width: 150px">
            <el-option label="MACD+布林带" value="combined" />
            <el-option label="MACD" value="macd" />
            <el-option label="布林带" value="bollinger" />
            <el-option label="成交量" value="volume" />
          </el-select>
        </el-form-item>
        <el-form-item label="周期类型">
          <el-select v-model="queryParams.period" placeholder="选择周期" style="width: 120px">
            <el-option label="日线" value="daily" />
            <el-option label="周线" value="weekly" />
          </el-select>
        </el-form-item>
        <el-form-item label="筛选日期">
          <el-date-picker v-model="queryParams.endDate" type="date" placeholder="不填则今天" format="YYYY-MM-DD" value-format="YYYYMMDD" style="width: 150px" />
        </el-form-item>
        <el-form-item label="回溯天数">
          <el-input-number v-model="queryParams.lookbackDays" :min="20" :max="365" style="width: 120px" />
        </el-form-item>
        <el-form-item v-if="queryParams.strategyType === 'combined'">
          <el-checkbox v-model="queryParams.requireMacdGolden">要求MACD金叉</el-checkbox>
        </el-form-item>
        <el-form-item v-if="queryParams.strategyType === 'combined'">
          <el-checkbox v-model="queryParams.requireBbAboveMiddle">价格在布林带中轨之上</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="screen" :loading="loading">筛选</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="displayData" style="width: 100%" v-loading="loading" table-layout="auto" @row-click="handleRowClick">
        <el-table-column prop="code" label="代码" width="100">
          <template #default="{ row }">
            <el-link type="primary" :href="getFundUrl(row.code)" target="_blank" :underline="false" @click.stop>
              {{ row.code }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="200" />
        <el-table-column prop="signal_type" width="200">
          <template #header>
            <div style="display: flex; align-items: center; gap: 8px">
              <span>信号类型</span>
              <el-tooltip placement="top" effect="dark">
                <template #content>
                  <div style="line-height: 1.8; max-width: 300px">
                    <strong>信号类型说明：</strong><br/>
                    • <strong>组合信号</strong>：同时满足MACD金叉 + 价格在布林带中轨之上<br/>
                    • <strong>MACD金叉</strong>：MACD快线上穿信号线，看涨信号<br/>
                    • <strong>MACD死叉</strong>：MACD快线下穿信号线，看跌信号<br/>
                    • <strong>布林带突破上轨</strong>：价格突破布林带上轨<br/>
                    • <strong>布林带突破下轨</strong>：价格跌破布林带下轨<br/>
                    • <strong>布林带收缩</strong>：带宽较窄，可能即将突破<br/>
                    • <strong>高成交量</strong>：成交量异常放大
                  </div>
                </template>
                <el-icon style="cursor: help; color: #909399; font-size: 14px">
                  <QuestionFilled />
                </el-icon>
              </el-tooltip>
            </div>
          </template>
          <template #default="{ row }">
            {{ formatSignalType(row, null, row.signal_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="close" label="最新价" width="100" :formatter="formatNumber3" />
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column v-if="queryParams.strategyType === 'combined' || queryParams.strategyType === 'macd'" prop="macd_fast" label="MACD快线" width="100" :formatter="formatNumber3" />
        <el-table-column v-if="queryParams.strategyType === 'combined' || queryParams.strategyType === 'macd'" prop="macd_signal" label="MACD信号线" width="110" :formatter="formatNumber3" />
        <el-table-column v-if="queryParams.strategyType === 'combined' || queryParams.strategyType === 'bollinger'" prop="bb_upper" label="布林带上轨" width="100" :formatter="formatNumber3" />
        <el-table-column v-if="queryParams.strategyType === 'combined' || queryParams.strategyType === 'bollinger'" prop="bb_middle" label="布林带中轨" width="100" :formatter="formatNumber3" />
        <el-table-column v-if="queryParams.strategyType === 'combined' || queryParams.strategyType === 'bollinger'" prop="bb_lower" label="布林带下轨" width="100" :formatter="formatNumber3" />
        <el-table-column v-if="queryParams.strategyType === 'combined' || queryParams.strategyType === 'bollinger'" prop="bb_position" label="布林带位置" width="110">
          <template #default="{ row }">
            {{ (row.bb_position * 100).toFixed(3) }}%
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, sizes, prev, pager, next"
        :page-sizes="[10, 13, 20, 50, 100]"
        style="margin-top: 20px; justify-content: flex-end"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="`${selectedEtf?.code || ''} - ${selectedEtf?.name || ''}`" width="90%" top="5vh">
      <div v-loading="loadingChart" class="chart-container">
        <div ref="mainChartRef" class="main-chart"></div>
        <div ref="macdChartRef" class="macd-chart"></div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'
import { screeningAPI, databaseAPI, backtestAPI } from '@/api/endpoints'
import * as echarts from 'echarts'
import {
  LegendComponent,
  TooltipComponent,
  GridComponent,
  DataZoomComponent
} from 'echarts/components'
import { LineChart, BarChart } from 'echarts/charts'
import { ElMessage } from 'element-plus'

echarts.use([
  LegendComponent,
  TooltipComponent,
  GridComponent,
  DataZoomComponent,
  LineChart,
  BarChart
])

const queryParams = ref({
  strategyType: 'combined',
  period: 'daily',
  endDate: '',
  lookbackDays: 60,
  requireMacdGolden: true,
  requireBbAboveMiddle: true
})

const screeningData = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(13)
const total = ref(0)

const dialogVisible = ref(false)
const selectedEtf = ref(null)
const loadingChart = ref(false)

const mainChartRef = ref(null)
const macdChartRef = ref(null)

const mainChart = ref(null)
const macdChart = ref(null)

let resizeHandler = null

const displayData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return screeningData.value.slice(start, end)
})

const screen = async () => {
  loading.value = true
  try {
    let response
    
    const commonParams = {
      end_date: queryParams.value.endDate,
      period: queryParams.value.period,
      lookback_days: queryParams.value.lookbackDays
    }
    
    switch (queryParams.value.strategyType) {
      case 'combined':
        response = await screeningAPI.getCombined({
          ...commonParams,
          require_macd_golden: queryParams.value.requireMacdGolden,
          require_bb_above_middle: queryParams.value.requireBbAboveMiddle
        })
        break
      case 'macd':
        response = await screeningAPI.getMACD({
          ...commonParams,
          include_golden_cross: queryParams.value.requireMacdGolden,
          include_death_cross: false
        })
        break
      case 'bollinger':
        response = await screeningAPI.getBollinger({
          ...commonParams,
          include_upper_break: true,
          include_lower_break: false,
          include_squeeze: false
        })
        break
      case 'volume':
        response = await screeningAPI.getVolume({
          ...commonParams,
          min_volume_ratio: 2.0
        })
        break
    }
    
    if (response.success) {
      screeningData.value = response.data
      total.value = response.data.length
      currentPage.value = 1
    }
  } catch (error) {
    console.error('筛选失败:', error)
  } finally {
    loading.value = false
  }
}

const handleRowClick = async (row) => {
  selectedEtf.value = row
  dialogVisible.value = true
  await nextTick()
  await nextTick()
  await loadChartData(row.code)
}

const loadChartData = async (code) => {
  loadingChart.value = true
  try {
    const startDate = new Date()
    startDate.setMonth(startDate.getMonth() - 3)
    const startDateStr = `${startDate.getFullYear()}${String(startDate.getMonth() + 1).padStart(2, '0')}${String(startDate.getDate()).padStart(2, '0')}`
    
    const response = await databaseAPI.queryHistory({ code, start_date: startDateStr })
    
    if (response.success && response.data.length > 0) {
      // 计算技术指标
      const dataWithIndicators = calculateIndicators(response.data)
      
      await nextTick()
      initCharts()
      updateCharts(dataWithIndicators)
    }
  } catch (error) {
    console.error('加载图表数据失败:', error)
  } finally {
    loadingChart.value = false
  }
}

// 计算简单移动平均线
const calculateSMA = (data, period) => {
  const result = []
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null)
    } else {
      let sum = 0
      for (let j = 0; j < period; j++) {
        sum += data[i - j]
      }
      result.push(sum / period)
    }
  }
  return result
}

// 计算指数移动平均线
const calculateEMA = (data, period) => {
  const result = []
  const multiplier = 2 / (period + 1)
  
  // 第一个EMA使用SMA
  let ema = null
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null)
    } else if (i === period - 1) {
      let sum = 0
      for (let j = 0; j < period; j++) {
        sum += data[i - j]
      }
      ema = sum / period
      result.push(ema)
    } else {
      ema = (data[i] - ema) * multiplier + ema
      result.push(ema)
    }
  }
  return result
}

// 计算MACD
const calculateMACD = (closes, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) => {
  const fastEMA = calculateEMA(closes, fastPeriod)
  const slowEMA = calculateEMA(closes, slowPeriod)
  
  const macdLine = []
  for (let i = 0; i < closes.length; i++) {
    if (fastEMA[i] === null || slowEMA[i] === null) {
      macdLine.push(null)
    } else {
      macdLine.push(fastEMA[i] - slowEMA[i])
    }
  }
  
  // 过滤掉null值用于计算信号线
  const validMacdLine = macdLine.filter(v => v !== null)
  const signalLineValid = calculateEMA(validMacdLine, signalPeriod)
  
  // 将信号线映射回原始数组
  const signalLine = []
  let validIndex = 0
  for (let i = 0; i < macdLine.length; i++) {
    if (macdLine[i] === null) {
      signalLine.push(null)
    } else {
      signalLine.push(signalLineValid[validIndex] || null)
      validIndex++
    }
  }
  
  const histogram = []
  for (let i = 0; i < macdLine.length; i++) {
    if (macdLine[i] === null || signalLine[i] === null) {
      histogram.push(null)
    } else {
      histogram.push(macdLine[i] - signalLine[i])
    }
  }
  
  return { macdLine, signalLine, histogram }
}

// 计算布林带
const calculateBollingerBands = (closes, period = 20, stdDev = 2) => {
  const sma = calculateSMA(closes, period)
  const upper = []
  const lower = []
  
  for (let i = 0; i < closes.length; i++) {
    if (sma[i] === null) {
      upper.push(null)
      lower.push(null)
    } else {
      let sum = 0
      for (let j = 0; j < period; j++) {
        const diff = closes[i - j] - sma[i]
        sum += diff * diff
      }
      const std = Math.sqrt(sum / period)
      upper.push(sma[i] + stdDev * std)
      lower.push(sma[i] - stdDev * std)
    }
  }
  
  return { middle: sma, upper, lower }
}

// 计算RSI
const calculateRSI = (closes, period = 14) => {
  const rsi = []
  const changes = []
  
  for (let i = 1; i < closes.length; i++) {
    changes.push(closes[i] - closes[i - 1])
  }
  
  for (let i = 0; i < closes.length; i++) {
    if (i < period) {
      rsi.push(null)
    } else {
      let gains = 0
      let losses = 0
      
      for (let j = 0; j < period; j++) {
        const change = changes[i - 1 - j]
        if (change > 0) {
          gains += change
        } else {
          losses -= change
        }
      }
      
      const avgGain = gains / period
      const avgLoss = losses / period
      
      if (avgLoss === 0) {
        rsi.push(100)
      } else {
        const rs = avgGain / avgLoss
        rsi.push(100 - (100 / (1 + rs)))
      }
    }
  }
  
  return rsi
}

// 计算所有技术指标
const calculateIndicators = (data) => {
  const closes = data.map(d => d.close)
  
  const { macdLine, signalLine, histogram } = calculateMACD(closes)
  const { middle: bbMiddle, upper: bbUpper, lower: bbLower } = calculateBollingerBands(closes)
  const rsi = calculateRSI(closes)
  
  return data.map((item, index) => ({
    ...item,
    macd: macdLine[index],
    macd_signal: signalLine[index],
    macd_hist: histogram[index],
    bb_upper: bbUpper[index],
    bb_middle: bbMiddle[index],
    bb_lower: bbLower[index],
    rsi: rsi[index]
  }))
}

const initCharts = () => {
  if (mainChartRef.value) {
    if (mainChart.value) {
      mainChart.value.dispose()
    }
    mainChart.value = echarts.init(mainChartRef.value)
  }
  
  if (macdChartRef.value) {
    if (macdChart.value) {
      macdChart.value.dispose()
    }
    macdChart.value = echarts.init(macdChartRef.value)
  }
}

const updateCharts = (data) => {
  if (!mainChart.value || !macdChart.value) {
    return
  }
  
  const dates = data.map(d => d.date)
  const closes = data.map(d => d.close)
  const bbUppers = data.map(d => d.bb_upper)
  const bbMiddles = data.map(d => d.bb_middle)
  const bbLowers = data.map(d => d.bb_lower)
  const macds = data.map(d => d.macd)
  const macdSignals = data.map(d => d.macd_signal)
  const macdHists = data.map(d => d.macd_hist)
  
  const mainOption = {
    tooltip: {
      show: true,
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function(params) {
        let result = params[0].axisValue + '<br/>'
        params.forEach(param => {
          if (param.value !== null && param.value !== undefined) {
            result += `${param.marker} ${param.seriesName}: ${Number(param.value).toFixed(3)}<br/>`
          }
        })
        return result
      }
    },
    legend: {
      show: true,
      data: ['收盘价', '布林带上轨', '布林带中轨', '布林带下轨'],
      selected: {
        '收盘价': true,
        '布林带上轨': true,
        '布林带中轨': true,
        '布林带下轨': true
      }
    },
    grid: {
      left: '3%',
      right: '3%',
      top: '20%',
      bottom: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      scale: true
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLabel: {
        formatter: '{value}'
      }
    },
    dataZoom: [
      {
        type: 'inside',
        start: 50,
        end: 100
      },
      {
        show: true,
        type: 'slider',
        top: '90%',
        start: 50,
        end: 100
      }
    ],
    series: [
      {
        name: '收盘价',
        type: 'line',
        data: closes,
        smooth: true,
        itemStyle: {
          color: '#5470c6'
        },
        lineStyle: {
          width: 2
        }
      },
      {
        name: '布林带上轨',
        type: 'line',
        data: bbUppers,
        smooth: true,
        itemStyle: {
          color: '#ee6666'
        },
        lineStyle: {
          width: 1,
          type: 'dashed'
        }
      },
      {
        name: '布林带中轨',
        type: 'line',
        data: bbMiddles,
        smooth: true,
        itemStyle: {
          color: '#91cc75'
        },
        lineStyle: {
          width: 1
        }
      },
      {
        name: '布林带下轨',
        type: 'line',
        data: bbLowers,
        smooth: true,
        itemStyle: {
          color: '#ee6666'
        },
        lineStyle: {
          width: 1,
          type: 'dashed'
        }
      }
    ]
  }
  
  const macdOption = {
    tooltip: {
      show: true,
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function(params) {
        let result = params[0].axisValue + '<br/>'
        params.forEach(param => {
          if (param.value !== null && param.value !== undefined) {
            result += `${param.marker} ${param.seriesName}: ${Number(param.value).toFixed(3)}<br/>`
          }
        })
        return result
      }
    },
    legend: {
      show: true,
      data: ['MACD（快线）', '慢线（信号线）', '柱状图'],
      selected: {
        'MACD（快线）': true,
        '慢线（信号线）': true,
        '柱状图': true
      }
    },
    grid: {
      left: '3%',
      right: '3%',
      top: '20%',
      bottom: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      scale: true
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLabel: {
        formatter: '{value}'
      }
    },
    dataZoom: [
      {
        type: 'inside',
        start: 50,
        end: 100
      },
      {
        show: true,
        type: 'slider',
        top: '90%',
        start: 50,
        end: 100
      }
    ],
    series: [
      {
        name: 'MACD（快线）',
        type: 'line',
        data: macds,
        smooth: true,
        itemStyle: {
          color: '#5470c6'
        },
        lineStyle: {
          width: 2
        }
      },
      {
        name: '慢线（信号线）',
        type: 'line',
        data: macdSignals,
        smooth: true,
        itemStyle: {
          color: '#fac858'
        },
        lineStyle: {
          width: 2
        }
      },
      {
        name: '柱状图',
        type: 'bar',
        data: macdHists,
        itemStyle: {
          color: (params) => {
            return params.value >= 0 ? '#91cc75' : '#ee6666'
          }
        }
      }
    ]
  }
  
  mainChart.value.setOption(mainOption, { notMerge: true })
  macdChart.value.setOption(macdOption, { notMerge: true })
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

const formatNumber3 = (row, column, cellValue) => {
  if (cellValue === null || cellValue === undefined || cellValue === '') {
    return '-'
  }
  return Number(cellValue).toFixed(3)
}

const formatSignalType = (_, __, cellValue) => {
  const signalTypeMap = {
    'MACD Golden Cross': 'MACD金叉',
    'MACD Death Cross': 'MACD死叉',
    'BB Upper Break': '布林带突破上轨',
    'BB Lower Break': '布林带突破下轨',
    'BB Squeeze': '布林带收缩',
    'Combined Signal': '组合信号',
    'High Volume': '高成交量'
  }
  return signalTypeMap[cellValue] || cellValue || '-'
}

const getFundUrl = (code) => {
  let cleanCode = code
  if (code.startsWith('sh') || code.startsWith('sz')) {
    cleanCode = code.substring(2)
  }
  return `http://fund.eastmoney.com/${cleanCode}.html`
}

onMounted(() => {
  screen()
  resizeHandler = () => {
    mainChart.value && mainChart.value.resize()
    macdChart.value && macdChart.value.resize()
  }
  window.addEventListener('resize', resizeHandler)
})

onUnmounted(() => {
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
  }
  if (mainChart.value) {
    mainChart.value.dispose()
  }
  if (macdChart.value) {
    macdChart.value.dispose()
  }
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-table {
  width: 100%;
}

.el-table .el-table__body-wrapper {
  width: 100%;
}

.el-table :deep(.el-table__body tr:hover > td) {
  cursor: pointer;
}

.chart-container {
  min-height: 600px;
}

.main-chart {
  width: 100%;
  height: 350px;
  margin-bottom: 20px;
}

.macd-chart {
  width: 100%;
  height: 250px;
}

.el-dialog {
  z-index: 2000 !important;
}

.el-dialog__body {
  overflow: visible !important;
}
</style>
