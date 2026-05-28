<script setup>
import './css/nuxt-ui.css'
import 'uno.css'
</script>

<template>
  <UApp :toaster="{ position: 'top-right' }">
    <router-view />
  </UApp>
</template>
