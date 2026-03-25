<template>
  <div class="indicator-chart" :style="{ height: height }">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import {
  LegendComponent,
  TooltipComponent,
  GridComponent,
  DataZoomComponent
} from 'echarts/components'
import { LineChart, BarChart } from 'echarts/charts'
import { ChartManager } from './ChartManager.js'
import { ChartConfigBuilder } from './ChartConfigBuilder.js'
import { IndicatorCalculator } from '../../utils/indicators/IndicatorCalculator.js'
import { registerDefaultIndicators } from './IndicatorRegistry.js'
import { ChartType } from './IndicatorConfig.js'

echarts.use([
  LegendComponent,
  TooltipComponent,
  GridComponent,
  DataZoomComponent,
  LineChart,
  BarChart
])

const props = defineProps({
  chartId: {
    type: String,
    required: true
  },
  chartType: {
    type: String,
    required: true,
    validator: (value) => {
      return ['main', 'macd', 'rsi', 'kdj'].includes(value)
    }
  },
  data: {
    type: Array,
    required: true,
    default: () => []
  },
  height: {
    type: String,
    default: '400px'
  },
  showDataZoom: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['legend-select-changed', 'chart-ready'])

const chartRef = ref(null)

let chartManager = null
let configBuilder = null
let indicatorCalculator = null
let chartInstance = null

const chartTypeMap = {
  'main': ChartType.MAIN,
  'macd': ChartType.MACD,
  'rsi': ChartType.RSI,
  'kdj': ChartType.KDJ
}

const MAX_INIT_RETRIES = 10

const initChart = async (retryCount = 0) => {
  if (!chartRef.value) {
    console.error('图表DOM元素未找到')
    return
  }

  try {
    // 等待DOM完全渲染
    await nextTick()

    // 检查DOM尺寸是否有效
    if (chartRef.value.clientWidth === 0 || chartRef.value.clientHeight === 0) {
      if (retryCount >= MAX_INIT_RETRIES) {
        console.error(`图表 ${props.chartId} DOM尺寸为0，已达最大重试次数，放弃初始化`)
        return
      }
      // 延迟重试
      setTimeout(() => initChart(retryCount + 1), 100)
      return
    }

    registerDefaultIndicators()

    chartManager = new ChartManager()
    configBuilder = new ChartConfigBuilder(chartManager)
    indicatorCalculator = new IndicatorCalculator()

    const chartTypeEnum = chartTypeMap[props.chartType]
    chartInstance = chartManager.createChart(props.chartId, chartRef, echarts.init, {
      chartType: chartTypeEnum
    })

    // 设置图例事件监听器，支持响应式线条控制
    chartManager.setLegendListener(props.chartId, (indicatorId, visible) => {
      emit('legend-select-changed', {
        chartId: props.chartId,
        chartType: props.chartType,
        indicatorId: indicatorId,
        visible: visible
      })
    })

    if (props.data && props.data.length > 0) {
      await updateChart()
    }

    emit('chart-ready', {
      chartId: props.chartId,
      chartType: props.chartType
    })
  } catch (error) {
    console.error('初始化图表失败:', error)
    cleanup()
  }
}

const MAX_UPDATE_RETRIES = 10

const updateChart = async (retryCount = 0) => {
  if (!chartInstance || !props.data || props.data.length === 0) {
    return
  }

  try {
    await nextTick()

    // 检查DOM尺寸是否有效
    if (chartRef.value && (chartRef.value.clientWidth === 0 || chartRef.value.clientHeight === 0)) {
      if (retryCount >= MAX_UPDATE_RETRIES) {
        console.error(`图表 ${props.chartId} DOM尺寸为0，已达最大重试次数，放弃更新`)
        return
      }
      setTimeout(() => updateChart(retryCount + 1), 100)
      return
    }

    const chartTypeEnum = chartTypeMap[props.chartType]
    const indicatorData = indicatorCalculator.calculateForChart(props.data, chartTypeEnum)
    const config = configBuilder.build(chartTypeEnum, indicatorData, {
      showDataZoom: props.showDataZoom
    })
    chartInstance.setOption(config, { notMerge: true })
  } catch (error) {
    console.error(`图表 ${props.chartId} 更新失败:`, error)
  }
}


const resize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

const getChartInstance = () => {
  return chartInstance
}

const getChartManager = () => {
  return chartManager
}

const cleanup = () => {
  if (chartManager) {
    chartManager.disposeChart(props.chartId)
    chartInstance = null  // chartManager.disposeChart 已释放 echarts 实例
    chartManager = null
  }
  if (chartInstance && !chartInstance.isDisposed()) {
    chartInstance.dispose()
  }
  chartInstance = null
  configBuilder = null
  indicatorCalculator = null
}

watch(() => props.data, () => {
  updateChart()
}, { deep: true })

watch(() => props.chartType, () => {
  cleanup()
  initChart()
})

onMounted(() => {
  initChart()
})

onUnmounted(() => {
  cleanup()
})

defineExpose({
  resize,
  getChartInstance,
  getChartManager
})
</script>

<style scoped>
.indicator-chart {
  width: 100%;
  position: relative;
}

.chart-container {
  width: 100%;
  height: 100%;
}
</style>
