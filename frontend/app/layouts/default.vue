<template>
  <div class="flex h-screen bg-gray-50">
    <!-- Sidebar -->
    <Sidebar
      :collapsed="sidebarCollapsed"
      @toggle="sidebarCollapsed = !sidebarCollapsed"
    />

    <!-- Main content -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Header -->
      <Header @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed" />

      <!-- Page content -->
      <main class="flex-1 overflow-hidden">
        <slot />
      </main>
    </div>

    <!-- Mobile bottom nav -->
    <MobileNav class="lg:hidden" />
  </div>
</template>

<script setup lang="ts">
const sidebarCollapsed = ref(false)

// Auto-collapse sidebar on mobile
const { width } = useWindowSize()
watch(width, (w) => {
  if (w < 1024) sidebarCollapsed.value = true
}, { immediate: true })
</script>
