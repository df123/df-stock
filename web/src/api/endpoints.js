import api from './index'

export const realtimeAPI = {
  getAll: () => api.get('/realtime'),
  getBySymbol: (symbol) => api.get(`/realtime/${symbol}`),
  getTopGainers: (limit) => api.get(`/realtime/top/gainers?limit=${limit}`),
  getTopLosers: (limit) => api.get(`/realtime/top/losers?limit=${limit}`),
  search: (keyword, limit) => api.get(`/realtime/search?keyword=${keyword}&limit=${limit}`)
}

export const databaseAPI = {
  getStats: () => api.get('/db/stats'),
  getETFList: (params) => api.get('/db/etf_list', { params }),
  queryRealtime: (params) => api.get('/db/query/etf_realtime', { params }),
  queryHistory: (params) => api.get('/db/query/etf_history', { params }),
  queryScreening: (params) => api.get('/db/query/screening_results', { params }),
  queryBacktest: (params) => api.get('/db/query/backtest_results', { params }),
  export: (table) => api.get(`/db/export/${table}`),
  incrementalUpdate: (params) => api.post('/db/update/incremental', null, { params }),
  getUpdateStatus: () => api.get('/db/update/status')
}

export const screeningAPI = {
  getCombined: (params) => api.get('/screening/combined', { params }),
  getMACD: (params) => api.get('/screening/macd', { params }),
  getBollinger: (params) => api.get('/screening/bollinger', { params }),
  getVolume: (params) => api.get('/screening/volume', { params })
}

export const backtestAPI = {
  run: (params) => api.post('/backtest/run', null, { params }),
  getProgress: (taskId) => api.get(`/backtest/progress/${taskId}`),
  getStrategies: () => api.get('/backtest/strategies')
}
