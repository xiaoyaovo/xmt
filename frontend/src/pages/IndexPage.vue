<script setup>
import NarrativeSection from 'src/components/site/NarrativeSection.vue'
import NumberedRow from 'src/components/site/NumberedRow.vue'
import { useScrollReveal } from 'src/composables/useScrollReveal'
import { aboutSection, heroAction, homeHero, homeRows } from 'src/lib/siteHome'
import { RouterLink } from 'vue-router'

const { root } = useScrollReveal()
</script>

<template>
  <div
    ref="root"
    class="home-narrative"
  >
    <NarrativeSection
      :divider="false"
      width="container"
    >
      <template #header>
        <div
          class="home-hero"
          data-reveal
        >
          <div class="home-hero-badge">{{ homeHero.badge }}</div>
          <h1 class="home-hero-title">{{ homeHero.title }}</h1>
          <p class="home-hero-description">{{ homeHero.description }}</p>
          <div class="home-hero-actions">
            <RouterLink
              :to="heroAction.to"
              class="home-hero-cta"
            >
              {{ heroAction.label }}
              <span aria-hidden="true">→</span>
            </RouterLink>
          </div>
        </div>
      </template>
    </NarrativeSection>

    <NarrativeSection
      kicker="工具"
      title="选一项进入工作台。"
      width="container"
    >
      <div class="home-rows">
        <NumberedRow
          v-for="row in homeRows"
          :key="row.title"
          :index="row.index"
          :title="row.title"
          :description="row.description"
          :to="row.to"
        />
      </div>
    </NarrativeSection>

    <NarrativeSection
      :kicker="aboutSection.kicker"
      :title="aboutSection.title"
      :description="aboutSection.description"
    />
  </div>
</template>

<style scoped>
.home-narrative {
  padding-bottom: 80px;
}

.home-hero {
  align-items: flex-start;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 56px 0 32px;
  opacity: 1;
  transform: none;
  transition:
    opacity 480ms cubic-bezier(0.22, 0.61, 0.36, 1),
    transform 480ms cubic-bezier(0.22, 0.61, 0.36, 1);
}

.home-hero[data-reveal] {
  opacity: 0;
  transform: translateY(14px);
  transition-delay: var(--reveal-delay, 0ms);
}

.home-hero[data-reveal].is-revealed {
  opacity: 1;
  transform: translateY(0);
}

.home-hero-badge {
  color: rgba(16, 37, 66, 0.66);
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.home-hero-title {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: clamp(2.2rem, 5vw, 3.6rem);
  font-weight: 600;
  line-height: 1.04;
  margin: 0;
  max-width: 18ch;
  text-wrap: balance;
}

.home-hero-description {
  color: rgba(15, 23, 35, 0.74);
  font-size: 1.05rem;
  line-height: 1.7;
  margin: 0;
  max-width: 58ch;
}

.home-hero-actions {
  margin-top: 8px;
}

.home-hero-cta {
  align-items: center;
  background: var(--brand-color-accent, var(--shell-navy));
  border-radius: var(--brand-radius-pill, 999px);
  color: #ffffff;
  display: inline-flex;
  font-size: 0.94rem;
  font-weight: 700;
  gap: 10px;
  min-height: 46px;
  padding: 0 22px;
  text-decoration: none;
  transition: transform 200ms ease, box-shadow 200ms ease;
}

.home-hero-cta:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 30px rgba(16, 37, 66, 0.18);
}

.home-hero-cta:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.18));
  outline: none;
}

.home-rows {
  display: flex;
  flex-direction: column;
}

@media (prefers-reduced-motion: reduce) {
  .home-hero,
  .home-hero[data-reveal] {
    opacity: 1;
    transform: none;
    transition: none;
  }

  .home-hero-cta:hover {
    transform: none;
  }
}

@media (max-width: 599px) {
  .home-hero {
    padding: 36px 0 24px;
  }
}
</style>
