<template>
  <div class="max-w-3xl mx-auto p-6 space-y-6">
    <div>
      <h1 class="text-2xl font-semibold text-heading">Environments</h1>
      <p class="mt-1 text-sm text-muted">
        Manage environment variables and domains (coming in Phase 2)
      </p>
    </div>

    <!-- Staging -->
    <section class="card p-6 space-y-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-yellow-400"></span>
          <h2 class="text-lg font-medium text-heading">Staging</h2>
        </div>
        <span class="text-xs text-faint bg-surface-hover px-2 py-1 rounded">Auto-created</span>
      </div>

      <div class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-sub mb-1">Domain</label>
          <input type="text" class="input-field" placeholder="staging.example.com" disabled />
          <p class="mt-1 text-xs text-faint">Domain configuration coming in Phase 2</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-sub mb-1">Environment Variables</label>
          <div class="bg-inset rounded-lg p-4 text-center text-sm text-faint">
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
          <h2 class="text-lg font-medium text-heading">Production</h2>
        </div>
        <span class="text-xs text-faint bg-surface-hover px-2 py-1 rounded">Auto-created</span>
      </div>

      <div class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-sub mb-1">Domain</label>
          <input type="text" class="input-field" placeholder="example.com" disabled />
        </div>

        <div>
          <label class="block text-sm font-medium text-sub mb-1">Environment Variables</label>
          <div class="bg-inset rounded-lg p-4 text-center text-sm text-faint">
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
