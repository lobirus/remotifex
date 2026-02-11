<template>
  <div class="max-w-3xl mx-auto p-6 space-y-6">
    <div>
      <h1 class="text-2xl font-semibold text-gray-900">Git</h1>
      <p class="mt-1 text-sm text-gray-500">Repository configuration and operations (coming in Phase 3)</p>
    </div>

    <section class="card p-6 space-y-4">
      <h2 class="text-lg font-medium text-gray-900">Repository</h2>

      <div class="space-y-4 opacity-50">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Repository URL</label>
          <input type="text" class="input-field" placeholder="https://github.com/user/repo.git" disabled />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Branch</label>
          <input type="text" class="input-field" value="main" disabled />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Access Token</label>
          <input type="password" class="input-field" placeholder="ghp_..." disabled />
        </div>
      </div>

      <p class="text-xs text-gray-400">
        Git integration will let you connect a repository, commit changes manually,
        and push when you're ready.
      </p>
    </section>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })
</script>
