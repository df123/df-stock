import api from './index'

export const realtimeAPI = {
  getAll: () => api.get('/realtime'),
  getBySymbol: (symbol) => api.get(`/realtime/${symbol}`),
  getTopGainers: (limit) => api.get(`/realtime/top/gainers?limit=${limit}`),
  getTopLosers: (limit) => api.get(`/realtime/top/losers?limit=${limit}`),
  search: (keyword, limit) => api.get(`/realtime/search?keyword=${keyword}&limit=${limit}`)
}

export const historyAPI = {
  get: (symbol, startDate, endDate) => api.get(`/history/${symbol}?start_date=${startDate}&end_date=${endDate}`),
  getWithIndicators: (symbol, startDate, endDate, indicators) => 
    api.get(`/history/${symbol}/indicators?start_date=${startDate}&end_date=${endDate}&indicators=${indicators}`)
}

export const databaseAPI = {
  getStats: () => api.get('/db/stats'),
  queryRealtime: (params) => api.get('/db/query/etf_realtime', { params }),
  queryHistory: (params) => api.get('/db/query/etf_history', { params }),
  queryScreening: (params) => api.get('/db/query/screening_results', { params }),
  queryBacktest: (params) => api.get('/db/query/backtest_results', { params }),
  export: (table) => api.get(`/db/export/${table}`)
}
