<template>
  <div class="database">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据库管理</span>
          <el-button type="primary" @click="loadStats" :loading="loading">刷新</el-button>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="实时数据" :value="stats.etf_realtime" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="历史数据" :value="stats.etf_history" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="筛选结果" :value="stats.screening_results" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="回测结果" :value="stats.backtest_results" />
        </el-col>
      </el-row>
      
      <el-divider />
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="数据统计" name="stats">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="实时数据记录数">{{ stats.etf_realtime }}</el-descriptions-item>
            <el-descriptions-item label="历史数据记录数">{{ stats.etf_history }}</el-descriptions-item>
            <el-descriptions-item label="唯一ETF代码数">{{ stats.unique_history_codes }}</el-descriptions-item>
            <el-descriptions-item label="实时数据日期范围">{{ stats.realtime_date_range }}</el-descriptions-item>
            <el-descriptions-item label="历史数据日期范围">{{ stats.history_date_range }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        
        <el-tab-pane label="实时数据预览" name="realtime">
          <el-table :data="realtimeData" style="width: 100%" max-height="400">
            <el-table-column prop="code" label="代码" width="100" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="price" label="最新价" width="100" />
            <el-table-column prop="change_percent" label="涨跌幅(%)" width="100" />
            <el-table-column prop="snapshot_date" label="快照日期" width="120" />
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="历史数据预览" name="history">
          <el-table :data="historyData" style="width: 100%" max-height="400">
            <el-table-column prop="code" label="代码" width="100" />
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="close" label="收盘" width="100" />
            <el-table-column prop="volume" label="成交量" width="150" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { databaseAPI } from '@/api/endpoints'

const activeTab = ref('stats')
const stats = ref({})
const realtimeData = ref([])
const historyData = ref([])
const loading = ref(false)

onMounted(() => {
  loadStats()
  loadRealtimeData()
  loadHistoryData()
})

const loadStats = async () => {
  loading.value = true
  try {
    const response = await databaseAPI.getStats()
    if (response.success) {
      stats.value = response.data
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

const loadRealtimeData = async () => {
  try {
    const response = await databaseAPI.queryRealtime({ limit: 10 })
    if (response.success) {
      realtimeData.value = response.data
    }
  } catch (error) {
    console.error('加载实时数据失败:', error)
  }
}

const loadHistoryData = async () => {
  try {
    const response = await databaseAPI.queryHistory({ limit: 10 })
    if (response.success) {
      historyData.value = response.data
    }
  } catch (error) {
    console.error('加载历史数据失败:', error)
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
