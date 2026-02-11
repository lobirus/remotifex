<template>
  <header class="flex h-14 flex-shrink-0 items-center justify-between border-b border-gray-200 bg-white px-4 lg:px-6">
    <!-- Left: hamburger (mobile) + page title -->
    <div class="flex items-center gap-3">
      <!-- Mobile sidebar toggle -->
      <button
        class="flex items-center justify-center rounded-md p-1.5 text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700 lg:hidden"
        @click="$emit('toggle-sidebar')"
      >
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>

      <!-- Page title -->
      <h1 class="text-base font-semibold text-gray-900 truncate">
        {{ pageTitle }}
      </h1>
    </div>

    <!-- Right: user menu -->
    <div class="relative">
      <button
        class="flex items-center gap-2 rounded-full p-1 transition-colors hover:bg-gray-50"
        @click="showUserMenu = !showUserMenu"
      >
        <div
          class="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-sm font-semibold text-brand-700"
        >
          {{ userInitials }}
        </div>
        <span class="hidden text-sm font-medium text-gray-700 sm:inline">
          {{ userName }}
        </span>
        <svg
          class="hidden h-4 w-4 text-gray-400 sm:block"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      <!-- Dropdown menu -->
      <Transition
        enter-active-class="transition duration-100 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition duration-75 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          v-if="showUserMenu"
          class="absolute right-0 top-full z-50 mt-1 w-48 origin-top-right rounded-lg border border-gray-200 bg-white py-1 shadow-lg"
        >
          <div class="border-b border-gray-100 px-3 py-2">
            <p class="text-sm font-medium text-gray-900">{{ userName }}</p>
            <p class="text-xs text-gray-500">{{ userRole }}</p>
          </div>
          <button
            class="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-gray-700 transition-colors hover:bg-gray-50"
            @click="handleLogout"
          >
            <svg class="h-4 w-4 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            Log out
          </button>
        </div>
      </Transition>
    </div>

    <!-- Click-outside overlay to close menu -->
    <div
      v-if="showUserMenu"
      class="fixed inset-0 z-40"
      @click="showUserMenu = false"
    />
  </header>
</template>

<script setup lang="ts">
defineEmits<{
  'toggle-sidebar': []
}>()

const route = useRoute()
const authStore = useAuthStore()
const projectsStore = useProjectsStore()

const showUserMenu = ref(false)

// Page title: use project name when inside a project, otherwise route meta or fallback
const pageTitle = computed(() => {
  const meta = route.meta?.title as string | undefined
  if (meta) return meta

  // If inside a project, show project name
  if (projectsStore.currentProject && route.path.includes('/projects/')) {
    return projectsStore.currentProject.name
  }

  // Fallback from route path
  const segment = route.path.split('/').filter(Boolean).pop()
  if (!segment || segment === '/') return 'Dashboard'
  return segment.charAt(0).toUpperCase() + segment.slice(1)
})

const userName = computed(() => authStore.user?.username ?? 'User')

const userInitials = computed(() => {
  const name = authStore.user?.username ?? 'U'
  return name
    .split(/[\s_-]+/)
    .map((w) => w[0]?.toUpperCase() ?? '')
    .slice(0, 2)
    .join('')
})

const userRole = computed(() => (authStore.isAdmin ? 'Admin' : 'Member'))

function handleLogout() {
  showUserMenu.value = false
  authStore.logout()
  navigateTo('/login')
}
</script>
