export interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
}

const toasts = ref<Toast[]>([])
let nextId = 0

function addToast(message: string, type: Toast['type']) {
  const id = nextId++
  toasts.value.push({ id, message, type })

  setTimeout(() => {
    removeToast(id)
  }, 4000)
}

function removeToast(id: number) {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index !== -1) {
    toasts.value.splice(index, 1)
  }
}

export function useToast() {
  return {
    toasts: readonly(toasts),
    removeToast,
    success(message: string) {
      addToast(message, 'success')
    },
    error(message: string) {
      addToast(message, 'error')
    },
    info(message: string) {
      addToast(message, 'info')
    },
  }
}
