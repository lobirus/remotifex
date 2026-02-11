<script setup lang="ts">
interface Props {
  hoverable?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  hoverable: false,
  padding: 'md',
})

const paddingClass = computed(() => {
  const map: Record<string, string> = {
    none: '',
    sm: 'p-3',
    md: 'p-5',
    lg: 'p-8',
  }
  return map[props.padding]
})
</script>

<template>
  <div
    :class="[
      hoverable ? 'card-hover' : 'card',
    ]"
  >
    <!-- Header -->
    <div
      v-if="$slots.header"
      class="px-5 py-4 border-b border-gray-100"
    >
      <slot name="header" />
    </div>

    <!-- Body -->
    <div :class="paddingClass">
      <slot />
    </div>
  </div>
</template>
