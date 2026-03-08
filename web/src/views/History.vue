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
          <el-select v-model="queryParams.symbol" placeholder="请选择ETF代码" style="width: 150px" filterable>
            <el-option
              v-for="item in etfCodes"
              :key="item.code"
              :label="item.code"
              :value="item.code"
            >
              <span>{{ item.code }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">{{ item.name }}</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-input v-model="queryParams.startDate" placeholder="不填则从最开始" style="width: 140px" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-input v-model="queryParams.endDate" placeholder="不填则至最新" style="width: 140px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData" :loading="loading">查询</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="displayData" style="width: 100%" v-loading="loading" table-layout="auto">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="open" label="开盘" width="100" />
        <el-table-column prop="high" label="最高" width="100" />
        <el-table-column prop="low" label="最低" width="100" />
        <el-table-column prop="close" label="收盘" width="100" />
        <el-table-column prop="volume" label="成交量" min-width="150" />
        <el-table-column prop="amount" label="成交额" min-width="150" />
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, sizes, prev, pager, next"
        :page-sizes="[10, 13, 20, 50, 100]"
        style="margin-top: 20px; justify-content: flex-end"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { historyAPI } from '@/api/endpoints'
import { realtimeAPI } from '@/api/endpoints'
import { databaseAPI } from '@/api/endpoints'

const queryParams = ref({
  symbol: '510300',
  startDate: '',
  endDate: ''
})

const historyData = ref([])
const etfCodes = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(13)
const total = ref(0)

const displayData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return historyData.value.slice(start, end)
})

onMounted(() => {
  loadEtfcodes()
})

const loadEtfcodes = async () => {
  try {
    const response = await databaseAPI.getETFList({})
    if (response.success) {
      const codes = response.data.map(item => ({
        code: item.code,
        name: item.name
      }))
      etfCodes.value = codes
    }
  } catch (error) {
    console.error('加载ETF代码失败:', error)
  }
}

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
      currentPage.value = 1
    }
  } catch (error) {
    console.error('加载历史数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-table {
  width: 100%;
}

.el-table .el-table__body-wrapper {
  width: 100%;
}
</style>
