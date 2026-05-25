<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  index: {
    type: [String, Number],
    default: ''
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  meta: {
    type: String,
    default: ''
  },
  to: {
    type: [String, Object],
    default: null
  },
  href: {
    type: String,
    default: ''
  },
  cta: {
    type: String,
    default: '→'
  }
})

const formattedIndex = computed(() => {
  if (props.index === '' || props.index === null || props.index === undefined) return ''
  if (typeof props.index === 'number') {
    return String(props.index).padStart(2, '0')
  }
  return String(props.index)
})

const isInternal = computed(() => Boolean(props.to))
const isExternal = computed(() => Boolean(!props.to && props.href))
</script>

<template>
  <component
    :is="isInternal ? RouterLink : isExternal ? 'a' : 'div'"
    :to="isInternal ? to : undefined"
    :href="isExternal ? href : undefined"
    class="numbered-row"
    :class="{ 'numbered-row-link': isInternal || isExternal }"
    data-reveal
  >
    <span
      v-if="formattedIndex"
      class="numbered-row-index"
    >
      {{ formattedIndex }}
    </span>

    <span class="numbered-row-body">
      <span class="numbered-row-title">{{ title }}</span>
      <span
        v-if="description"
        class="numbered-row-description"
      >
        {{ description }}
      </span>
      <span
        v-if="meta"
        class="numbered-row-meta"
      >
        {{ meta }}
      </span>
    </span>

    <span
      v-if="isInternal || isExternal"
      class="numbered-row-cta"
      aria-hidden="true"
    >
      {{ cta }}
    </span>
  </component>
</template>

<style scoped>
.numbered-row {
  align-items: baseline;
  border-bottom: 1px solid var(--shell-line);
  color: inherit;
  display: grid;
  gap: 18px;
  grid-template-columns: 56px minmax(0, 1fr) auto;
  padding: 22px 0;
  text-decoration: none;
  transition:
    opacity 480ms cubic-bezier(0.22, 0.61, 0.36, 1),
    transform 480ms cubic-bezier(0.22, 0.61, 0.36, 1),
    background-color 200ms ease;
}

.numbered-row[data-reveal] {
  opacity: 0;
  transform: translateY(14px);
  transition-delay: var(--reveal-delay, 0ms);
}

.numbered-row[data-reveal].is-revealed {
  opacity: 1;
  transform: translateY(0);
}

.numbered-row:first-child {
  border-top: 1px solid var(--shell-line);
}

.numbered-row-link {
  cursor: pointer;
}

.numbered-row-link:hover {
  background: rgba(16, 37, 66, 0.04);
}

.numbered-row-link:focus-visible {
  background: rgba(16, 37, 66, 0.06);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.numbered-row-link:hover .numbered-row-cta,
.numbered-row-link:focus-visible .numbered-row-cta {
  transform: translateX(4px);
}

.numbered-row-index {
  color: var(--shell-coral, #ff7a59);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: 1.05rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  padding-top: 4px;
}

.numbered-row-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.numbered-row-title {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: clamp(1.2rem, 2.2vw, 1.6rem);
  font-weight: 600;
  line-height: 1.2;
}

.numbered-row-description {
  color: rgba(15, 23, 35, 0.72);
  font-size: 1rem;
  line-height: 1.68;
}

.numbered-row-meta {
  color: rgba(15, 23, 35, 0.5);
  font-size: 0.86rem;
  letter-spacing: 0.02em;
  margin-top: 2px;
}

.numbered-row-cta {
  color: var(--shell-navy);
  font-size: 1.4rem;
  font-weight: 700;
  padding-top: 4px;
  transition: transform 200ms ease;
}

@media (prefers-reduced-motion: reduce) {
  .numbered-row,
  .numbered-row[data-reveal] {
    opacity: 1;
    transform: none;
    transition: none;
  }

  .numbered-row-link:hover .numbered-row-cta,
  .numbered-row-link:focus-visible .numbered-row-cta {
    transform: none;
  }
}

@media (max-width: 599px) {
  .numbered-row {
    gap: 14px;
    grid-template-columns: 40px minmax(0, 1fr) auto;
    padding: 18px 0;
  }

  .numbered-row-index {
    font-size: 0.95rem;
  }

  .numbered-row-cta {
    font-size: 1.2rem;
  }
}
</style>
