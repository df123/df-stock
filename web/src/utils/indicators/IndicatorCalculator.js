/**
 * 指标计算器模块
 * 提供统一的技术指标计算接口
 */

import { indicatorRegistry } from '@/components/charts/IndicatorRegistry.js'

/**
 * 计算简单移动平均线 (SMA)
 * @param {Array<number>} data - 数据数组
 * @param {number} period - 周期
 * @returns {Array<number|null>} SMA值数组
 */
export function calculateSMA(data, period) {
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

/**
 * 计算指数移动平均线 (EMA)
 * @param {Array<number>} data - 数据数组
 * @param {number} period - 周期
 * @returns {Array<number|null>} EMA值数组
 */
export function calculateEMA(data, period) {
  const result = []
  const multiplier = 2 / (period + 1)
  
  // 第一个EMA使用SMA
  let ema = null
  for (let i = 0; i < data.length; i++) {
    if (data[i] === null) {
      // 遇到null值，保持之前的有效EMA值
      result.push(ema)
    } else if (i < period - 1) {
      result.push(null)
    } else if (i === period - 1) {
      // 计算初始SMA，只使用有效值
      let sum = 0
      let count = 0
      for (let j = 0; j < period; j++) {
        if (data[i - j] !== null) {
          sum += data[i - j]
          count++
        }
      }
      ema = count > 0 ? sum / count : null
      result.push(ema)
    } else {
      ema = (data[i] - ema) * multiplier + ema
      result.push(ema)
    }
  }
  return result
}

/**
 * 计算MACD指标
 * @param {Array<number>} closes - 收盘价数组
 * @param {number} fastPeriod - 快线周期，默认12
 * @param {number} slowPeriod - 慢线周期，默认26
 * @param {number} signalPeriod - 信号线周期，默认9
 * @returns {Object} 包含macdLine, signalLine, histogram的对象
 */
export function calculateMACD(closes, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) {
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
  
  // 直接在macdLine上计算信号线，保持数据长度一致
  const signalLine = calculateEMA(macdLine, signalPeriod)
  
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

/**
 * 计算布林带 (Bollinger Bands)
 * @param {Array<number>} closes - 收盘价数组
 * @param {number} period - 周期，默认20
 * @param {number} stdDev - 标准差倍数，默认2
 * @returns {Object} 包含upper, middle, lower的对象
 */
export function calculateBollingerBands(closes, period = 20, stdDev = 2) {
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

/**
 * 计算RSI指标 (Relative Strength Index)
 * @param {Array<number>} closes - 收盘价数组
 * @param {number} period - 周期，默认14
 * @returns {Array<number|null>} RSI值数组
 */
export function calculateRSI(closes, period = 14) {
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

/**
 * 计算KDJ指标
 * @param {Array<number>} highs - 最高价数组
 * @param {Array<number>} lows - 最低价数组
 * @param {Array<number>} closes - 收盘价数组
 * @param {number} period - RSV周期，默认9
 * @param {number} kPeriod - K值平滑周期，默认3
 * @param {number} dPeriod - D值平滑周期，默认3
 * @returns {Object} 包含k, d, j的对象
 */
export function calculateKDJ(highs, lows, closes, period = 9, kPeriod = 3, dPeriod = 3) {
  const k = []
  const d = []
  const j = []
  const rsv = []
  
  // 计算RSV (Raw Stochastic Value)
  for (let i = 0; i < closes.length; i++) {
    if (i < period - 1) {
      rsv.push(null)
    } else {
      let highestHigh = -Infinity
      let lowestLow = Infinity
      
      for (let j = 0; j < period; j++) {
        const high = highs[i - j]
        const low = lows[i - j]
        if (high > highestHigh) highestHigh = high
        if (low < lowestLow) lowestLow = low
      }
      
      if (highestHigh === lowestLow) {
        rsv.push(50)
      } else {
        rsv.push(((closes[i] - lowestLow) / (highestHigh - lowestLow)) * 100)
      }
    }
  }
  
  // 计算K值 (使用EMA平滑RSV)
  let prevK = 50
  for (let i = 0; i < rsv.length; i++) {
    if (rsv[i] === null) {
      k.push(null)
    } else if (i < period - 1) {
      k.push(null)
    } else if (i === period - 1) {
      // 初始K值使用RSV
      prevK = rsv[i]
      k.push(prevK)
    } else {
      // K值 = (2/3) * 前一日K值 + (1/3) * 当日RSV
      prevK = (2 * prevK + rsv[i]) / 3
      k.push(prevK)
    }
  }
  
  // 计算D值 (使用EMA平滑K值)
  let prevD = 50
  for (let i = 0; i < k.length; i++) {
    if (k[i] === null) {
      d.push(null)
    } else if (i < period + kPeriod - 2) {
      d.push(null)
    } else if (i === period + kPeriod - 2) {
      // 初始D值使用K值
      prevD = k[i]
      d.push(prevD)
    } else {
      // D值 = (2/3) * 前一日D值 + (1/3) * 当日K值
      prevD = (2 * prevD + k[i]) / 3
      d.push(prevD)
    }
  }
  
  // 计算J值
  for (let i = 0; i < k.length; i++) {
    if (k[i] === null || d[i] === null) {
      j.push(null)
    } else {
      // J值 = 3 * K值 - 2 * D值
      j.push(3 * k[i] - 2 * d[i])
    }
  }
  
  return { k, d, j }
}

/**
 * 指标计算器类
 * 负责计算所有技术指标
 */
export class IndicatorCalculator {
  /**
   * 计算所有指标
   * @param {Array} data - 原始数据数组，每个元素应包含 close, high, low, date 字段
   * @param {Array<string>} indicatorIds - 需要计算的指标ID列表
   * @returns {Object} - 指标数据对象
   */
  calculateAll(data, indicatorIds = null) {
    if (!data || data.length === 0) {
      return {
        dates: [],
        closes: [],
        highs: [],
        lows: []
      }
    }

    const requiredFields = ['close', 'high', 'low', 'date']
    const missingFields = requiredFields.filter(f => data[0][f] === undefined || data[0][f] === null)
    if (missingFields.length > 0) {
      console.warn(`calculateAll: \u6570\u636e\u7f3a\u5c11\u5fc5\u8981\u5b57\u6bb5: ${missingFields.join(', ')}`)
      return { dates: [], closes: [], highs: [], lows: [] }
    }

    const closes = data.map(d => d.close)
    const highs = data.map(d => d.high)
    const lows = data.map(d => d.low)
    
    const result = {
      dates: data.map(d => d.date),
      closes,
      highs,
      lows
    }

    // 如果没有指定指标，计算所有注册的指标
    if (!indicatorIds) {
      indicatorIds = indicatorRegistry.getAll().map(i => i.id)
    }

    // 计算每个指标
    indicatorIds.forEach(id => {
      const indicator = indicatorRegistry.get(id)
      if (indicator) {
        const indicatorData = this._calculateIndicator(
          indicator,
          closes,
          highs,
          lows
        )
        // 复合指标返回对象（如 { macd_fast: [...], macd_signal: [...] }），需展开到顶层
        if (indicatorData && typeof indicatorData === 'object' && !Array.isArray(indicatorData)) {
          Object.assign(result, indicatorData)
        } else {
          result[id] = indicatorData
        }
      }
    })

    return result
  }

  /**
   * 计算单个指标
   * @private
   * @param {IndicatorConfig|CompositeIndicatorConfig} indicator - 指标配置
   * @param {Array<number>} closes - 收盘价数组
   * @param {Array<number>} highs - 最高价数组
   * @param {Array<number>} lows - 最低价数组
   * @returns {Object|Array|null} - 指标数据
   */
  _calculateIndicator(indicator, closes, highs, lows) {
    const params = indicator.defaultParams

    switch (indicator.type) {
      case 'sma':
        return calculateSMA(closes, params.period)
      
      case 'ema':
        return calculateEMA(closes, params.period)
      
      case 'macd':
        const macdResult = calculateMACD(
          closes,
          params.fastPeriod,
          params.slowPeriod,
          params.signalPeriod
        )
        // 返回复合指标数据
        return {
          macd_fast: macdResult.macdLine,
          macd_signal: macdResult.signalLine,
          macd_hist: macdResult.histogram
        }
      
      case 'bollinger':
        const bbResult = calculateBollingerBands(
          closes,
          params.period,
          params.stdDev
        )
        // 返回复合指标数据
        return {
          bollinger_upper: bbResult.upper,
          bollinger_middle: bbResult.middle,
          bollinger_lower: bbResult.lower
        }
      
      case 'rsi':
        return calculateRSI(closes, params.period)
      
      case 'kdj':
        const kdjResult = calculateKDJ(
          highs,
          lows,
          closes,
          params.period,
          params.kPeriod,
          params.dPeriod
        )
        // 返回复合指标数据
        return {
          kdj_k: kdjResult.k,
          kdj_d: kdjResult.d,
          kdj_j: kdjResult.j
        }
      
      default:
        console.warn(`Unknown indicator type: ${indicator.type}`)
        return null
    }
  }

  /**
   * 计算指定图表的指标
   * @param {Array} data - 原始数据数组
   * @param {string} chartType - 图表类型
   * @returns {Object} - 指标数据对象
   */
  calculateForChart(data, chartType) {
    const indicators = indicatorRegistry.getByChartType(chartType)
    const indicatorIds = indicators.map(i => i.id)
    return this.calculateAll(data, indicatorIds)
  }
}

/**
 * 创建全局指标计算器实例
 */
export const indicatorCalculator = new IndicatorCalculator()
