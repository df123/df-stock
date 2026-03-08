import api from './index'

export const realtimeAPI = {
  getAll: () => api.get('/realtime'),
  getBySymbol: (symbol) => api.get(`/realtime/${symbol}`),
  getTopGainers: (limit) => api.get(`/realtime/top/gainers?limit=${limit}`),
  getTopLosers: (limit) => api.get(`/realtime/top/losers?limit=${limit}`),
  search: (keyword, limit) => api.get(`/realtime/search?keyword=${keyword}&limit=${limit}`)
}

export const historyAPI = {
  get: (symbol, startDate = null, endDate = null) => {
    let url = `/history/${symbol}`
    const params = []
    if (startDate) params.push(`start_date=${startDate}`)
    if (endDate) params.push(`end_date=${endDate}`)
    if (params.length > 0) url += `?${params.join('&')}`
    return api.get(url)
  },
  getWithIndicators: (symbol, startDate = null, endDate = null, indicators = 'all') => {
    let url = `/history/${symbol}/indicators`
    const params = []
    if (startDate) params.push(`start_date=${startDate}`)
    if (endDate) params.push(`end_date=${endDate}`)
    params.push(`indicators=${indicators}`)
    url += `?${params.join('&')}`
    return api.get(url)
  }
}

export const databaseAPI = {
  getStats: () => api.get('/db/stats'),
  getETFList: (params) => api.get('/db/etf_list', { params }),
  queryRealtime: (params) => api.get('/db/query/etf_realtime', { params }),
  queryHistory: (params) => api.get('/db/query/etf_history', { params }),
  queryScreening: (params) => api.get('/db/query/screening_results', { params }),
  queryBacktest: (params) => api.get('/db/query/backtest_results', { params }),
  export: (table) => api.get(`/db/export/${table}`)
}

export const screeningAPI = {
  getCombined: (params) => api.get('/screening/combined', { params }),
  getMACD: (params) => api.get('/screening/macd', { params }),
  getBollinger: (params) => api.get('/screening/bollinger', { params }),
  getVolume: (params) => api.get('/screening/volume', { params })
}
