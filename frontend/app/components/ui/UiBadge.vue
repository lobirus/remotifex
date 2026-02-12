<script setup lang="ts">
interface Props {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'sm' | 'md'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
})

const variantClass = computed(() => {
  const map: Record<string, string> = {
    default: 'bg-surface-hover text-sub',
    success: 'bg-green-50 text-green-700 border-green-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    danger: 'bg-red-50 text-red-700 border-red-200',
    info: 'bg-brand-50 text-brand-700 border-brand-200',
  }
  return map[props.variant]
})

const sizeClass = computed(() => {
  const map: Record<string, string> = {
    sm: 'px-1.5 py-0.5 text-[10px]',
    md: 'px-2.5 py-0.5 text-xs',
  }
  return map[props.size]
})
</script>

<template>
  <span
    :class="[variantClass, sizeClass]"
    class="inline-flex items-center font-medium rounded-full border"
  >
    <slot />
  </span>
</template>
