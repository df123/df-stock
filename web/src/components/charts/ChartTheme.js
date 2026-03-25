/**
 * 图表主题配置模块
 * 定义图表主题、颜色方案、样式配置
 */

/**
 * 默认图表主题配置
 */
export const defaultChartTheme = {
  // 颜色方案
  colors: {
    // 主图表颜色
    price: '#5470c6',
    bollingerUpper: '#ee6666',
    bollingerMiddle: '#91cc75',
    bollingerLower: '#ee6666',
    
    // MACD 颜色
    macdFast: '#5470c6',
    macdSignal: '#fac858',
    macdHistogramPositive: '#91cc75',
    macdHistogramNegative: '#ee6666',
    
    // RSI 颜色
    rsi: '#73c0de',
    rsiOverbought: '#ee6666',
    rsiOversold: '#91cc75',
    
    // KDJ 颜色
    kdjK: '#5470c6',
    kdjD: '#fac858',
    kdjJ: '#ee6666',
    
    // 通用颜色
    background: '#ffffff',
    text: '#333333',
    grid: '#e0e0e0',
    axisLine: '#999999',
    splitLine: '#e0e0e0'
  },
  
  // 线条样式
  lineStyles: {
    // 主线条
    main: {
      width: 2,
      type: 'solid',
      opacity: 1
    },
    
    // 辅助线条
    auxiliary: {
      width: 1,
      type: 'dashed',
      opacity: 0.7
    },
    
    // 参考线
    reference: {
      width: 1,
      type: 'dotted',
      opacity: 0.5
    }
  },
  
  // 坐标轴配置
  axis: {
    // X轴配置
    xAxis: {
      type: 'category',
      boundaryGap: false,
      axisLine: {
        show: true,
        lineStyle: {
          color: '#999999',
          width: 1
        }
      },
      axisTick: {
        show: true,
        alignWithLabel: true
      },
      axisLabel: {
        show: true,
        color: '#333333',
        fontSize: 12,
        rotate: 0
      },
      splitLine: {
        show: false
      }
    },
    
    // Y轴配置
    yAxis: {
      type: 'value',
      scale: true,
      axisLine: {
        show: true,
        lineStyle: {
          color: '#999999',
          width: 1
        }
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        show: true,
        color: '#333333',
        fontSize: 12,
        formatter: '{value}'
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: '#e0e0e0',
          width: 1,
          type: 'dashed'
        }
      }
    }
  },
  
  // 图例配置
  legend: {
    show: true,
    type: 'scroll',
    orient: 'horizontal',
    align: 'auto',
    left: 'center',
    top: 10,
    padding: [5, 10, 5, 10],
    itemGap: 15,
    itemWidth: 25,
    itemHeight: 14,
    textStyle: {
      color: '#333333',
      fontSize: 12,
      fontWeight: 'normal'
    },
    selectedMode: true,
    inactiveColor: '#cccccc'
  },
  
  // Tooltip配置
  tooltip: {
    show: true,
    trigger: 'axis',
    confine: true,
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#999999',
    borderWidth: 1,
    textStyle: {
      color: '#333333',
      fontSize: 12
    },
    axisPointer: {
      type: 'cross',
      label: {
        backgroundColor: '#6a7985',
        color: '#ffffff',
        fontSize: 11,
        padding: [4, 8]
      },
      lineStyle: {
        color: '#999999',
        width: 1,
        type: 'dashed'
      },
      crossStyle: {
        color: '#999999',
        width: 1,
        type: 'dashed'
      }
    },
    padding: [8, 12],
    position: (point, params, dom, rect, size) => {
      // 自动调整位置，避免超出边界
      const [x, y] = point
      const boxWidth = size.contentSize[0]
      const boxHeight = size.contentSize[1]
      const posX = x + boxWidth > size.viewSize[0] ? x - boxWidth - 10 : x + 10
      const posY = y + boxHeight > size.viewSize[1] ? y - boxHeight - 10 : y + 10
      return [posX, posY]
    }
  },
  
  // DataZoom配置
  dataZoom: [
    {
      type: 'inside',
      start: 50,
      end: 100,
      zoomLock: false,
      moveOnMouseMove: true,
      moveOnMouseWheel: false,
      preventDefaultMouseMove: false
    },
    {
      show: true,
      type: 'slider',
      top: '90%',
      start: 50,
      end: 100,
      height: 20,
      borderColor: '#999999',
      fillerColor: 'rgba(84, 112, 198, 0.2)',
      backgroundColor: '#f5f5f5',
      handleStyle: {
        color: '#5470c6',
        borderColor: '#5470c6'
      },
      textStyle: {
        color: '#333333'
      },
      borderColor: '#999999'
    }
  ],
  
  // Grid配置
  grid: {
    left: '3%',
    right: '3%',
    top: '15%',
    bottom: '15%',
    containLabel: true,
    backgroundColor: 'transparent',
    borderColor: '#e0e0e0',
    borderWidth: 0
  },
  
  // 动画配置
  animation: {
    enabled: true,
    duration: 1000,
    easing: 'cubicOut'
  }
}

/**
 * 图表特定主题配置
 */
export const chartSpecificThemes = {
  // 主图表主题
  main: {
    ...defaultChartTheme,
    yAxis: {
      ...defaultChartTheme.axis.yAxis,
      scale: true,
      splitNumber: 5
    },
    grid: {
      ...defaultChartTheme.grid,
      top: '15%',
      bottom: '20%'
    }
  },
  
  // MACD图表主题
  macd: {
    ...defaultChartTheme,
    yAxis: {
      ...defaultChartTheme.axis.yAxis,
      scale: true,
      splitNumber: 5
    },
    grid: {
      ...defaultChartTheme.grid,
      top: '15%',
      bottom: '20%'
    }
  },
  
  // RSI图表主题
  rsi: {
    ...defaultChartTheme,
    yAxis: {
      ...defaultChartTheme.axis.yAxis,
      scale: false,
      min: 0,
      max: 100,
      splitNumber: 5
    },
    grid: {
      ...defaultChartTheme.grid,
      top: '15%',
      bottom: '20%'
    }
  },
  
  // KDJ图表主题
  kdj: {
    ...defaultChartTheme,
    yAxis: {
      ...defaultChartTheme.axis.yAxis,
      scale: false,
      min: 0,
      max: 100,
      splitNumber: 5
    },
    grid: {
      ...defaultChartTheme.grid,
      top: '15%',
      bottom: '20%'
    }
  }
}

/**
 * 获取指定图表类型的主题配置
 * @param {string} chartType - 图表类型
 * @returns {Object} 主题配置对象
 */
export function getChartTheme(chartType) {
  return chartSpecificThemes[chartType] || defaultChartTheme
}

/**
 * 获取指定指标的颜色配置
 * @param {string} indicatorId - 指标ID
 * @returns {string} 颜色值
 */
export function getIndicatorColor(indicatorId) {
  const colorMap = {
    'bollinger_upper': defaultChartTheme.colors.bollingerUpper,
    'bollinger_middle': defaultChartTheme.colors.bollingerMiddle,
    'bollinger_lower': defaultChartTheme.colors.bollingerLower,
    'macd_fast': defaultChartTheme.colors.macdFast,
    'macd_signal': defaultChartTheme.colors.macdSignal,
    'macd_hist': (params) => {
      return params.value >= 0 
        ? defaultChartTheme.colors.macdHistogramPositive 
        : defaultChartTheme.colors.macdHistogramNegative
    },
    'rsi': defaultChartTheme.colors.rsi,
    'kdj_k': defaultChartTheme.colors.kdjK,
    'kdj_d': defaultChartTheme.colors.kdjD,
    'kdj_j': defaultChartTheme.colors.kdjJ
  }
  
  return colorMap[indicatorId] || defaultChartTheme.colors.price
}

/**
 * 获取参考线配置（用于RSI、KDJ等有固定范围的指标）
 * @param {string} indicatorType - 指标类型
 * @returns {Array} 参考线配置数组
 */
export function getReferenceLines(indicatorType) {
  const referenceLines = {
    rsi: [
      {
        yAxis: 70,
        name: '超买线',
        lineStyle: {
          color: defaultChartTheme.colors.rsiOverbought,
          type: 'dashed',
          width: 1
        },
        label: {
          show: true,
          position: 'end',
          formatter: '70',
          color: defaultChartTheme.colors.rsiOverbought,
          fontSize: 10
        }
      },
      {
        yAxis: 30,
        name: '超卖线',
        lineStyle: {
          color: defaultChartTheme.colors.rsiOversold,
          type: 'dashed',
          width: 1
        },
        label: {
          show: true,
          position: 'end',
          formatter: '30',
          color: defaultChartTheme.colors.rsiOversold,
          fontSize: 10
        }
      }
    ],
    kdj: [
      {
        yAxis: 80,
        name: '超买线',
        lineStyle: {
          color: defaultChartTheme.colors.rsiOverbought,
          type: 'dashed',
          width: 1
        },
        label: {
          show: true,
          position: 'end',
          formatter: '80',
          color: defaultChartTheme.colors.rsiOverbought,
          fontSize: 10
        }
      },
      {
        yAxis: 20,
        name: '超卖线',
        lineStyle: {
          color: defaultChartTheme.colors.rsiOversold,
          type: 'dashed',
          width: 1
        },
        label: {
          show: true,
          position: 'end',
          formatter: '20',
          color: defaultChartTheme.colors.rsiOversold,
          fontSize: 10
        }
      }
    ]
  }
  
  return referenceLines[indicatorType] || []
}
