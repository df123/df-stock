/**
 * 指标配置模块
 * 定义指标配置接口和默认配置
 */

/**
 * 指标类型枚举
 */
export const IndicatorType = {
  SMA: 'sma',
  EMA: 'ema',
  MACD: 'macd',
  BOLLINGER: 'bollinger',
  RSI: 'rsi',
  KDJ: 'kdj'
}

/**
 * 图表类型枚举
 */
export const ChartType = {
  MAIN: 'main',        // 主图表（价格）
  MACD: 'macd',        // MACD图表
  RSI: 'rsi',          // RSI图表
  KDJ: 'kdj'           // KDJ图表
}

/**
 * 指标配置类
 */
export class IndicatorConfig {
  /**
   * @param {string} id - 指标唯一标识
   * @param {string} name - 指标显示名称
   * @param {IndicatorType} type - 指标类型
   * @param {ChartType} chartType - 所属图表类型
   * @param {string} seriesType - ECharts 系列类型 (line, bar)
   * @param {Object} seriesConfig - ECharts 系列配置
   * @param {Object} defaultParams - 默认计算参数
   * @param {boolean} visible - 默认是否可见
   * @param {Function} tooltipFormatter - 自定义 tooltip 格式化函数
   */
  constructor({
    id,
    name,
    type,
    chartType,
    seriesType,
    seriesConfig = {},
    defaultParams = {},
    visible = true,
    tooltipFormatter = null
  }) {
    this.id = id
    this.name = name
    this.type = type
    this.chartType = chartType
    this.seriesType = seriesType
    this.seriesConfig = seriesConfig
    this.defaultParams = defaultParams
    this.visible = visible
    this.tooltipFormatter = tooltipFormatter
  }
}

/**
 * 复合指标配置（如MACD包含快线、信号线、柱状图）
 */
export class CompositeIndicatorConfig {
  /**
   * @param {string} id - 指标唯一标识
   * @param {string} name - 指标显示名称
   * @param {IndicatorType} type - 指标类型
   * @param {ChartType} chartType - 所属图表类型
   * @param {Array<IndicatorConfig>} subIndicators - 子指标配置
   * @param {Object} defaultParams - 默认计算参数
   */
  constructor({
    id,
    name,
    type,
    chartType,
    subIndicators,
    defaultParams = {}
  }) {
    this.id = id
    this.name = name
    this.type = type
    this.chartType = chartType
    this.subIndicators = subIndicators
    this.defaultParams = defaultParams
  }
}

// ==================== 指标配置定义 ====================

/**
 * 布林带上轨配置
 */
export const bollingerUpperConfig = new IndicatorConfig({
  id: 'bollinger_upper',
  name: '布林带上轨',
  type: IndicatorType.BOLLINGER,
  chartType: ChartType.MAIN,
  seriesType: 'line',
  seriesConfig: {
    smooth: true,
    lineStyle: { width: 1, type: 'dashed' },
    itemStyle: { color: '#ee6666' }
  },
  defaultParams: { period: 20, stdDev: 2 },
  visible: true
})

/**
 * 布林带中轨配置
 */
export const bollingerMiddleConfig = new IndicatorConfig({
  id: 'bollinger_middle',
  name: '布林带中轨',
  type: IndicatorType.BOLLINGER,
  chartType: ChartType.MAIN,
  seriesType: 'line',
  seriesConfig: {
    smooth: true,
    lineStyle: { width: 1 },
    itemStyle: { color: '#91cc75' }
  },
  defaultParams: { period: 20 },
  visible: true
})

/**
 * 布林带下轨配置
 */
export const bollingerLowerConfig = new IndicatorConfig({
  id: 'bollinger_lower',
  name: '布林带下轨',
  type: IndicatorType.BOLLINGER,
  chartType: ChartType.MAIN,
  seriesType: 'line',
  seriesConfig: {
    smooth: true,
    lineStyle: { width: 1, type: 'dashed' },
    itemStyle: { color: '#ee6666' }
  },
  defaultParams: { period: 20, stdDev: 2 },
  visible: true
})

/**
 * MACD指标配置（复合指标）
 */
export const macdIndicator = new CompositeIndicatorConfig({
  id: 'macd',
  name: 'MACD',
  type: IndicatorType.MACD,
  chartType: ChartType.MACD,
  subIndicators: [
    new IndicatorConfig({
      id: 'macd_fast',
      name: 'MACD（快线）',
      type: IndicatorType.MACD,
      chartType: ChartType.MACD,
      seriesType: 'line',
      seriesConfig: {
        smooth: true,
        lineStyle: { width: 2 },
        itemStyle: { color: '#5470c6' }
      },
      defaultParams: { fastPeriod: 12, slowPeriod: 26 },
      visible: true
    }),
    new IndicatorConfig({
      id: 'macd_signal',
      name: '慢线（信号线）',
      type: IndicatorType.MACD,
      chartType: ChartType.MACD,
      seriesType: 'line',
      seriesConfig: {
        smooth: true,
        lineStyle: { width: 2 },
        itemStyle: { color: '#fac858' }
      },
      defaultParams: { signalPeriod: 9 },
      visible: true
    }),
    new IndicatorConfig({
      id: 'macd_hist',
      name: '柱状图',
      type: IndicatorType.MACD,
      chartType: ChartType.MACD,
      seriesType: 'bar',
      seriesConfig: {
        itemStyle: {
          color: (params) => {
            return params.value >= 0 ? '#91cc75' : '#ee6666'
          }
        }
      },
      defaultParams: {},
      visible: true
    })
  ],
  defaultParams: { fastPeriod: 12, slowPeriod: 26, signalPeriod: 9 }
})

/**
 * RSI指标配置
 */
export const rsiIndicator = new IndicatorConfig({
  id: 'rsi',
  name: 'RSI',
  type: IndicatorType.RSI,
  chartType: ChartType.RSI,
  seriesType: 'line',
  seriesConfig: {
    smooth: true,
    lineStyle: { width: 2 },
    itemStyle: { color: '#73c0de' }
  },
  defaultParams: { period: 14 },
  visible: true
})

/**
 * KDJ指标配置（复合指标）
 */
export const kdjIndicator = new CompositeIndicatorConfig({
  id: 'kdj',
  name: 'KDJ',
  type: IndicatorType.KDJ,
  chartType: ChartType.KDJ,
  subIndicators: [
    new IndicatorConfig({
      id: 'kdj_k',
      name: 'K线',
      type: IndicatorType.KDJ,
      chartType: ChartType.KDJ,
      seriesType: 'line',
      seriesConfig: {
        smooth: true,
        lineStyle: { width: 2 },
        itemStyle: { color: '#5470c6' }
      },
      defaultParams: { period: 9, kPeriod: 3, dPeriod: 3 },
      visible: true
    }),
    new IndicatorConfig({
      id: 'kdj_d',
      name: 'D线',
      type: IndicatorType.KDJ,
      chartType: ChartType.KDJ,
      seriesType: 'line',
      seriesConfig: {
        smooth: true,
        lineStyle: { width: 2 },
        itemStyle: { color: '#fac858' }
      },
      defaultParams: { period: 9, kPeriod: 3, dPeriod: 3 },
      visible: true
    }),
    new IndicatorConfig({
      id: 'kdj_j',
      name: 'J线',
      type: IndicatorType.KDJ,
      chartType: ChartType.KDJ,
      seriesType: 'line',
      seriesConfig: {
        smooth: true,
        lineStyle: { width: 2 },
        itemStyle: { color: '#ee6666' }
      },
      defaultParams: { period: 9, kPeriod: 3, dPeriod: 3 },
      visible: true
    })
  ],
  defaultParams: { period: 9, kPeriod: 3, dPeriod: 3 }
})

/**
 * 默认指标配置列表
 */
export const defaultIndicators = [
  bollingerUpperConfig,
  bollingerMiddleConfig,
  bollingerLowerConfig,
  macdIndicator,
  rsiIndicator,
  kdjIndicator
]
