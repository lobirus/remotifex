<script setup lang="ts">
definePageMeta({ layout: 'default' })

const route = useRoute()
const projectsStore = useProjectsStore()

const projectId = computed(() => route.params.id as string)

// Fetch project details on mount
onMounted(async () => {
  await projectsStore.fetchProject(projectId.value)
})

// Update project if route param changes
watch(projectId, async (newId) => {
  if (newId) {
    await projectsStore.fetchProject(newId)
  }
})
</script>

<template>
  <div class="h-full flex flex-col">
    <!-- Loading State -->
    <div v-if="projectsStore.loading && !projectsStore.currentProject" class="flex-1 flex items-center justify-center">
      <svg class="animate-spin h-8 w-8 text-brand-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
      </svg>
    </div>

    <!-- Chat Panel -->
    <ChatPanel
      v-else
      :project-id="projectId"
      class="flex-1"
    />
  </div>
</template>
