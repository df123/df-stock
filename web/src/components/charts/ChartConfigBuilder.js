/**
 * 图表配置构建器模块
 * 负责构建 ECharts 配置
 */

import { ChartType } from './IndicatorConfig.js'
import { indicatorRegistry } from './IndicatorRegistry.js'
import { getChartTheme, getIndicatorColor, getReferenceLines } from './ChartTheme.js'

/**
 * 图表配置构建器类
 * 负责构建 ECharts 配置
 */
export class ChartConfigBuilder {
  /**
   * @param {Object} chartManager - 图表管理器实例（用于获取响应式状态）
   */
  constructor(chartManager = null) {
    this.chartManager = chartManager
  }

  /**
   * 构建图表配置
   * @param {ChartType} chartType - 图表类型
   * @param {Object} data - 图表数据
   * @param {Object} options - 可选配置
   * @returns {Object} ECharts 配置对象
   */
  build(chartType, data, options = {}) {
    const theme = getChartTheme(chartType)
    const baseConfig = this._getBaseConfig(theme, options)
    const seriesConfig = this._buildSeries(chartType, data, theme)
    const legendConfig = this._buildLegend(chartType, theme)
    const xAxisConfig = this._buildXAxis(data.dates, theme)
    const yAxisConfig = this._buildYAxis(chartType, theme)
    const tooltipConfig = this._buildTooltip(chartType, theme)
    const dataZoomConfig = this._buildDataZoom(theme)

    return {
      ...baseConfig,
      legend: legendConfig,
      xAxis: xAxisConfig,
      yAxis: yAxisConfig,
      tooltip: tooltipConfig,
      dataZoom: dataZoomConfig,
      series: seriesConfig
    }
  }

  /**
   * 构建主图表配置
   * @param {Object} data - 图表数据
   * @param {Object} options - 可选配置
   * @returns {Object} ECharts 配置对象
   */
  buildMainChartOption(data, options = {}) {
    return this.build(ChartType.MAIN, data, options)
  }

  /**
   * 构建指标图表配置
   * @param {ChartType} chartType - 图表类型
   * @param {Object} data - 图表数据
   * @param {Object} options - 可选配置
   * @returns {Object} ECharts 配置对象
   */
  buildIndicatorChartOption(chartType, data, options = {}) {
    return this.build(chartType, data, options)
  }

  /**
   * 构建系列配置
   * @private
   * @param {ChartType} chartType - 图表类型
   * @param {Object} data - 图表数据
   * @param {Object} theme - 主题配置
   * @returns {Array} 系列配置数组
   */
  _buildSeries(chartType, data, theme) {
    const indicators = indicatorRegistry.getByChartType(chartType)
    const series = []

    // 添加价格系列（仅主图表）
    if (chartType === ChartType.MAIN) {
      series.push({
        name: '收盘价',
        type: 'line',
        data: data.closes,
        smooth: true,
        itemStyle: { color: theme.colors.price },
        lineStyle: { width: 2 },
        symbol: 'circle',
        symbolSize: 4
      })
    }

    // 添加指标系列
    indicators.forEach(indicator => {
      // 检查是否是复合指标
      if (indicator.subIndicators && Array.isArray(indicator.subIndicators)) {
        // 处理复合指标：为每个子指标添加系列
        indicator.subIndicators.forEach(subIndicator => {
          const subIndicatorData = data[subIndicator.id]
          if (subIndicatorData) {
            series.push({
              name: subIndicator.name,
              type: subIndicator.seriesType,
              data: subIndicatorData,
              ...subIndicator.seriesConfig,
              symbol: 'circle',
              symbolSize: 4
            })
          }
        })
      } else {
        // 处理简单指标
        const indicatorData = data[indicator.id]
        if (indicatorData) {
          series.push({
            name: indicator.name,
            type: indicator.seriesType,
            data: indicatorData,
            ...indicator.seriesConfig,
            symbol: 'circle',
            symbolSize: 4
          })
        }
      }
    })

    return series
  }

  /**
   * 构建图例配置（支持响应式）
   * @private
   * @param {ChartType} chartType - 图表类型
   * @param {Object} theme - 主题配置
   * @returns {Object} 图例配置对象
   */
  _buildLegend(chartType, theme) {
    const indicators = indicatorRegistry.getByChartType(chartType)
    const data = []
    
    // 添加价格系列（仅主图表）
    if (chartType === ChartType.MAIN) {
      data.push('收盘价')
    }
    
    // 添加指标系列
    indicators.forEach(indicator => {
      // 检查是否是复合指标
      if (indicator.subIndicators && Array.isArray(indicator.subIndicators)) {
        // 复合指标：添加所有子指标的名称
        indicator.subIndicators.forEach(subIndicator => {
          data.push(subIndicator.name)
        })
      } else {
        // 简单指标：添加指标名称
        data.push(indicator.name)
      }
    })
    
    // 如果有图表管理器，获取响应式状态
    let selected = {}
    if (this.chartManager) {
      selected = this.chartManager.getVisibleStates(chartType)
    } else {
      // 否则使用默认状态
      data.forEach(name => {
        selected[name] = true
      })
    }
    
    return {
      ...theme.legend,
      data,
      selected
    }
  }

  /**
   * 构建Tooltip配置（优化数据点提示）
   * @private
   * @param {ChartType} chartType - 图表类型
   * @param {Object} theme - 主题配置
   * @returns {Object} Tooltip配置对象
   */
  _buildTooltip(chartType, theme) {
    return {
      ...theme.tooltip,
      formatter: (params) => this._tooltipFormatter(params)
    }
  }

  /**
   * Tooltip格式化函数
   * @private
   * @param {Array} params - ECharts tooltip参数数组
   * @returns {string} 格式化的HTML字符串
   */
  _tooltipFormatter(params) {
    if (!params || params.length === 0) return ''
    
    let result = `<div style="padding: 4px 0;">`
    result += `<div style="font-weight: bold; margin-bottom: 8px;">${params[0].axisValue}</div>`
    
    params.forEach(param => {
      if (param.value !== null && param.value !== undefined) {
        const value = Number(param.value).toFixed(3)
        result += `<div style="display: flex; align-items: center; margin: 4px 0;">`
        result += `<span style="display: inline-block; width: 10px; height: 10px; background-color: ${param.color}; margin-right: 8px; border-radius: 50%;"></span>`
        result += `<span style="flex: 1;">${param.seriesName}</span>`
        result += `<span style="font-weight: bold; margin-left: 8px;">${value}</span>`
        result += `</div>`
      }
    })
    
    result += `</div>`
    return result
  }

  /**
   * 构建X轴配置
   * @private
   * @param {Array} dates - 日期数组
   * @param {Object} theme - 主题配置
   * @returns {Object} X轴配置对象
   */
  _buildXAxis(dates, theme) {
    return {
      ...theme.axis.xAxis,
      data: dates,
      scale: true
    }
  }

  /**
   * 构建Y轴配置
   * @private
   * @param {ChartType} chartType - 图表类型
   * @param {Object} theme - 主题配置
   * @returns {Object} Y轴配置对象
   */
  _buildYAxis(chartType, theme) {
    const config = {
      ...theme.axis.yAxis
    }

    // RSI 和 KDJ 有固定的范围
    if (chartType === ChartType.RSI || chartType === ChartType.KDJ) {
      config.min = 0
      config.max = 100
    }

    return config
  }

  /**
   * 构建DataZoom配置
   * @private
   * @param {Object} theme - 主题配置
   * @returns {Array} DataZoom配置数组
   */
  _buildDataZoom(theme) {
    return theme.dataZoom
  }

  /**
   * 获取基础配置
   * @private
   * @param {Object} theme - 主题配置
   * @param {Object} options - 可选配置
   * @returns {Object} 基础配置对象
   */
  _getBaseConfig(theme, options) {
    return {
      grid: theme.grid,
      animation: options.animation !== false ? theme.animation.enabled : false,
      animationDuration: theme.animation.duration,
      animationEasing: theme.animation.easing
    }
  }
}

/**
 * 创建全局图表配置构建器实例
 */
export const chartConfigBuilder = new ChartConfigBuilder()
