<script setup lang="ts">
import type { Project } from '~/types'

definePageMeta({ layout: 'default' })

const projectsStore = useProjectsStore()
const toast = useToast()

// Modal state
const showCreateModal = ref(false)
const newProjectName = ref('')
const newProjectDescription = ref('')
const creating = ref(false)

// Fetch projects on mount
onMounted(() => {
  projectsStore.fetchProjects()
})

// Status badge styles
function statusBadgeClass(status: string): string {
  const map: Record<string, string> = {
    active: 'bg-green-50 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-400 dark:border-green-800',
    archived: 'bg-surface-hover text-muted border-edge',
    paused: 'bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-950 dark:text-yellow-400 dark:border-yellow-800',
  }
  return map[status] || 'bg-surface-hover text-muted border-edge'
}

// Format date
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

// Truncate description
function truncate(text: string, maxLen = 100): string {
  if (!text || text.length <= maxLen) return text || ''
  return text.slice(0, maxLen).trimEnd() + '...'
}

// Create project
async function handleCreate() {
  if (!newProjectName.value.trim()) return

  creating.value = true
  try {
    const project = await projectsStore.createProject(
      newProjectName.value.trim(),
      newProjectDescription.value.trim(),
    )
    toast.success(`Project "${project.name}" created!`)
    showCreateModal.value = false
    newProjectName.value = ''
    newProjectDescription.value = ''
    await navigateTo(`/projects/${project.id}`)
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Failed to create project'
    toast.error(message)
  } finally {
    creating.value = false
  }
}

function openCreateModal() {
  newProjectName.value = ''
  newProjectDescription.value = ''
  showCreateModal.value = true
}
</script>

<template>
  <div class="h-full overflow-y-auto">
    <div class="max-w-6xl mx-auto px-6 py-8">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-2xl font-bold text-heading">Projects</h1>
          <p class="mt-1 text-sm text-muted">Manage your AI-powered development projects</p>
        </div>
        <UiButton variant="primary" @click="openCreateModal">
          <svg class="w-4 h-4 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" />
          </svg>
          New Project
        </UiButton>
      </div>

      <!-- Loading State -->
      <div v-if="projectsStore.loading" class="flex items-center justify-center py-20">
        <svg class="animate-spin h-8 w-8 text-brand-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="projectsStore.projects.length === 0"
        class="text-center py-20 animate-fade-in"
      >
        <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-brand-soft mb-6">
          <svg class="w-10 h-10 text-brand-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" />
            <line x1="12" y1="11" x2="12" y2="17" />
            <line x1="9" y1="14" x2="15" y2="14" />
          </svg>
        </div>
        <h2 class="text-lg font-semibold text-heading mb-2">No projects yet</h2>
        <p class="text-sm text-muted mb-6 max-w-sm mx-auto">
          Create your first project to start building with AI-powered development tools.
        </p>
        <UiButton variant="primary" @click="openCreateModal">
          Create your first project
        </UiButton>
      </div>

      <!-- Project Grid -->
      <div
        v-else
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 animate-fade-in"
      >
        <NuxtLink
          v-for="project in projectsStore.projects"
          :key="project.id"
          :to="`/projects/${project.id}`"
          class="card-hover p-5 group block"
        >
          <div class="flex items-start justify-between mb-3">
            <h3 class="text-base font-semibold text-heading group-hover:text-brand-600 transition-colors">
              {{ project.name }}
            </h3>
            <span
              class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border capitalize"
              :class="statusBadgeClass(project.status)"
            >
              {{ project.status }}
            </span>
          </div>

          <p class="text-sm text-muted mb-4 line-clamp-2 min-h-[2.5rem]">
            {{ truncate(project.description) || 'No description' }}
          </p>

          <div class="flex items-center text-xs text-faint">
            <svg class="w-3.5 h-3.5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
            </svg>
            Created {{ formatDate(project.created_at) }}
          </div>
        </NuxtLink>
      </div>
    </div>

    <!-- Create Project Modal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="showCreateModal"
          class="fixed inset-0 z-50 flex items-center justify-center p-4"
        >
          <!-- Backdrop -->
          <div
            class="absolute inset-0 bg-black/40 backdrop-blur-sm"
            @click="showCreateModal = false"
          />

          <!-- Modal -->
          <div class="relative w-full max-w-md card p-6 animate-slide-up">
            <h2 class="text-lg font-semibold text-heading mb-1">New Project</h2>
            <p class="text-sm text-muted mb-6">
              Set up a new AI-powered development project.
            </p>

            <form @submit.prevent="handleCreate" class="space-y-4">
              <div>
                <label for="project-name" class="block text-sm font-medium text-sub mb-1.5">
                  Project Name
                </label>
                <input
                  id="project-name"
                  v-model="newProjectName"
                  type="text"
                  placeholder="My awesome project"
                  class="input-field"
                  :disabled="creating"
                  autofocus
                />
              </div>

              <div>
                <label for="project-description" class="block text-sm font-medium text-sub mb-1.5">
                  Description
                  <span class="text-faint font-normal">(optional)</span>
                </label>
                <textarea
                  id="project-description"
                  v-model="newProjectDescription"
                  rows="3"
                  placeholder="Briefly describe what this project is about"
                  class="input-field resize-none"
                  :disabled="creating"
                />
              </div>

              <div class="flex items-center justify-end gap-3 pt-2">
                <UiButton
                  variant="ghost"
                  :disabled="creating"
                  @click="showCreateModal = false"
                >
                  Cancel
                </UiButton>
                <UiButton
                  type="submit"
                  variant="primary"
                  :loading="creating"
                  :disabled="!newProjectName.trim()"
                >
                  Create Project
                </UiButton>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>
