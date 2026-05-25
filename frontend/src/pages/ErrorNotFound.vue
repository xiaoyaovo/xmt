<template>
  <div class="error-page">
    <div class="error-shell">
      <div class="error-code">404</div>
      <h1 class="error-title">这个页面路由还没有接入完整内容。</h1>
      <p class="error-text">
        你可以先返回首页，继续查看站点骨架、工具区或后台区的当前结构。
      </p>
      <RouterLink
        to="/"
        class="hero-button hero-button-primary"
      >
        返回首页
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>
