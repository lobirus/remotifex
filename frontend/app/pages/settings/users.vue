<template>
  <div class="max-w-3xl mx-auto p-6 space-y-6">
    <div>
      <h1 class="text-2xl font-semibold text-gray-900">Users</h1>
      <p class="mt-1 text-sm text-gray-500">Manage user accounts (coming in Phase 4)</p>
    </div>

    <div class="card p-12 text-center">
      <div class="text-4xl mb-4">
        <svg class="w-12 h-12 mx-auto text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900">Multi-user support coming soon</h3>
      <p class="mt-2 text-sm text-gray-500">
        You'll be able to create user accounts with username/password authentication
        and manage per-project access.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })
</script>
