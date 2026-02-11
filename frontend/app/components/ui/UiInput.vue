<script setup lang="ts">
interface Props {
  modelValue?: string
  label?: string
  placeholder?: string
  type?: 'text' | 'password' | 'email'
  error?: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  label: undefined,
  placeholder: undefined,
  type: 'text',
  error: undefined,
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const inputId = useId()

function onInput(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="w-full">
    <label
      v-if="label"
      :for="inputId"
      class="block text-sm font-medium text-gray-700 mb-1.5"
    >
      {{ label }}
    </label>

    <input
      :id="inputId"
      :value="modelValue"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      class="input-field"
      :class="{
        'border-red-500 focus:ring-red-500 focus:border-red-500': error,
        'bg-gray-50 cursor-not-allowed text-gray-500': disabled,
      }"
      @input="onInput"
    />

    <p
      v-if="error"
      class="mt-1.5 text-sm text-red-600"
    >
      {{ error }}
    </p>
  </div>
</template>
