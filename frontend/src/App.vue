<script setup lang="ts">
// App.vue - 简化版本，移除可能导致冲突的路由逻辑
// 路由守卫在 router/index.ts 中处理
</script>

<template>
  <router-view />
</template>

<style>
/* 全局样式 */
html, body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}
</style>
