<template>
  <div class="max-w-3xl mx-auto p-6 space-y-6">
    <div>
      <h1 class="text-2xl font-semibold text-gray-900">Environments</h1>
      <p class="mt-1 text-sm text-gray-500">
        Manage environment variables and domains (coming in Phase 2)
      </p>
    </div>

    <!-- Staging -->
    <section class="card p-6 space-y-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-yellow-400"></span>
          <h2 class="text-lg font-medium text-gray-900">Staging</h2>
        </div>
        <span class="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">Auto-created</span>
      </div>

      <div class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Domain</label>
          <input type="text" class="input-field" placeholder="staging.example.com" disabled />
          <p class="mt-1 text-xs text-gray-400">Domain configuration coming in Phase 2</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Environment Variables</label>
          <div class="bg-gray-50 rounded-lg p-4 text-center text-sm text-gray-400">
            Environment variable management coming in Phase 2
          </div>
        </div>
      </div>
    </section>

    <!-- Production -->
    <section class="card p-6 space-y-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-green-400"></span>
          <h2 class="text-lg font-medium text-gray-900">Production</h2>
        </div>
        <span class="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">Auto-created</span>
      </div>

      <div class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Domain</label>
          <input type="text" class="input-field" placeholder="example.com" disabled />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Environment Variables</label>
          <div class="bg-gray-50 rounded-lg p-4 text-center text-sm text-gray-400">
            Environment variable management coming in Phase 2
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })
</script>
