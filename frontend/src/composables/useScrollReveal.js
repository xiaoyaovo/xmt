import { onBeforeUnmount, onMounted, shallowRef } from 'vue'

const REVEALED_CLASS = 'is-revealed'

function prefersReducedMotion() {
  if (typeof window === 'undefined' || !window.matchMedia) return false
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

export function useScrollReveal({
  selector = '[data-reveal]',
  rootMargin = '0px 0px -8% 0px',
  threshold = 0.12,
  stagger = 80
} = {}) {
  const root = shallowRef(null)
  let observer = null

  function revealImmediately(targets) {
    targets.forEach((node) => node.classList.add(REVEALED_CLASS))
  }

  function setup() {
    if (typeof window === 'undefined') return

    const container = root.value || document
    const targets = Array.from(container.querySelectorAll(selector))
    if (!targets.length) return

    // Apply a deterministic stagger index so CSS can animate via delay.
    targets.forEach((node, index) => {
      if (!node.style.getPropertyValue('--reveal-delay')) {
        node.style.setProperty('--reveal-delay', `${index * stagger}ms`)
      }
    })

    if (prefersReducedMotion() || !('IntersectionObserver' in window)) {
      revealImmediately(targets)
      return
    }

    observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add(REVEALED_CLASS)
          observer.unobserve(entry.target)
        }
      })
    }, { rootMargin, threshold })

    targets.forEach((node) => observer.observe(node))
  }

  onMounted(() => {
    // Wait one frame so child components have rendered their `data-reveal` nodes.
    requestAnimationFrame(setup)
  })

  onBeforeUnmount(() => {
    if (observer) {
      observer.disconnect()
      observer = null
    }
  })

  return { root }
}
