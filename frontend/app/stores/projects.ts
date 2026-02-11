import type { Project } from '~/types'

export const useProjectsStore = defineStore('projects', () => {
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const loading = ref(false)

  async function fetchProjects() {
    const api = useApi()
    loading.value = true
    try {
      const data = await api.get<{ projects: Project[]; total: number }>('/projects')
      projects.value = data.projects
    } finally {
      loading.value = false
    }
  }

  async function fetchProject(id: string) {
    const api = useApi()
    loading.value = true
    try {
      currentProject.value = await api.get<Project>(`/projects/${id}`)
    } finally {
      loading.value = false
    }
  }

  async function createProject(name: string, description: string = '') {
    const api = useApi()
    const project = await api.post<Project>('/projects', { name, description })
    projects.value.unshift(project)
    return project
  }

  async function deleteProject(id: string) {
    const api = useApi()
    await api.delete(`/projects/${id}`)
    projects.value = projects.value.filter(p => p.id !== id)
    if (currentProject.value?.id === id) {
      currentProject.value = null
    }
  }

  return {
    projects,
    currentProject,
    loading,
    fetchProjects,
    fetchProject,
    createProject,
    deleteProject,
  }
})
