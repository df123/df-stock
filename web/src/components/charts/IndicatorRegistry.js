/**
 * 指标注册表模块
 * 负责管理所有指标的注册、查询和配置
 */

import { IndicatorConfig, CompositeIndicatorConfig, defaultIndicators } from './IndicatorConfig.js'

/**
 * 指标注册表类
 * 负责管理所有指标的注册、查询和配置
 */
export class IndicatorRegistry {
  constructor() {
    this.indicators = new Map() // id -> IndicatorConfig|CompositeIndicatorConfig
    this.chartIndicators = new Map() // chartType -> Array<IndicatorConfig>
    this.visibleStates = new Map() // id -> boolean
  }

  /**
   * 注册指标
   * @param {IndicatorConfig|CompositeIndicatorConfig} indicator - 指标配置
   * @throws {Error} 如果指标已存在则抛出错误
   */
  register(indicator) {
    if (!indicator || !indicator.id) {
      throw new Error('指标配置无效：缺少 id 属性')
    }

    if (this.indicators.has(indicator.id)) {
      throw new Error(`指标 ${indicator.id} 已存在`)
    }

    if (indicator instanceof CompositeIndicatorConfig) {
      // 注册复合指标
      this.indicators.set(indicator.id, indicator)
      // 将复合指标添加到图表映射（不添加子指标）
      this._addToChartMap(indicator)
      
      // 注册子指标（但不添加到图表映射）
      indicator.subIndicators.forEach(sub => {
        if (this.indicators.has(sub.id)) {
          throw new Error(`子指标 ${sub.id} 已存在`)
        }
        this.indicators.set(sub.id, sub)
        this.visibleStates.set(sub.id, sub.visible ?? true)
      })
    } else {
      // 注册简单指标
      this.indicators.set(indicator.id, indicator)
      this._addToChartMap(indicator)
      this.visibleStates.set(indicator.id, indicator.visible ?? true)
    }
  }

  /**
   * 批量注册指标
   * @param {Array<IndicatorConfig|CompositeIndicatorConfig>} indicators - 指标配置数组
   * @throws {Error} 如果任一指标注册失败则抛出错误
   */
  registerBatch(indicators) {
    if (!Array.isArray(indicators)) {
      throw new Error('indicators 必须是数组')
    }

    indicators.forEach(indicator => {
      try {
        this.register(indicator)
      } catch (error) {
        throw new Error(`批量注册失败: ${error.message}`)
      }
    })
  }

  /**
   * 注销指标
   * @param {string} id - 指标ID
   * @returns {boolean} 是否成功注销
   */
  unregister(id) {
    if (!id || typeof id !== 'string') {
      return false
    }

    const indicator = this.indicators.get(id)
    if (!indicator) {
      return false
    }

    // 如果是复合指标，需要注销所有子指标
    if (indicator instanceof CompositeIndicatorConfig) {
      // 从图表映射中移除复合指标
      this._removeFromChartMap(indicator)
      // 注销子指标（但不从图表映射中移除，因为它们从未被添加）
      indicator.subIndicators.forEach(sub => {
        this.indicators.delete(sub.id)
        this.visibleStates.delete(sub.id)
      })
    } else {
      // 简单指标，从图表映射中移除
      this._removeFromChartMap(indicator)
    }

    this.indicators.delete(id)
    this.visibleStates.delete(id)
    return true
  }

  /**
   * 获取指标配置
   * @param {string} id - 指标ID
   * @returns {IndicatorConfig|CompositeIndicatorConfig|null}
   */
  get(id) {
    return this.indicators.get(id) || null
  }

  /**
   * 获取所有指标
   * @returns {Array<IndicatorConfig|CompositeIndicatorConfig>}
   */
  getAll() {
    return Array.from(this.indicators.values())
  }

  /**
   * 获取指定图表的所有指标
   * @param {string} chartType - 图表类型
   * @returns {Array<IndicatorConfig>}
   */
  getByChartType(chartType) {
    return this.chartIndicators.get(chartType) || []
  }

  /**
   * 检查指标是否已注册
   * @param {string} id - 指标ID
   * @returns {boolean}
   */
  has(id) {
    return this.indicators.has(id)
  }

  /**
   * 更新指标可见性
   * @param {string} id - 指标ID
   * @param {boolean} visible - 是否可见
   * @returns {boolean} 是否成功更新
   */
  updateVisibility(id, visible) {
    if (!this.indicators.has(id)) {
      return false
    }
    this.visibleStates.set(id, !!visible)
    return true
  }

  /**
   * 获取指标可见性
   * @param {string} id - 指标ID
   * @returns {boolean}
   */
  getVisibility(id) {
    return this.visibleStates.get(id) ?? true
  }

  /**
   * 获取指定图表的 legend 配置
   * @param {string} chartType - 图表类型
   * @returns {Object} legend 配置对象
   */
  getLegendConfig(chartType) {
    const indicators = this.getByChartType(chartType)
    const selected = {}
    const data = []

    indicators.forEach(indicator => {
      // 检查是否是复合指标
      if (indicator.subIndicators && Array.isArray(indicator.subIndicators)) {
        // 复合指标：添加所有子指标的名称和可见性
        indicator.subIndicators.forEach(subIndicator => {
          data.push(subIndicator.name)
          selected[subIndicator.name] = this.getVisibility(subIndicator.id)
        })
      } else {
        // 简单指标：添加指标名称和可见性
        data.push(indicator.name)
        selected[indicator.name] = this.getVisibility(indicator.id)
      }
    })

    return {
      show: true,
      data,
      selected
    }
  }

  /**
   * 清空所有指标
   */
  clear() {
    this.indicators.clear()
    this.chartIndicators.clear()
    this.visibleStates.clear()
  }

  /**
   * 获取已注册指标数量
   * @returns {number}
   */
  size() {
    return this.indicators.size
  }

  /**
   * 私有方法：添加到图表映射
   * @private
   * @param {IndicatorConfig} indicator - 指标配置
   */
  _addToChartMap(indicator) {
    const chartType = indicator.chartType
    if (!this.chartIndicators.has(chartType)) {
      this.chartIndicators.set(chartType, [])
    }
    this.chartIndicators.get(chartType).push(indicator)
  }

  /**
   * 私有方法：从图表映射中移除
   * @private
   * @param {IndicatorConfig} indicator - 指标配置
   */
  _removeFromChartMap(indicator) {
    const chartType = indicator.chartType
    const indicators = this.chartIndicators.get(chartType)
    if (indicators) {
      const index = indicators.findIndex(ind => ind.id === indicator.id)
      if (index !== -1) {
        indicators.splice(index, 1)
      }
      // 如果该图表类型没有指标了，删除映射
      if (indicators.length === 0) {
        this.chartIndicators.delete(chartType)
      }
    }
  }
}

/**
 * 创建全局指标注册表实例
 */
export const indicatorRegistry = new IndicatorRegistry()

/**
 * 注册默认指标
 * @returns {void}
 */
export function registerDefaultIndicators() {
  // 检查是否已经注册过指标，避免重复注册
  if (indicatorRegistry.size() > 0) {
    return
  }
  indicatorRegistry.registerBatch(defaultIndicators)
}

// 自动注册默认指标
registerDefaultIndicators()
