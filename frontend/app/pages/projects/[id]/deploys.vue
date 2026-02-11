<template>
  <div class="max-w-3xl mx-auto p-6 space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Deployments</h1>
        <p class="mt-1 text-sm text-gray-500">Deploy staging to production (coming in Phase 3)</p>
      </div>
      <button class="btn-primary" disabled>
        Deploy to Production
      </button>
    </div>

    <div class="card p-12 text-center">
      <svg class="w-12 h-12 mx-auto text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
      <h3 class="text-lg font-medium text-gray-900">Deployments coming soon</h3>
      <p class="mt-2 text-sm text-gray-500 max-w-md mx-auto">
        You'll be able to deploy your staging environment to production with one click,
        view deployment history, and roll back to previous versions.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })
</script>
