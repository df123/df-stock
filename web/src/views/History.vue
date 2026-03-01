<template>
  <div class="history">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>历史数据查询</span>
        </div>
      </template>
      
      <el-form :inline="true" :model="queryParams">
        <el-form-item label="ETF代码">
          <el-input v-model="queryParams.symbol" placeholder="例如: 510300" style="width: 150px" />
        </el-form-item>
        <el-form-item label="开始日期">
          <el-input v-model="queryParams.startDate" placeholder="20240101" style="width: 120px" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-input v-model="queryParams.endDate" placeholder="20240226" style="width: 120px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData" :loading="loading">查询</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="historyData" style="width: 100%" v-loading="loading">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="open" label="开盘" width="100" />
        <el-table-column prop="high" label="最高" width="100" />
        <el-table-column prop="low" label="最低" width="100" />
        <el-table-column prop="close" label="收盘" width="100" />
        <el-table-column prop="volume" label="成交量" width="150" />
        <el-table-column prop="amount" label="成交额" width="150" />
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, sizes, prev, pager, next"
        :page-sizes="[10, 20, 50, 100]"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { historyAPI } from '@/api/endpoints'

const queryParams = ref({
  symbol: '510300',
  startDate: '20240101',
  endDate: '20240226'
})

const historyData = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const loadData = async () => {
  loading.value = true
  try {
    const response = await historyAPI.get(
      queryParams.value.symbol,
      queryParams.value.startDate,
      queryParams.value.endDate
    )
    if (response.success) {
      historyData.value = response.data
      total.value = response.data.length
    }
  } catch (error) {
    console.error('加载历史数据失败:', error)
  } finally {
    loading.value = false
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
