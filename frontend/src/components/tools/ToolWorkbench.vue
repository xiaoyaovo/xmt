<script setup>
defineProps({
  sourceTitle: {
    type: String,
    default: '源'
  },
  previewTitle: {
    type: String,
    default: '预览'
  }
})
</script>

<template>
  <section class="tool-workbench">
    <header class="tool-workbench-toolbar">
      <slot name="toolbar" />
    </header>

    <div class="tool-workbench-panes">
      <section class="tool-workbench-pane">
        <div class="tool-workbench-pane-kicker">{{ sourceTitle }}</div>
        <slot name="source" />
      </section>

      <section class="tool-workbench-pane">
        <div class="tool-workbench-pane-kicker">{{ previewTitle }}</div>
        <slot name="preview" />
      </section>
    </div>
  </section>
</template>

<style scoped>
.tool-workbench {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 28px;
}

.tool-workbench-toolbar,
.tool-workbench-pane {
  background: var(--shell-panel);
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: var(--brand-radius-lg, 24px);
  box-shadow: var(--brand-shadow-card, var(--shell-shadow));
  min-width: 0;
}

.tool-workbench-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  padding: 18px;
}

.tool-workbench-panes {
  display: grid;
  gap: 20px;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  min-width: 0;
}

.tool-workbench-pane {
  min-height: 520px;
  padding: 22px;
}

.tool-workbench-pane-kicker {
  color: rgba(15, 23, 35, 0.58);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0;
  margin-bottom: 14px;
}

@media (max-width: 1023px) {
  .tool-workbench-panes {
    grid-template-columns: 1fr;
  }

  .tool-workbench-pane {
    min-height: 360px;
  }
}

@media (max-width: 599px) {
  .tool-workbench-toolbar,
  .tool-workbench-pane {
    padding: 18px;
  }
}
</style>
