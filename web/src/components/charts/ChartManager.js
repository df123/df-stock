/**
 * 图表管理器模块
 * 负责管理图表实例的生命周期，包括创建、更新、销毁和响应式线条控制
 */

import { reactive } from 'vue'
import { indicatorRegistry } from './IndicatorRegistry.js'

/**
 * 图表管理器类
 * 负责管理多个图表实例，处理响应式线条控制
 */
export class ChartManager {
  constructor() {
    // 图表实例映射
    this.charts = new Map() // chartId -> ECharts instance
    
    // 响应式线条可见性状态
    this.visibleStates = reactive({})
    
    // 图表引用映射
    this.chartRefs = new Map() // chartId -> ref
    
    // 事件监听器映射
    this.eventListeners = new Map() // chartId -> Array<{event: string, handler: Function}>
    
    // 图表配置映射
    this.chartConfigs = new Map() // chartId -> Object
  }

  /**
   * 创建图表实例
   * @param {string} chartId - 图表唯一标识
   * @param {Object} chartRef - 图表DOM引用
   * @param {Function} echartsInit - ECharts初始化函数
   * @param {Object} options - 可选配置
   * @param {string} options.chartType - 图表类型（用于关联指标）
   * @param {Object} options.theme - 图表主题配置
   * @returns {Object|null} ECharts实例，如果创建失败则返回null
   * @throws {Error} 如果图表ID已存在则抛出错误
   */
  createChart(chartId, chartRef, echartsInit, options = {}) {
    if (!chartId || typeof chartId !== 'string') {
      throw new Error('图表ID无效')
    }

    if (this.charts.has(chartId)) {
      throw new Error(`图表 ${chartId} 已存在`)
    }

    if (!chartRef || !chartRef.value) {
      console.error(`图表 ${chartId} 的DOM引用无效`)
      return null
    }

    // 保存图表引用
    this.chartRefs.set(chartId, chartRef)
    
    // 创建图表实例
    let chart
    try {
      if (options.theme) {
        chart = echartsInit(chartRef.value, options.theme)
      } else {
        chart = echartsInit(chartRef.value)
      }
    } catch (error) {
      console.error(`创建图表 ${chartId} 失败:`, error)
      return null
    }

    this.charts.set(chartId, chart)
    this.chartConfigs.set(chartId, options)

    // 初始化可见性状态
    if (options.chartType) {
      const indicators = indicatorRegistry.getByChartType(options.chartType)
      indicators.forEach(indicator => {
        // 检查是否是复合指标
        if (indicator.subIndicators && Array.isArray(indicator.subIndicators)) {
          // 复合指标：初始化所有子指标的可见性状态
          indicator.subIndicators.forEach(subIndicator => {
            if (!this.visibleStates.hasOwnProperty(subIndicator.id)) {
              this.visibleStates[subIndicator.id] = indicatorRegistry.getVisibility(subIndicator.id)
            }
          })
        } else {
          // 简单指标：初始化指标的可见性状态
          if (!this.visibleStates.hasOwnProperty(indicator.id)) {
            this.visibleStates[indicator.id] = indicatorRegistry.getVisibility(indicator.id)
          }
        }
      })
    }

    return chart
  }

  /**
   * 获取图表实例
   * @param {string} chartId - 图表ID
   * @returns {Object|null} ECharts实例，如果不存在则返回null
   */
  getChart(chartId) {
    return this.charts.get(chartId) || null
  }

  /**
   * 更新图表配置
   * @param {string} chartId - 图表ID
   * @param {Object} config - ECharts配置对象
   * @param {Object} options - 可选配置
   * @param {boolean} options.notMerge - 是否不合并配置，默认false
   * @param {boolean} options.lazyUpdate - 是否延迟更新，默认false
   * @returns {boolean} 是否更新成功
   */
  updateChart(chartId, config, options = {}) {
    const chart = this.charts.get(chartId)
    if (!chart) {
      console.error(`图表 ${chartId} 不存在`)
      return false
    }

    try {
      chart.setOption(config, {
        notMerge: options.notMerge ?? false,
        lazyUpdate: options.lazyUpdate ?? false
      })
      return true
    } catch (error) {
      console.error(`更新图表 ${chartId} 失败:`, error)
      return false
    }
  }

  /**
   * 销毁图表实例
   * @param {string} chartId - 图表ID
   * @returns {boolean} 是否销毁成功
   */
  disposeChart(chartId) {
    const chart = this.charts.get(chartId)
    if (!chart) {
      return false
    }

    try {
      // 移除所有事件监听器
      const listeners = this.eventListeners.get(chartId) || []
      listeners.forEach(({ event, handler }) => {
        chart.off(event, handler)
      })
      this.eventListeners.delete(chartId)

      // 销毁图表实例
      chart.dispose()
      
      // 清理映射
      this.charts.delete(chartId)
      this.chartRefs.delete(chartId)
      this.chartConfigs.delete(chartId)
      
      return true
    } catch (error) {
      console.error(`销毁图表 ${chartId} 失败:`, error)
      return false
    }
  }

  /**
   * 销毁所有图表实例
   * @returns {number} 成功销毁的图表数量
   */
  disposeAll() {
    let count = 0
    this.charts.forEach((chart, chartId) => {
      if (this.disposeChart(chartId)) {
        count++
      }
    })
    return count
  }

  /**
   * 调整图表大小
   * @param {string} chartId - 图表ID
   * @returns {boolean} 是否调整成功
   */
  resize(chartId) {
    const chart = this.charts.get(chartId)
    if (!chart) {
      return false
    }

    try {
      chart.resize()
      return true
    } catch (error) {
      console.error(`调整图表 ${chartId} 大小失败:`, error)
      return false
    }
  }

  /**
   * 调整所有图表大小
   * @returns {number} 成功调整的图表数量
   */
  resizeAll() {
    let count = 0
    this.charts.forEach((chart, chartId) => {
      if (this.resize(chartId)) {
        count++
      }
    })
    return count
  }

  /**
   * 设置图例事件监听器（支持线条隐藏/显示）
   * @param {string} chartId - 图表ID
   * @param {Function} callback - 自定义回调函数，接收参数 (indicatorId, visible)
   * @returns {boolean} 是否设置成功
   */
  setLegendListener(chartId, callback = null) {
    const chart = this.charts.get(chartId)
    if (!chart) {
      console.error(`图表 ${chartId} 不存在`)
      return false
    }

    const chartConfig = this.chartConfigs.get(chartId)
    if (!chartConfig || !chartConfig.chartType) {
      console.error(`图表 ${chartId} 没有关联的图表类型`)
      return false
    }

    const chartType = chartConfig.chartType

    // 定义事件处理器
    const handler = (params) => {
      // 更新响应式状态
      const indicators = indicatorRegistry.getByChartType(chartType)
      indicators.forEach(indicator => {
        // 检查是否是复合指标
        if (indicator.subIndicators && Array.isArray(indicator.subIndicators)) {
          // 复合指标：检查子指标
          indicator.subIndicators.forEach(subIndicator => {
            if (subIndicator.name === params.name) {
              this.visibleStates[subIndicator.id] = params.selected
              // 同步更新注册表中的状态
              indicatorRegistry.updateVisibility(subIndicator.id, params.selected)
              
              // 执行自定义回调
              if (callback && typeof callback === 'function') {
                callback(subIndicator.id, params.selected)
              }
            }
          })
        } else {
          // 简单指标
          if (indicator.name === params.name) {
            this.visibleStates[indicator.id] = params.selected
            // 同步更新注册表中的状态
            indicatorRegistry.updateVisibility(indicator.id, params.selected)
            
            // 执行自定义回调
            if (callback && typeof callback === 'function') {
              callback(indicator.id, params.selected)
            }
          }
        }
      })
    }

    // 移除已存在的监听器
    const existingListeners = this.eventListeners.get(chartId) || []
    const legendListeners = existingListeners.filter(l => l.event === 'legendselectchanged')
    legendListeners.forEach(({ handler: existingHandler }) => {
      chart.off('legendselectchanged', existingHandler)
    })

    // 添加新监听器
    chart.on('legendselectchanged', handler)

    // 保存监听器
    const filteredListeners = existingListeners.filter(l => l.event !== 'legendselectchanged')
    filteredListeners.push({ event: 'legendselectchanged', handler })
    this.eventListeners.set(chartId, filteredListeners)

    return true
  }

  /**
   * 获取线条可见性状态
   * @param {string} indicatorId - 指标ID
   * @returns {boolean} 线条是否可见
   */
  getLineVisibility(indicatorId) {
    return this.visibleStates[indicatorId] ?? true
  }

  /**
   * 设置线条可见性状态
   * @param {string} indicatorId - 指标ID
   * @param {boolean} visible - 是否可见
   * @returns {boolean} 是否设置成功
   */
  setLineVisibility(indicatorId, visible) {
    if (!indicatorId || typeof indicatorId !== 'string') {
      return false
    }

    // 更新响应式状态
    this.visibleStates[indicatorId] = !!visible

    // 同步更新注册表中的状态
    indicatorRegistry.updateVisibility(indicatorId, !!visible)

    // 更新所有关联图表的 legend 配置
    this.charts.forEach((chart, chartId) => {
      const chartConfig = this.chartConfigs.get(chartId)
      if (chartConfig && chartConfig.chartType) {
        const indicators = indicatorRegistry.getByChartType(chartConfig.chartType)
        let found = false
        
        // 检查是否是简单指标
        const simpleIndicator = indicators.find(ind => ind.id === indicatorId)
        if (simpleIndicator) {
          found = true
        }
        
        // 检查是否是复合指标的子指标
        if (!found) {
          indicators.forEach(indicator => {
            if (indicator.subIndicators && Array.isArray(indicator.subIndicators)) {
              const subIndicator = indicator.subIndicators.find(sub => sub.id === indicatorId)
              if (subIndicator) {
                found = true
              }
            }
          })
        }
        
        if (found) {
          const legendConfig = indicatorRegistry.getLegendConfig(chartConfig.chartType)
          chart.setOption({
            legend: legendConfig
          })
        }
      }
    })

    return true
  }

  /**
   * 获取指定图表的所有线条可见性状态
   * @param {string} chartId - 图表ID
   * @returns {Object} { indicatorName: boolean }
   */
  getVisibleStates(chartId) {
    const chartConfig = this.chartConfigs.get(chartId)
    if (!chartConfig || !chartConfig.chartType) {
      return {}
    }

    const indicators = indicatorRegistry.getByChartType(chartConfig.chartType)
    const states = {}
    indicators.forEach(indicator => {
      // 检查是否是复合指标
      if (indicator.subIndicators && Array.isArray(indicator.subIndicators)) {
        // 复合指标：添加所有子指标的可见性状态
        indicator.subIndicators.forEach(subIndicator => {
          states[subIndicator.name] = this.visibleStates[subIndicator.id] ?? true
        })
      } else {
        // 简单指标：添加指标的可见性状态
        states[indicator.name] = this.visibleStates[indicator.id] ?? true
      }
    })
    return states
  }

  /**
   * 检查指标是否可见
   * @param {string} indicatorId - 指标ID
   * @returns {boolean}
   */
  isVisible(indicatorId) {
    return this.getLineVisibility(indicatorId)
  }

  /**
   * 获取已创建的图表数量
   * @returns {number}
   */
  size() {
    return this.charts.size
  }

  /**
   * 检查图表是否存在
   * @param {string} chartId - 图表ID
   * @returns {boolean}
   */
  has(chartId) {
    return this.charts.has(chartId)
  }

  /**
   * 获取所有图表ID
   * @returns {Array<string>}
   */
  getChartIds() {
    return Array.from(this.charts.keys())
  }
}

/**
 * 创建全局图表管理器实例
 */
export const chartManager = new ChartManager()
