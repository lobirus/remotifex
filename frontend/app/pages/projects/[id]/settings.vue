<template>
  <div class="max-w-3xl mx-auto p-6 space-y-8">
    <div>
      <h1 class="text-2xl font-semibold text-heading">Project Settings</h1>
      <p class="mt-1 text-sm text-muted">Configure {{ project?.name || 'project' }}</p>
    </div>

    <div v-if="project" class="space-y-6">
      <!-- General -->
      <section class="card p-6 space-y-4">
        <h2 class="text-lg font-medium text-heading">General</h2>

        <div>
          <label class="block text-sm font-medium text-sub mb-1">Project Name</label>
          <input v-model="projectName" type="text" class="input-field" />
        </div>

        <div>
          <label class="block text-sm font-medium text-sub mb-1">Description</label>
          <textarea v-model="projectDescription" class="input-field" rows="3" />
        </div>

        <button class="btn-primary btn-sm" @click="updateProject">Save Changes</button>
      </section>

      <!-- AI Configuration -->
      <section class="card p-6 space-y-4">
        <h2 class="text-lg font-medium text-heading">AI Configuration</h2>
        <p class="text-sm text-muted">Override global AI settings for this project</p>

        <div>
          <label class="block text-sm font-medium text-sub mb-1">AI Tool</label>
          <select v-model="aiTool" class="input-field" @change="updateAiConfig">
            <option value="claude">Claude Code</option>
            <option value="amp">Amp</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-sub mb-1">Model</label>
          <select v-model="aiModel" class="input-field" @change="updateAiConfig">
            <option value="sonnet">Claude Sonnet 4.5</option>
            <option value="opus">Claude Opus 4.6</option>
            <option value="haiku">Claude Haiku 4.5</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-sub mb-1">System Prompt (optional)</label>
          <textarea
            v-model="systemPrompt"
            class="input-field font-mono text-xs"
            rows="4"
            placeholder="Additional instructions for the AI when working on this project..."
            @blur="updateAiConfig"
          />
        </div>
      </section>

      <!-- Danger Zone -->
      <section class="card border-red-200 p-6 space-y-4">
        <h2 class="text-lg font-medium text-red-600">Danger Zone</h2>

        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-heading">Delete Project</p>
            <p class="text-xs text-muted">Permanently delete this project and all its data</p>
          </div>
          <button class="btn-danger btn-sm" @click="confirmDelete">Delete Project</button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

const route = useRoute()
const router = useRouter()
const projectsStore = useProjectsStore()
const api = useApi()

const projectId = route.params.id as string

const project = computed(() => projectsStore.currentProject)
const projectName = ref('')
const projectDescription = ref('')
const aiTool = ref('claude')
const aiModel = ref('sonnet')
const systemPrompt = ref('')

onMounted(async () => {
  await projectsStore.fetchProject(projectId)
  if (project.value) {
    projectName.value = project.value.name
    projectDescription.value = project.value.description
    aiTool.value = project.value.ai_config.tool
    aiModel.value = project.value.ai_config.model
    systemPrompt.value = project.value.ai_config.append_system_prompt || ''
  }
})

async function updateProject() {
  await api.patch(`/projects/${projectId}`, {
    name: projectName.value,
    description: projectDescription.value,
  })
  await projectsStore.fetchProject(projectId)
}

async function updateAiConfig() {
  await api.patch(`/projects/${projectId}/ai-config`, {
    tool: aiTool.value,
    model: aiModel.value,
    append_system_prompt: systemPrompt.value || null,
  })
}

async function confirmDelete() {
  if (!confirm(`Are you sure you want to delete "${project.value?.name}"? This cannot be undone.`)) {
    return
  }
  await projectsStore.deleteProject(projectId)
  router.push('/')
}
</script>
