<script setup lang="ts">
// Simple blinking cursor shown at the end of streaming assistant messages.
</script>

<template>
  <span class="streaming-cursor inline text-brand-600">&#9610;</span>
</template>

<style scoped>
.streaming-cursor {
  animation: blink 1s step-end infinite;
  font-size: 0.9em;
  line-height: 1;
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}
</style>
