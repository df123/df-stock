<template>
  <div class="realtime">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>实时行情</span>
          <el-button type="primary" @click="loadData" :loading="loading">刷新</el-button>
        </div>
      </template>
      
      <el-input
        v-model="searchKeyword"
        placeholder="搜索ETF代码或名称"
        style="width: 300px; margin-bottom: 20px"
        @keyup.enter="search"
      >
        <template #append>
          <el-button icon="Search" @click="search" />
        </template>
      </el-input>
      
      <el-table :data="realtimeData" style="width: 100%" v-loading="loading">
        <el-table-column prop="code" label="代码" width="100" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="price" label="最新价" width="100" />
        <el-table-column prop="change_percent" label="涨跌幅(%)" width="100">
          <template #default="{ row }">
            <span :style="getColorStyle(row.change_percent)">
              {{ row.change_percent }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="change_amount" label="涨跌额" width="100" />
        <el-table-column prop="data_date" label="数据日期" width="120" />
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
        layout="total, sizes, prev, pager, next"
        :page-sizes="[10, 13, 20, 50, 100]"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { realtimeAPI } from '@/api/endpoints'

const realtimeData = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(13)
const total = ref(0)

onMounted(() => {
  loadData()
})

const allData = ref([])

const loadData = async () => {
  loading.value = true
  try {
    const response = await realtimeAPI.getAll()
    if (response.success) {
      allData.value = response.data
      total.value = response.data.length
      updateDisplayedData()
    }
  } catch (error) {
    console.error('加载实时数据失败:', error)
  } finally {
    loading.value = false
  }
}

const updateDisplayedData = () => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  realtimeData.value = allData.value.slice(start, end)
}

const search = async () => {
  if (!searchKeyword.value) {
    loadData()
    return
  }
  loading.value = true
  try {
    const response = await realtimeAPI.search(searchKeyword.value, 100)
    if (response.success) {
      realtimeData.value = response.data
      total.value = response.data.length
    }
  } catch (error) {
    console.error('搜索失败:', error)
  } finally {
    loading.value = false
  }
}

const getColorStyle = (value) => {
  if (!value) return ''
  const num = parseFloat(value)
  if (num > 0) return 'color: red'
  if (num < 0) return 'color: green'
  return ''
}

const handlePageChange = (page) => {
  currentPage.value = page
  updateDisplayedData()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  updateDisplayedData()
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
