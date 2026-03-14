<template>
  <div class="screening">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>策略筛选</span>
        </div>
      </template>
      
      <el-form :inline="true" :model="queryParams">
        <el-form-item label="策略类型">
          <el-select v-model="queryParams.strategyType" placeholder="选择策略" style="width: 150px">
            <el-option label="MACD+布林带" value="combined" />
            <el-option label="MACD" value="macd" />
            <el-option label="布林带" value="bollinger" />
            <el-option label="成交量" value="volume" />
          </el-select>
        </el-form-item>
        <el-form-item label="周期类型">
          <el-select v-model="queryParams.period" placeholder="选择周期" style="width: 120px">
            <el-option label="日线" value="daily" />
            <el-option label="周线" value="weekly" />
          </el-select>
        </el-form-item>
        <el-form-item label="筛选日期">
          <el-date-picker v-model="queryParams.endDate" type="date" placeholder="不填则今天" format="YYYY-MM-DD" value-format="YYYYMMDD" style="width: 150px" />
        </el-form-item>
        <el-form-item label="回溯天数">
          <el-input-number v-model="queryParams.lookbackDays" :min="20" :max="365" style="width: 120px" />
        </el-form-item>
        <el-form-item v-if="queryParams.strategyType === 'combined'">
          <el-checkbox v-model="queryParams.requireMacdGolden">要求MACD金叉</el-checkbox>
        </el-form-item>
        <el-form-item v-if="queryParams.strategyType === 'combined'">
          <el-checkbox v-model="queryParams.requireBbAboveMiddle">价格在布林带中轨之上</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="screen" :loading="loading">筛选</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="displayData" style="width: 100%" v-loading="loading" table-layout="auto">
        <el-table-column prop="code" label="代码" width="100">
          <template #default="{ row }">
            <el-link type="primary" :href="getFundUrl(row.code)" target="_blank" :underline="false">
              {{ row.code }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="200" />
        <el-table-column prop="signal_type" width="200">
          <template #header>
            <div style="display: flex; align-items: center; gap: 8px">
              <span>信号类型</span>
              <el-tooltip placement="top" effect="dark">
                <template #content>
                  <div style="line-height: 1.8; max-width: 300px">
                    <strong>信号类型说明：</strong><br/>
                    • <strong>组合信号</strong>：同时满足MACD金叉 + 价格在布林带中轨之上<br/>
                    • <strong>MACD金叉</strong>：MACD快线上穿信号线，看涨信号<br/>
                    • <strong>MACD死叉</strong>：MACD快线下穿信号线，看跌信号<br/>
                    • <strong>布林带突破上轨</strong>：价格突破布林带上轨<br/>
                    • <strong>布林带突破下轨</strong>：价格跌破布林带下轨<br/>
                    • <strong>布林带收缩</strong>：带宽较窄，可能即将突破<br/>
                    • <strong>高成交量</strong>：成交量异常放大
                  </div>
                </template>
                <el-icon style="cursor: help; color: #909399; font-size: 14px">
                  <QuestionFilled />
                </el-icon>
              </el-tooltip>
            </div>
          </template>
          <template #default="{ row }">
            {{ formatSignalType(row, null, row.signal_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="close" label="最新价" width="100" :formatter="formatNumber3" />
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column v-if="queryParams.strategyType === 'combined' || queryParams.strategyType === 'macd'" prop="macd_fast" label="MACD快线" width="100" :formatter="formatNumber3" />
        <el-table-column v-if="queryParams.strategyType === 'combined' || queryParams.strategyType === 'macd'" prop="macd_signal" label="MACD信号线" width="110" :formatter="formatNumber3" />
        <el-table-column v-if="queryParams.strategyType === 'combined' || queryParams.strategyType === 'bollinger'" prop="bb_upper" label="布林带上轨" width="100" :formatter="formatNumber3" />
        <el-table-column v-if="queryParams.strategyType === 'combined' || queryParams.strategyType === 'bollinger'" prop="bb_middle" label="布林带中轨" width="100" :formatter="formatNumber3" />
        <el-table-column v-if="queryParams.strategyType === 'combined' || queryParams.strategyType === 'bollinger'" prop="bb_lower" label="布林带下轨" width="100" :formatter="formatNumber3" />
        <el-table-column v-if="queryParams.strategyType === 'combined' || queryParams.strategyType === 'bollinger'" prop="bb_position" label="布林带位置" width="110">
          <template #default="{ row }">
            {{ (row.bb_position * 100).toFixed(3) }}%
          </template>
        </el-table-column>
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
import { QuestionFilled } from '@element-plus/icons-vue'
import { screeningAPI } from '@/api/endpoints'

const queryParams = ref({
  strategyType: 'combined',
  period: 'daily',
  endDate: '',
  lookbackDays: 60,
  requireMacdGolden: true,
  requireBbAboveMiddle: true
})

const screeningData = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(13)
const total = ref(0)

const displayData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return screeningData.value.slice(start, end)
})

const screen = async () => {
  loading.value = true
  try {
    let response
    
    switch (queryParams.value.strategyType) {
      case 'combined':
        response = await screeningAPI.getCombined({
          end_date: queryParams.value.endDate,
          period: queryParams.value.period,
          lookback_days: queryParams.value.lookbackDays,
          require_macd_golden: queryParams.value.requireMacdGolden,
          require_bb_above_middle: queryParams.value.requireBbAboveMiddle
        })
        break
      case 'macd':
        response = await screeningAPI.getMACD({
          end_date: queryParams.value.endDate,
          period: queryParams.value.period,
          lookback_days: queryParams.value.lookbackDays,
          include_golden_cross: queryParams.value.requireMacdGolden,
          include_death_cross: false
        })
        break
      case 'bollinger':
        response = await screeningAPI.getBollinger({
          end_date: queryParams.value.endDate,
          period: queryParams.value.period,
          lookback_days: queryParams.value.lookbackDays,
          include_upper_break: true,
          include_lower_break: false,
          include_squeeze: false
        })
        break
      case 'volume':
        response = await screeningAPI.getVolume({
          end_date: queryParams.value.endDate,
          period: queryParams.value.period,
          lookback_days: queryParams.value.lookbackDays,
          min_volume_ratio: 2.0
        })
        break
    }
    
    if (response.success) {
      screeningData.value = response.data
      total.value = response.data.length
      currentPage.value = 1
    }
  } catch (error) {
    console.error('筛选失败:', error)
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

const formatNumber3 = (row, column, cellValue) => {
  if (cellValue === null || cellValue === undefined || cellValue === '') {
    return '-'
  }
  return Number(cellValue).toFixed(3)
}

const formatSignalType = (row, column, cellValue) => {
  const signalTypeMap = {
    'MACD Golden Cross': 'MACD金叉',
    'MACD Death Cross': 'MACD死叉',
    'BB Upper Break': '布林带突破上轨',
    'BB Lower Break': '布林带突破下轨',
    'BB Squeeze': '布林带收缩',
    'Combined Signal': '组合信号',
    'High Volume': '高成交量'
  }
  return signalTypeMap[cellValue] || cellValue || '-'
}

const getFundUrl = (code) => {
  // 新浪财经ETF链接格式：http://finance.sina.com.cn/fund/etf/{code}.shtml
  // 如果代码不带前缀，根据第一位判断添加sh或sz前缀
  let fullCode = code
  if (!code.startsWith('sh') && !code.startsWith('sz')) {
    const firstDigit = code.charAt(0)
    if (firstDigit === '5' || firstDigit === '6') {
      fullCode = `sh${code}`
    } else {
      fullCode = `sz${code}`
    }
  }
  return `http://finance.sina.com.cn/fund/etf/${fullCode}.shtml`
}

onMounted(() => {
  screen()
})
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
