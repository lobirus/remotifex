<template>
  <aside
    :class="[
      'fixed inset-y-0 left-0 z-30 flex flex-col border-r border-edge bg-surface transition-all duration-200 ease-in-out',
      collapsed ? 'w-16' : 'w-60',
      'hidden lg:flex',
    ]"
  >
    <!-- Brand -->
    <div class="flex h-14 items-center border-b border-edge-subtle px-4">
      <NuxtLink to="/" class="flex items-center gap-2.5 overflow-hidden">
        <div class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-brand-600 text-white">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 4h8a8 8 0 0 1 0 16H4V4z" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" />
            <path d="M4 12h8" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" />
            <path d="M12 12l5 8" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" />
          </svg>
        </div>
        <span
          v-if="!collapsed"
          class="text-base font-semibold text-heading whitespace-nowrap"
        >
          Remotifex
        </span>
      </NuxtLink>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto px-2 py-3">
      <!-- Main nav -->
      <div class="space-y-0.5">
        <NuxtLink
          v-for="item in mainNavItems"
          :key="item.to"
          :to="item.to"
          :class="[
            'group flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors duration-150',
            collapsed ? 'justify-center' : '',
            isActive(item.to)
              ? 'bg-brand-soft text-brand-500'
              : 'text-muted hover:bg-surface-hover hover:text-heading',
          ]"
          :title="collapsed ? item.label : undefined"
        >
          <span
            :class="[
              'flex-shrink-0',
              isActive(item.to) ? 'text-brand-500' : 'text-faint group-hover:text-muted',
            ]"
            v-html="item.icon"
          />
          <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
        </NuxtLink>
      </div>

      <!-- Project nav (when inside a project) -->
      <template v-if="currentProject">
        <div class="my-3 border-t border-edge-subtle" />
        <div v-if="!collapsed" class="mb-2 px-3">
          <p class="text-[11px] font-medium uppercase tracking-wider text-faint">
            {{ currentProject.name }}
          </p>
        </div>
        <div class="space-y-0.5">
          <NuxtLink
            v-for="item in projectNavItems"
            :key="item.to"
            :to="item.to"
            :class="[
              'group flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors duration-150',
              collapsed ? 'justify-center' : '',
              isActive(item.to)
                ? 'bg-brand-soft text-brand-500'
                : 'text-muted hover:bg-surface-hover hover:text-heading',
            ]"
            :title="collapsed ? item.label : undefined"
          >
            <span
              :class="[
                'flex-shrink-0',
                isActive(item.to) ? 'text-brand-500' : 'text-faint group-hover:text-muted',
              ]"
              v-html="item.icon"
            />
            <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
          </NuxtLink>
        </div>
      </template>
    </nav>

    <!-- Collapse toggle -->
    <div class="border-t border-edge-subtle p-2">
      <button
        class="flex w-full items-center justify-center rounded-md p-2 text-faint transition-colors hover:bg-surface-hover hover:text-muted"
        @click="$emit('toggle')"
      >
        <svg
          :class="['h-4 w-4 transition-transform duration-200', collapsed ? 'rotate-180' : '']"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M15 18l-6-6 6-6" />
        </svg>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
defineProps<{
  collapsed: boolean
}>()

defineEmits<{
  toggle: []
}>()

const route = useRoute()
const projectsStore = useProjectsStore()

const currentProject = computed(() => projectsStore.currentProject)

const projectId = computed(() => route.params.id as string | undefined)

// Shared icon SVG attributes
const ico = 'class="h-[18px] w-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"'

// Main navigation items
const mainNavItems = computed(() => [
  {
    to: '/',
    label: 'Dashboard',
    icon: `<svg ${ico}><rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/></svg>`,
  },
  {
    to: '/settings',
    label: 'Settings',
    icon: `<svg ${ico}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>`,
  },
])

// Project-specific navigation items
const projectNavItems = computed(() => {
  const id = projectId.value
  if (!id) return []
  return [
    {
      to: `/projects/${id}`,
      label: 'Chat',
      icon: `<svg ${ico}><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`,
    },
    {
      to: `/projects/${id}/files`,
      label: 'Files',
      icon: `<svg ${ico}><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>`,
    },
    {
      to: `/projects/${id}/environments`,
      label: 'Environments',
      icon: `<svg ${ico}><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>`,
    },
    {
      to: `/projects/${id}/deploys`,
      label: 'Deploys',
      icon: `<svg ${ico}><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>`,
    },
    {
      to: `/projects/${id}/git`,
      label: 'Git',
      icon: `<svg ${ico}><circle cx="18" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><path d="M13 6h3a2 2 0 0 1 2 2v7"/><line x1="6" y1="9" x2="6" y2="21"/></svg>`,
    },
    {
      to: `/projects/${id}/settings`,
      label: 'Settings',
      icon: `<svg ${ico}><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>`,
    },
  ]
})

function isActive(to: string): boolean {
  if (to === '/') return route.path === '/'
  // For project index (chat), exact match to avoid highlighting on sub-pages
  if (/^\/projects\/[^/]+$/.test(to)) return route.path === to
  return route.path.startsWith(to)
}
</script>
