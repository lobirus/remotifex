<script setup lang="ts">
interface Props {
  show: boolean
  title?: string
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  title: undefined,
  size: 'md',
})

const emit = defineEmits<{
  close: []
}>()

const sizeClass = computed(() => {
  const map: Record<string, string> = {
    sm: 'max-w-sm',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
  }
  return map[props.size]
})

function onBackdropClick() {
  emit('close')
}

function onContentClick(event: MouseEvent) {
  event.stopPropagation()
}

// Close on Escape key
function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    emit('close')
  }
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})

// Lock body scroll when modal is open
watch(() => props.show, (isOpen) => {
  if (isOpen) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
}, { immediate: true })
</script>

<template>
  <Teleport to="body">
    <Transition name="modal-backdrop">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/40 backdrop-blur-sm"
          @click="onBackdropClick"
        />

        <!-- Modal content -->
        <Transition name="modal-content" appear>
          <div
            v-if="show"
            :class="[sizeClass]"
            class="relative w-full bg-white rounded-xl shadow-xl border border-gray-200"
            @click="onContentClick"
          >
            <!-- Header -->
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <h2 class="text-lg font-semibold text-gray-900">
                {{ title }}
              </h2>
              <button
                class="p-1 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                @click="emit('close')"
              >
                <svg
                  class="w-5 h-5"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="2"
                  stroke="currentColor"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- Body -->
            <div class="px-6 py-4">
              <slot />
            </div>

            <!-- Footer -->
            <div
              v-if="$slots.footer"
              class="px-6 py-4 border-t border-gray-100 flex items-center justify-end gap-3"
            >
              <slot name="footer" />
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* Backdrop transitions */
.modal-backdrop-enter-active,
.modal-backdrop-leave-active {
  transition: opacity 0.2s ease;
}

.modal-backdrop-enter-from,
.modal-backdrop-leave-to {
  opacity: 0;
}

/* Content transitions */
.modal-content-enter-active {
  transition: all 0.2s ease-out;
}

.modal-content-leave-active {
  transition: all 0.15s ease-in;
}

.modal-content-enter-from {
  opacity: 0;
  transform: scale(0.95) translateY(4px);
}

.modal-content-leave-to {
  opacity: 0;
  transform: scale(0.97) translateY(2px);
}
</style>
