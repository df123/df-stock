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
            <el-link type="primary" :href="getFundUrl(row.code)" target="_blank" :underline="'never'" @click.stop>
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

    <el-dialog v-model="dialogVisible" :title="`${selectedEtf?.code || ''} - ${selectedEtf?.name || ''}`" width="90%" top="5vh" @opened="handleDialogOpened">
      <div v-loading="loadingChart" class="chart-dialog-container">
        <!-- 图表控制面板 -->
        <div class="chart-controls">
          <el-checkbox-group v-model="visibleCharts">
            <el-checkbox value="main">主图表</el-checkbox>
            <el-checkbox value="macd">MACD</el-checkbox>
            <el-checkbox value="rsi">RSI</el-checkbox>
            <el-checkbox value="kdj">KDJ</el-checkbox>
          </el-checkbox-group>
        </div>

        <!-- 图表容器 -->
        <div class="charts-wrapper">
          <!-- 主图表 -->
          <IndicatorChart
            ref="mainChartRef"
            v-if="visibleCharts.includes('main')"
            chart-id="screening-main"
            chart-type="main"
            :data="chartData"
            height="350px"
            :show-data-zoom="true"
            @legend-select-changed="handleLegendChange"
            @chart-ready="handleChartReady"
          />

          <!-- MACD图表 -->
          <IndicatorChart
            ref="macdChartRef"
            v-if="visibleCharts.includes('macd')"
            chart-id="screening-macd"
            chart-type="macd"
            :data="chartData"
            height="250px"
            :show-data-zoom="true"
            @legend-select-changed="handleLegendChange"
            @chart-ready="handleChartReady"
          />

          <!-- RSI图表 -->
          <IndicatorChart
            ref="rsiChartRef"
            v-if="visibleCharts.includes('rsi')"
            chart-id="screening-rsi"
            chart-type="rsi"
            :data="chartData"
            height="200px"
            :show-data-zoom="true"
            @legend-select-changed="handleLegendChange"
            @chart-ready="handleChartReady"
          />

          <!-- KDJ图表 -->
          <IndicatorChart
            ref="kdjChartRef"
            v-if="visibleCharts.includes('kdj')"
            chart-id="screening-kdj"
            chart-type="kdj"
            :data="chartData"
            height="200px"
            :show-data-zoom="true"
            @legend-select-changed="handleLegendChange"
            @chart-ready="handleChartReady"
          />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'
import { screeningAPI, databaseAPI, backtestAPI } from '@/api/endpoints'
import IndicatorChart from '@/components/charts/IndicatorChart.vue'
import { ElMessage } from 'element-plus'

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

// 图表数据
const chartData = ref([])

// 可见的图表类型
const visibleCharts = ref(['main', 'macd'])

// 图表引用
const mainChartRef = ref(null)
const macdChartRef = ref(null)
const rsiChartRef = ref(null)
const kdjChartRef = ref(null)

// 图表引用映射
const chartRefs = {
  main: mainChartRef,
  macd: macdChartRef,
  rsi: rsiChartRef,
  kdj: kdjChartRef
}

// 图表实例映射（用于访问图表方法）
const chartInstances = ref({
  main: null,
  macd: null,
  rsi: null,
  kdj: null
})

// 窗口resize处理
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
    ElMessage.error('筛选失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleRowClick = async (row) => {
  selectedEtf.value = row
  dialogVisible.value = true
}

const handleDialogOpened = async () => {
  if (selectedEtf.value) {
    await loadChartData(selectedEtf.value.code)
  }
}

const loadChartData = async (code) => {
  loadingChart.value = true
  try {
    const startDate = new Date()
    startDate.setMonth(startDate.getMonth() - 3)
    const startDateStr = `${startDate.getFullYear()}${String(startDate.getMonth() + 1).padStart(2, '0')}${String(startDate.getDate()).padStart(2, '0')}`
    
    const response = await databaseAPI.queryHistory({ code, start_date: startDateStr })
    
    if (response.success && response.data.length > 0) {
      // 转换数据格式为图表所需格式
      chartData.value = response.data.map(item => ({
        date: item.date,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volume
      }))
    } else {
      chartData.value = []
      ElMessage.warning('未找到该ETF的历史数据')
    }
  } catch (error) {
    console.error('加载图表数据失败:', error)
    ElMessage.error('加载图表数据失败')
    chartData.value = []
  } finally {
    loadingChart.value = false
  }
}

const handleLegendChange = (event) => {
  // 图例状态已经通过 ChartManager 自动同步到响应式状态
  if (event.chartId && event.indicatorId !== undefined) {
    const preferenceKey = `chart-legend-${event.chartId}-${event.indicatorId}`
    try {
      localStorage.setItem(preferenceKey, String(event.visible))
    } catch (e) {
      // localStorage 不可用（隐私模式、存储危等），忽略
    }
  }
}

const handleChartReady = (event) => {
  console.log('图表准备就绪:', event)
  // 保存图表实例引用，以便后续调用其方法
  if (event.chartId && chartRefs[event.chartType]) {
    chartInstances.value[event.chartType] = chartRefs[event.chartType].value
  }
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
    // 调整所有可见图表的大小
    Object.values(chartInstances.value).forEach(chartInstance => {
      if (chartInstance && typeof chartInstance.resize === 'function') {
        chartInstance.resize()
      }
    })
  }
  window.addEventListener('resize', resizeHandler)
})

onUnmounted(() => {
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
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

.chart-dialog-container {
  min-height: 600px;
}

.chart-controls {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.charts-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.el-dialog {
  z-index: 2000 !important;
}

.el-dialog__body {
  overflow: visible !important;
}
</style>
