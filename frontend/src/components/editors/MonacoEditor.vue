<script setup>
import {
  nextTick,
  onBeforeUnmount,
  onMounted,
  shallowRef,
  useTemplateRef,
  watch
} from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  language: {
    type: String,
    default: 'xml'
  },
  readOnly: {
    type: Boolean,
    default: false
  },
  minHeight: {
    type: [String, Number],
    default: 560
  },
  options: {
    type: Object,
    default: () => ({})
  },
  ariaLabel: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'ready'])

const hostRef = useTemplateRef('host')
const editorRef = shallowRef(null)
const monacoRef = shallowRef(null)

let suppressEmit = false
let themeObserver = null
let resizeObserver = null
let disposeChangeListener = null

const themes = {
  light: 'xmt-light',
  dark: 'xmt-dark'
}

let themesRegistered = false

function isDarkTheme() {
  if (typeof document === 'undefined') return false
  const root = document.documentElement
  const brand = root.dataset.brandTheme
  return root.classList.contains('dark') || brand === 'terminal' || brand === 'spotify'
}

function activeTheme() {
  return isDarkTheme() ? themes.dark : themes.light
}

function registerThemes(monaco) {
  if (themesRegistered) return
  monaco.editor.defineTheme(themes.light, {
    base: 'vs',
    inherit: true,
    rules: [],
    colors: {
      'editor.background': '#ffffff',
      'editor.foreground': '#0f1723',
      'editor.lineHighlightBackground': '#f1f4f9',
      'editorLineNumber.foreground': '#9aa6b2',
      'editorLineNumber.activeForeground': '#102542',
      'editorIndentGuide.background': '#eaeef3',
      'editor.selectionBackground': '#d9e3f0'
    }
  })
  monaco.editor.defineTheme(themes.dark, {
    base: 'vs-dark',
    inherit: true,
    rules: [],
    colors: {
      'editor.background': '#0f1723',
      'editor.foreground': '#edf6ff',
      'editor.lineHighlightBackground': '#172132',
      'editorLineNumber.foreground': '#5d6b7e',
      'editorLineNumber.activeForeground': '#edf6ff',
      'editorIndentGuide.background': '#1d2738',
      'editor.selectionBackground': '#2c3a52'
    }
  })
  themesRegistered = true
}

async function loadMonaco() {
  if (monacoRef.value) return monacoRef.value

  const [
    monaco,
    { default: EditorWorker }
  ] = await Promise.all([
    import('monaco-editor'),
    import('monaco-editor/esm/vs/editor/editor.worker?worker')
  ])

  if (typeof self !== 'undefined' && !self.MonacoEnvironment) {
    self.MonacoEnvironment = {
      getWorker() {
        return new EditorWorker()
      }
    }
  }

  monacoRef.value = monaco
  return monaco
}

async function createEditor() {
  const host = hostRef.value
  if (!host) return
  const monaco = await loadMonaco()
  registerThemes(monaco)

  editorRef.value = monaco.editor.create(host, {
    value: props.modelValue ?? '',
    language: props.language,
    theme: activeTheme(),
    readOnly: props.readOnly,
    automaticLayout: true,
    fontFamily: '"SFMono-Regular", "Cascadia Code", "Liberation Mono", monospace',
    fontSize: 13,
    lineHeight: 22,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    smoothScrolling: true,
    renderLineHighlight: 'gutter',
    roundedSelection: false,
    tabSize: 2,
    wordWrap: 'on',
    bracketPairColorization: { enabled: true },
    padding: { top: 14, bottom: 14 },
    fixedOverflowWidgets: true,
    ...props.options
  })

  disposeChangeListener = editorRef.value.onDidChangeModelContent(() => {
    if (suppressEmit) return
    emit('update:modelValue', editorRef.value.getValue())
  }).dispose

  watchSystemTheme()
  emit('ready', { editor: editorRef.value, monaco })
}

function watchSystemTheme() {
  if (typeof document === 'undefined' || themeObserver) return
  themeObserver = new MutationObserver(() => {
    if (!editorRef.value || !monacoRef.value) return
    monacoRef.value.editor.setTheme(activeTheme())
  })
  themeObserver.observe(document.documentElement, {
    attributeFilter: ['class', 'data-brand-theme'],
    attributes: true
  })
}

function disposeEditor() {
  if (disposeChangeListener) {
    disposeChangeListener()
    disposeChangeListener = null
  }
  if (editorRef.value) {
    editorRef.value.dispose()
    editorRef.value = null
  }
  if (themeObserver) {
    themeObserver.disconnect()
    themeObserver = null
  }
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
}

defineExpose({
  focus() {
    editorRef.value?.focus()
  },
  getEditor() {
    return editorRef.value
  }
})

watch(
  () => props.modelValue,
  next => {
    const editor = editorRef.value
    if (!editor) return
    const current = editor.getValue()
    if (current === next) return
    suppressEmit = true
    const position = editor.getPosition()
    editor.setValue(next ?? '')
    if (position) {
      nextTick(() => editor.setPosition(position))
    }
    suppressEmit = false
  }
)

watch(
  () => props.language,
  next => {
    const editor = editorRef.value
    const monaco = monacoRef.value
    if (!editor || !monaco) return
    const model = editor.getModel()
    if (model) monaco.editor.setModelLanguage(model, next)
  }
)

watch(
  () => props.readOnly,
  next => {
    editorRef.value?.updateOptions({ readOnly: next })
  }
)

watch(
  () => props.options,
  next => {
    if (next) editorRef.value?.updateOptions(next)
  },
  { deep: true }
)

onMounted(() => {
  createEditor()
})

onBeforeUnmount(() => {
  disposeEditor()
})
</script>

<template>
  <div
    class="monaco-editor-host"
    :class="{ 'monaco-editor-host-readonly': readOnly }"
    :style="{ '--monaco-min-height': typeof minHeight === 'number' ? `${minHeight}px` : minHeight }"
    :aria-label="ariaLabel || undefined"
  >
    <div
      ref="host"
      class="monaco-editor-mount"
    />
  </div>
</template>

<style scoped>
.monaco-editor-host {
  background: var(--brand-color-surface, #ffffff);
  border: 1px solid var(--brand-color-border, var(--shell-line));
  border-radius: var(--brand-radius-md, 16px);
  display: flex;
  flex-direction: column;
  min-height: var(--monaco-min-height, 560px);
  overflow: hidden;
  position: relative;
  transition: border-color 120ms ease, box-shadow 120ms ease;
  width: 100%;
}

.monaco-editor-host:focus-within {
  border-color: var(--brand-color-accent, #102542);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
}

.monaco-editor-host-readonly:focus-within {
  border-color: var(--brand-color-border, var(--shell-line));
  box-shadow: none;
}

.monaco-editor-mount {
  flex: 1 1 auto;
  min-height: var(--monaco-min-height, 560px);
  width: 100%;
}

:global(html.dark) .monaco-editor-host,
:global(html[data-brand-theme='terminal']) .monaco-editor-host,
:global(html[data-brand-theme='spotify']) .monaco-editor-host {
  background: var(--brand-color-surface-2, #0f1723);
  border-color: var(--brand-color-border, rgba(255, 255, 255, 0.08));
}
</style>
