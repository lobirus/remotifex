<script setup lang="ts">
definePageMeta({ layout: 'default' })

const route = useRoute()
const projectsStore = useProjectsStore()

const projectId = computed(() => route.params.id as string)
const environment = ref('staging')
const selectedFile = ref<string | null>(null)

// Fetch project details on mount
onMounted(async () => {
  await projectsStore.fetchProject(projectId.value)
})

// Update project if route param changes
watch(projectId, async (newId) => {
  if (newId) {
    await projectsStore.fetchProject(newId)
    selectedFile.value = null
  }
})

function onFileSelect(path: string) {
  selectedFile.value = path
}
</script>

<template>
  <div class="h-full flex">
    <!-- Loading State -->
    <div v-if="projectsStore.loading && !projectsStore.currentProject" class="flex-1 flex items-center justify-center">
      <svg class="animate-spin h-8 w-8 text-brand-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
      </svg>
    </div>

    <template v-else>
      <!-- File Tree Sidebar -->
      <div class="w-[250px] flex-shrink-0 border-r border-gray-200 bg-white overflow-y-auto">
        <FileTree
          :project-id="projectId"
          :env="environment"
          @select="onFileSelect"
        />
      </div>

      <!-- File Viewer -->
      <div class="flex-1 min-w-0">
        <FileViewer
          v-if="selectedFile"
          :project-id="projectId"
          :path="selectedFile"
          :env="environment"
        />
        <div v-else class="h-full flex items-center justify-center text-gray-400">
          <div class="text-center">
            <svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="text-sm">Select a file to view its contents</p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
