<script setup lang="ts">
interface Props {
  title: string
  description?: string
  icon?: string
}

const props = withDefaults(defineProps<Props>(), {
  description: undefined,
  icon: undefined,
})
</script>

<template>
  <div class="flex flex-col items-center justify-center py-12 px-4 text-center">
    <!-- Custom SVG icon via prop -->
    <div
      v-if="icon"
      class="mb-4 text-gray-300"
      v-html="icon"
    />

    <!-- Default icon when no custom icon provided -->
    <div
      v-else
      class="mb-4"
    >
      <svg
        class="w-12 h-12 text-gray-300"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z"
        />
      </svg>
    </div>

    <h3 class="text-base font-semibold text-gray-900 mb-1">
      {{ title }}
    </h3>

    <p
      v-if="description"
      class="text-sm text-gray-500 max-w-sm mb-6"
    >
      {{ description }}
    </p>

    <!-- Action slot -->
    <div v-if="$slots.default">
      <slot />
    </div>
  </div>
</template>
