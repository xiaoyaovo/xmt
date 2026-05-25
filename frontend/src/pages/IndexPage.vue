<template>
  <div class="home-page">
    <SiteHeroPanel
      :hero="homeHero"
      :actions="heroActions"
      :metrics="heroMetrics"
      :status="heroStatus"
      :stacks="heroStacks"
    />

    <SiteFeatureBand :items="featureCards" />

    <SiteContentBand
      :heading="contentHeading"
      :items="contentBlocks"
    />
  </div>
</template>

<script setup>
import SiteContentBand from 'src/components/site/SiteContentBand.vue'
import SiteFeatureBand from 'src/components/site/SiteFeatureBand.vue'
import SiteHeroPanel from 'src/components/site/SiteHeroPanel.vue'
import {
  contentBlocks,
  contentHeading,
  featureCards,
  heroActions,
  heroMetrics,
  heroStacks,
  heroStatus,
  homeHero
} from 'src/lib/siteHome'
</script>
