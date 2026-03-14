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
import { screeningAPI } from '@/api/endpoints'
import axios from 'axios'
import * as echarts from 'echarts'

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

const displayData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return screeningData.value.slice(start, end)
})

const screen = async () => {
  loading.value = true
  try {
    let response
    
    switch (queryParams.value.strategyType) {
      case 'combined':
        response = await screeningAPI.getCombined({
          end_date: queryParams.value.endDate,
          period: queryParams.value.period,
          lookback_days: queryParams.value.lookbackDays,
          require_macd_golden: queryParams.value.requireMacdGolden,
          require_bb_above_middle: queryParams.value.requireBbAboveMiddle
        })
        break
      case 'macd':
        response = await screeningAPI.getMACD({
          end_date: queryParams.value.endDate,
          period: queryParams.value.period,
          lookback_days: queryParams.value.lookbackDays,
          include_golden_cross: queryParams.value.requireMacdGolden,
          include_death_cross: false
        })
        break
      case 'bollinger':
        response = await screeningAPI.getBollinger({
          end_date: queryParams.value.endDate,
          period: queryParams.value.period,
          lookback_days: queryParams.value.lookbackDays,
          include_upper_break: true,
          include_lower_break: false,
          include_squeeze: false
        })
        break
      case 'volume':
        response = await screeningAPI.getVolume({
          end_date: queryParams.value.endDate,
          period: queryParams.value.period,
          lookback_days: queryParams.value.lookbackDays,
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
    const startDateStr = startDate.toISOString().slice(0, 10).replace(/-/g, '')
    
    const response = await axios.get(`http://localhost:8000/api/history/${code}/indicators`, {
      params: {
        start_date: startDateStr,
        indicators: 'all'
      }
    })
    
    if (response.data.success && response.data.data.length > 0) {
      await nextTick()
      await nextTick()
      initCharts()
      updateCharts(response.data.data)
    }
  } catch (error) {
    console.error('加载图表数据失败:', error)
  } finally {
    loadingChart.value = false
  }
}

const initCharts = () => {
  console.log('initCharts called', {
    mainChartRef: !!mainChartRef.value,
    macdChartRef: !!macdChartRef.value
  })
  
  if (mainChartRef.value) {
    if (mainChart.value) {
      mainChart.value.dispose()
    }
    mainChart.value = echarts.init(mainChartRef.value)
    console.log('Main chart initialized')
  }
  
  if (macdChartRef.value) {
    if (macdChart.value) {
      macdChart.value.dispose()
    }
    macdChart.value = echarts.init(macdChartRef.value)
    console.log('MACD chart initialized')
  }
}

const updateCharts = (data) => {
  console.log('updateCharts called', {
    dataLength: data.length,
    mainChart: !!mainChart.value,
    macdChart: !!macdChart.value
  })
  
  if (!mainChart.value || !macdChart.value) {
    console.error('Charts not initialized')
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
  
  console.log('Data extracted', {
    dates: dates.length,
    closes: closes.length,
    macds: macds.filter(m => m !== null).length,
    macdSignals: macdSignals.filter(m => m !== null).length,
    macdHists: macdHists.filter(m => m !== null).length
  })
  
  const mainOption = {
    tooltip: {
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
      data: ['收盘价', '布林带上轨', '布林带中轨', '布林带下轨']
    },
    grid: {
      left: '3%',
      right: '3%',
      bottom: '3%',
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
      data: ['MACD（快线）', '慢线（信号线）', '柱状图']
    },
    grid: {
      left: '3%',
      right: '3%',
      bottom: '3%',
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
        data: macdHists.map((val, idx) => {
          return {
            value: val,
            itemStyle: {
              color: val >= 0 ? '#91cc75' : '#ee6666'
            }
          }
        }),
        itemStyle: {
          color: (params) => {
            return params.value >= 0 ? '#91cc75' : '#ee6666'
          }
        }
      }
    ]
  }
  
  mainChart.value.setOption(mainOption)
  macdChart.value.setOption(macdOption)
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

const formatSignalType = (row, column, cellValue) => {
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
  window.addEventListener('resize', () => {
    mainChart.value?.resize()
    macdChart.value?.resize()
  })
})

onUnmounted(() => {
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
</style>
