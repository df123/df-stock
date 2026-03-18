<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>ETF量化分析系统</h1>
          <nav>
            <router-link to="/">仪表盘</router-link>
            <router-link to="/realtime">实时行情</router-link>
            <router-link to="/history">历史数据</router-link>
            <router-link to="/screening">策略筛选</router-link>
            <router-link to="/backtest">策略推演</router-link>
            <router-link to="/database">数据库</router-link>
          </nav>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  min-height: 100vh;
}

.el-header {
  background-color: #409EFF;
  color: white;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-content {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-content h1 {
  margin: 0;
  font-size: 24px;
}

.header-content nav {
  display: flex;
  gap: 20px;
}

.header-content nav a {
  color: white;
  text-decoration: none;
  font-size: 16px;
}

.header-content nav a:hover {
  opacity: 0.8;
}

.el-main {
  padding: 20px;
}
</style>
