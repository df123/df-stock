<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>数据库统计</span>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.etf_realtime || 0 }}</div>
                <div class="stat-label">实时数据</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.etf_history || 0 }}</div>
                <div class="stat-label">历史数据</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.unique_history_codes || 0 }}</div>
                <div class="stat-label">ETF代码数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.screening_results || 0 }}</div>
                <div class="stat-label">筛选结果</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>涨幅前5名</span>
            </div>
          </template>
          <el-table :data="topGainers" style="width: 100%">
            <el-table-column prop="code" label="代码" width="100" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="price" label="最新价" width="80" />
            <el-table-column prop="change_percent" label="涨跌幅(%)" width="100">
              <template #default="{ row }">
                <span style="color: red">{{ row.change_percent }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>跌幅前5名</span>
            </div>
          </template>
          <el-table :data="topLosers" style="width: 100%">
            <el-table-column prop="code" label="代码" width="100" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="price" label="最新价" width="80" />
            <el-table-column prop="change_percent" label="涨跌幅(%)" width="100">
              <template #default="{ row }">
                <span style="color: green">{{ row.change_percent }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { databaseAPI } from '@/api/endpoints'
import { realtimeAPI } from '@/api/endpoints'

const stats = ref({})
const topGainers = ref([])
const topLosers = ref([])

onMounted(async () => {
  await loadStats()
  await loadTopData()
})

const loadStats = async () => {
  try {
    const response = await databaseAPI.getStats()
    if (response.success) {
      stats.value = response.data
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadTopData = async () => {
  try {
    const [gainersRes, losersRes] = await Promise.all([
      realtimeAPI.getTopGainers(5),
      realtimeAPI.getTopLosers(5)
    ])
    
    if (gainersRes.success) {
      topGainers.value = gainersRes.data
    }
    if (losersRes.success) {
      topLosers.value = losersRes.data
    }
  } catch (error) {
    console.error('加载排行榜数据失败:', error)
  }
}
</script>

<style scoped>
.stat-item {
  text-align: center;
  padding: 20px 0;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
