<script setup>
import { reactive, shallowRef } from 'vue'

const formState = reactive({
  email: ''
})
const submittedEmail = shallowRef('')

function validate(state) {
  const errors = []

  if (!state.email) {
    errors.push({ name: 'email', message: '请输入邮箱' })
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(state.email)) {
    errors.push({ name: 'email', message: '邮箱格式不正确' })
  }

  return errors
}

function submit() {
  submittedEmail.value = formState.email
}
</script>

<template>
  <main class="ui-preview-page">
    <section class="ui-preview-hero">
      <div>
        <UBadge
          color="primary"
          variant="soft"
          label="Nuxt UI"
        />
        <h1>新 UI 组件预览</h1>
        <p>用于验证 Nuxt UI 已经接入 Vue / Quasar 项目，后续登录、绑定邮箱、账户安全等表单可以逐步迁移到这套组件。</p>
      </div>
    </section>

    <section class="ui-preview-grid">
      <UCard>
        <template #header>
          <div class="ui-preview-card-head">
            <div>
              <h2>表单校验</h2>
              <p>UForm + UFormField 会把字段错误显示在对应输入下方。</p>
            </div>
            <UBadge
              color="neutral"
              variant="subtle"
              label="Smoke test"
            />
          </div>
        </template>

        <UForm
          :state="formState"
          :validate="validate"
          class="ui-preview-form"
          @submit="submit"
        >
          <UFormField
            label="邮箱"
            name="email"
            required
          >
            <UInput
              v-model="formState.email"
              type="email"
              placeholder="you@example.com"
            />
          </UFormField>

          <div class="ui-preview-actions">
            <UButton
              type="submit"
              label="验证"
            />
            <UButton
              type="button"
              color="neutral"
              variant="subtle"
              label="清空"
              @click="formState.email = ''; submittedEmail = ''"
            />
          </div>
        </UForm>

        <UAlert
          v-if="submittedEmail"
          class="ui-preview-alert"
          color="success"
          variant="soft"
          title="校验通过"
          :description="`当前邮箱：${submittedEmail}`"
        />
      </UCard>

      <UCard>
        <template #header>
          <div class="ui-preview-card-head">
            <div>
              <h2>基础控件</h2>
              <p>按钮、徽标、提示等控件已可直接使用。</p>
            </div>
          </div>
        </template>

        <div class="ui-preview-stack">
          <UAlert
            color="info"
            variant="soft"
            title="渐进迁移"
            description="现有 Quasar / Reka 页面保持可用，新页面优先采用 Nuxt UI。"
          />
          <div class="ui-preview-actions">
            <UButton label="主操作" />
            <UButton
              color="neutral"
              variant="outline"
              label="次操作"
            />
            <UButton
              color="error"
              variant="soft"
              label="危险操作"
            />
          </div>
        </div>
      </UCard>
    </section>
  </main>
</template>

<style scoped>
.ui-preview-page {
  color: var(--shell-ink);
  min-height: calc(100vh - 76px);
  padding: 48px min(6vw, 72px) 72px;
}

.ui-preview-hero {
  display: flex;
  justify-content: space-between;
  margin: 0 auto 28px;
  max-width: 1040px;
}

.ui-preview-hero h1 {
  color: var(--shell-navy);
  font-size: clamp(2rem, 4vw, 3.5rem);
  font-weight: 780;
  letter-spacing: 0;
  line-height: 1.05;
  margin: 14px 0 12px;
}

.ui-preview-hero p {
  color: rgba(15, 23, 35, 0.68);
  font-size: 1rem;
  line-height: 1.8;
  margin: 0;
  max-width: 680px;
}

.ui-preview-grid {
  display: grid;
  gap: 18px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin: 0 auto;
  max-width: 1040px;
}

.ui-preview-card-head {
  align-items: flex-start;
  display: flex;
  gap: 16px;
  justify-content: space-between;
}

.ui-preview-card-head h2 {
  color: var(--shell-navy);
  font-size: 1rem;
  font-weight: 740;
  letter-spacing: 0;
  margin: 0 0 4px;
}

.ui-preview-card-head p {
  color: rgba(15, 23, 35, 0.58);
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0;
}

.ui-preview-form,
.ui-preview-stack {
  display: grid;
  gap: 18px;
}

.ui-preview-actions {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.ui-preview-alert {
  margin-top: 18px;
}

@media (max-width: 780px) {
  .ui-preview-page {
    padding: 32px 18px 48px;
  }

  .ui-preview-grid {
    grid-template-columns: 1fr;
  }
}
</style>
