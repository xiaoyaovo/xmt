<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useScrollReveal } from 'src/composables/useScrollReveal'
import { request } from 'src/lib/http'
import CommentBoard from 'src/components/comment/CommentBoard.vue'

const { root } = useScrollReveal()

const couple = {
  groomEn: 'Yiming',
  groomCn: '一鸣',
  brideEn: 'Xinran',
  brideCn: '欣然',
  monogram: 'Y & X'
}

const wedding = {
  dateLabel: '2026 . 10 . 01',
  weekday: '星期四',
  ceremonyTime: '吉时 11:08',
  venueName: '杭州 · 西子湖畔花园酒店',
  venueAddress: '浙江省杭州市西湖区南山路 28 号',
  metStart: new Date('2020-05-20T00:00:00'),
  loveStart: new Date('2021-02-14T00:00:00'),
  weddingDate: new Date('2026-10-01T11:08:00')
}

const heroImage =
  'https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=1800&q=80'

const storyPortrait =
  'https://images.unsplash.com/photo-1606216794074-735e91aa2c92?auto=format&fit=crop&w=1200&q=80'

const galleryImages = [
  'https://images.unsplash.com/photo-1525258946800-98cfd641d0de?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1511285560929-80b456fea0bc?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1519225421980-715cb0215aed?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1583939003579-730e3918a45a?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1465495976277-4387d4b0e4a6?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1519671482749-fd09be7ccebf?auto=format&fit=crop&w=900&q=80'
]

const now = ref(new Date())
let timer = null

onMounted(() => {
  timer = setInterval(() => {
    now.value = new Date()
  }, 1000)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})

function daysBetween(a, b) {
  const ms = Math.abs(b.getTime() - a.getTime())
  return Math.floor(ms / (1000 * 60 * 60 * 24))
}

const metDays = computed(() => daysBetween(wedding.metStart, now.value))
const loveDays = computed(() => daysBetween(wedding.loveStart, now.value))

const countdown = computed(() => {
  const diff = wedding.weddingDate.getTime() - now.value.getTime()
  if (diff <= 0) return { days: 0, hours: 0, minutes: 0, seconds: 0, passed: true }
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((diff % (1000 * 60)) / 1000)
  return { days, hours, minutes, seconds, passed: false }
})

const rsvp = ref({
  name: '',
  attendance: 'yes',
  guests: 1,
  message: ''
})

const submitting = ref(false)
const submitStatus = ref('')

async function submitRsvp() {
  if (!rsvp.value.name.trim()) {
    submitStatus.value = '请先告诉我们您的名字 🤍'
    return
  }
  submitting.value = true
  submitStatus.value = ''
  try {
    await request.post('/wedding/rsvp', rsvp.value)
    submitStatus.value = '感谢您的祝福已送达 🤍'
    rsvp.value.message = ''
  } catch {
    submitStatus.value = '网络稍慢,请稍后再试,或直接联系新人 🤍'
  } finally {
    submitting.value = false
  }
}

function scrollTo(id) {
  const el = document.getElementById(id)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<template>
  <div
    ref="root"
    class="wedding-page"
  >
    <!-- Hero -->
    <section
      id="wedding-hero"
      class="wd-hero"
    >
      <div
        class="wd-hero-bg"
        :style="{ backgroundImage: `url(${heroImage})` }"
      />
      <div class="wd-hero-veil" />
      <div class="wd-hero-corner wd-hero-corner-tl">
        <svg viewBox="0 0 160 160" xmlns="http://www.w3.org/2000/svg">
          <g fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round">
            <path d="M20 140 C 40 100, 70 70, 130 30" />
            <path d="M40 130 C 55 110, 70 100, 88 90" />
            <path d="M40 130 L 30 138 M 40 130 L 48 122" />
            <path d="M60 116 L 52 122 M 60 116 L 68 110" />
            <path d="M78 100 C 70 92, 70 78, 82 70 C 88 80, 88 92, 78 100z" />
            <path d="M98 80 C 90 72, 90 58, 102 50 C 108 60, 108 72, 98 80z" />
            <path d="M118 60 C 110 52, 110 38, 122 30 C 128 40, 128 52, 118 60z" />
          </g>
        </svg>
      </div>
      <div class="wd-hero-corner wd-hero-corner-br">
        <svg viewBox="0 0 160 160" style="transform: scaleX(-1) scaleY(-1)" xmlns="http://www.w3.org/2000/svg">
          <g fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round">
            <path d="M20 140 C 40 100, 70 70, 130 30" />
            <path d="M40 130 C 55 110, 70 100, 88 90" />
            <path d="M40 130 L 30 138 M 40 130 L 48 122" />
            <path d="M60 116 L 52 122 M 60 116 L 68 110" />
            <path d="M78 100 C 70 92, 70 78, 82 70 C 88 80, 88 92, 78 100z" />
            <path d="M98 80 C 90 72, 90 58, 102 50 C 108 60, 108 72, 98 80z" />
            <path d="M118 60 C 110 52, 110 38, 122 30 C 128 40, 128 52, 118 60z" />
          </g>
        </svg>
      </div>

      <div class="wd-hero-inner">
        <div
          class="wd-hero-copy"
          data-reveal
        >
          <p class="wd-hero-eyebrow">We are getting married</p>
          <h1 class="wd-hero-title">
            <span class="wd-hero-name">{{ couple.groomEn }}</span>
            <span class="wd-hero-amp">&amp;</span>
            <span class="wd-hero-name">{{ couple.brideEn }}</span>
          </h1>
          <p class="wd-hero-sub">
            {{ couple.groomCn }} &amp; {{ couple.brideCn }} · 邀您共赴良辰
          </p>
          <div class="wd-hero-date">
            <span class="wd-hero-date-num">{{ wedding.dateLabel }}</span>
            <span class="wd-hero-date-meta">{{ wedding.weekday }} · {{ wedding.ceremonyTime }}</span>
          </div>
          <div class="wd-hero-actions">
            <button
              type="button"
              class="wd-btn wd-btn-dark"
              @click="scrollTo('wedding-rsvp')"
            >
              出席回执 →
            </button>
            <button
              type="button"
              class="wd-btn wd-btn-ghost"
              @click="scrollTo('wedding-info')"
            >
              查看详情
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats / Countdown -->
    <section class="wd-stats-wrap">
      <div
        class="wd-stats"
        data-reveal
      >
        <div class="wd-stat">
          <span class="wd-stat-num">{{ countdown.days }}</span>
          <span class="wd-stat-label">距婚礼 · 天</span>
        </div>
        <div class="wd-stat">
          <span class="wd-stat-num">{{ String(countdown.hours).padStart(2, '0') }}</span>
          <span class="wd-stat-label">小时</span>
        </div>
        <div class="wd-stat">
          <span class="wd-stat-num">{{ metDays }}</span>
          <span class="wd-stat-label">相识天数</span>
        </div>
        <div class="wd-stat">
          <span class="wd-stat-num">{{ loveDays }}</span>
          <span class="wd-stat-label">相恋天数</span>
        </div>
      </div>
    </section>

    <!-- Our Story -->
    <section
      id="wedding-story"
      class="wd-section wd-story"
    >
      <div class="wd-story-grid">
        <div
          class="wd-story-copy"
          data-reveal
        >
          <p class="wd-kicker">— Our Story</p>
          <h2 class="wd-h2">从初见,到余生</h2>
          <p class="wd-paragraph">
            2020 年那个微凉的春天,我们在一节再普通不过的下午课上偶遇。
            后来,是无数个并肩走过的傍晚,是一杯杯被分享的咖啡,是为彼此留的那盏夜灯。
          </p>
          <p class="wd-paragraph">
            我们决定,把这份漫长又安静的喜欢,变成一生一世的承诺。
            金秋十月,西子湖畔,等你来见证。
          </p>
          <div class="wd-rings">
            <svg viewBox="0 0 140 80" xmlns="http://www.w3.org/2000/svg">
              <g fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round">
                <circle cx="56" cy="44" r="26" />
                <circle cx="86" cy="44" r="26" />
                <path d="M52 18 L56 12 L60 18 Z" fill="currentColor" stroke="none" />
                <path d="M82 18 L86 12 L90 18 Z" fill="currentColor" stroke="none" />
              </g>
            </svg>
          </div>
        </div>
        <div
          class="wd-story-portrait"
          data-reveal
        >
          <img
            :src="storyPortrait"
            alt="couple portrait"
          />
          <div class="wd-story-portrait-frame" />
        </div>
      </div>
    </section>

    <!-- Gallery -->
    <section
      id="wedding-gallery"
      class="wd-section wd-gallery-wrap"
    >
      <div
        class="wd-section-head"
        data-reveal
      >
        <p class="wd-kicker">— Moments</p>
        <h2 class="wd-h2">那些被光照亮的日子</h2>
      </div>
      <div class="wd-gallery">
        <figure
          v-for="(img, i) in galleryImages"
          :key="i"
          class="wd-gallery-item"
          :class="{ 'wd-gallery-tall': i % 3 === 1 }"
          data-reveal
        >
          <img
            :src="img"
            :alt="`moment ${i + 1}`"
          />
        </figure>
      </div>
    </section>

    <!-- Event Info -->
    <section
      id="wedding-info"
      class="wd-section wd-info-wrap"
    >
      <div
        class="wd-section-head"
        data-reveal
      >
        <p class="wd-kicker">— Save the Date</p>
        <h2 class="wd-h2">{{ wedding.dateLabel }}</h2>
        <p class="wd-paragraph wd-center">{{ wedding.weekday }} · {{ wedding.ceremonyTime }}</p>
      </div>
      <div class="wd-info-cards">
        <article
          class="wd-info-card"
          data-reveal
        >
          <div class="wd-info-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 6v6l4 2" stroke-linecap="round" />
            </svg>
          </div>
          <h3 class="wd-info-title">仪式时间</h3>
          <p class="wd-info-line">2026 年 10 月 01 日</p>
          <p class="wd-info-line wd-muted">迎宾 10:30 · 仪式 11:08</p>
        </article>
        <article
          class="wd-info-card"
          data-reveal
        >
          <div class="wd-info-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
              <path d="M12 2C8 2 5 5 5 9c0 5 7 13 7 13s7-8 7-13c0-4-3-7-7-7z" />
              <circle cx="12" cy="9" r="2.4" />
            </svg>
          </div>
          <h3 class="wd-info-title">婚宴地点</h3>
          <p class="wd-info-line">{{ wedding.venueName }}</p>
          <p class="wd-info-line wd-muted">{{ wedding.venueAddress }}</p>
        </article>
        <article
          class="wd-info-card"
          data-reveal
        >
          <div class="wd-info-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
              <path d="M4 7h16v12H4z" />
              <path d="M4 7l8 6 8-6" />
            </svg>
          </div>
          <h3 class="wd-info-title">着装建议</h3>
          <p class="wd-info-line">Garden Elegant</p>
          <p class="wd-info-line wd-muted">米色 / 燕麦 / 雾粉</p>
        </article>
      </div>
    </section>

    <!-- Wishes (powered by CommentBoard) -->
    <section
      id="wedding-wishes"
      class="wd-section wd-wishes-wrap"
    >
      <div
        class="wd-section-head"
        data-reveal
      >
        <p class="wd-kicker">— Wishes</p>
        <h2 class="wd-h2">来自挚友的祝福</h2>
      </div>
      <div
        class="wd-wishes-board"
        data-reveal
      >
        <CommentBoard
          target-type="wedding"
          target-id="default"
          title="留下你的祝福"
          subtitle="让每一份心意都被记得"
          input-placeholder="送上你的祝福或一段故事 ……"
        />
      </div>
    </section>

    <!-- RSVP -->
    <section
      id="wedding-rsvp"
      class="wd-section wd-rsvp-wrap"
    >
      <div class="wd-rsvp">
        <div
          class="wd-rsvp-copy"
          data-reveal
        >
          <p class="wd-kicker">— RSVP</p>
          <h2 class="wd-h2">回复您的出席</h2>
          <p class="wd-paragraph">
            您的到来,是我们最大的心愿。请于 2026 年 09 月 15 日前告知,以便我们为您准备座位与餐食。
          </p>
        </div>
        <form
          class="wd-rsvp-form"
          data-reveal
          @submit.prevent="submitRsvp"
        >
          <label class="wd-field">
            <span>姓名 / Name</span>
            <input
              v-model="rsvp.name"
              type="text"
              placeholder="您的称呼"
            />
          </label>
          <label class="wd-field">
            <span>出席 / Attendance</span>
            <div class="wd-radio-row">
              <label class="wd-radio">
                <input v-model="rsvp.attendance" type="radio" value="yes" />
                <span>欣然赴约</span>
              </label>
              <label class="wd-radio">
                <input v-model="rsvp.attendance" type="radio" value="no" />
                <span>遗憾缺席</span>
              </label>
            </div>
          </label>
          <label class="wd-field">
            <span>同行人数 / Guests</span>
            <input
              v-model.number="rsvp.guests"
              type="number"
              min="1"
              max="6"
            />
          </label>
          <label class="wd-field">
            <span>祝福 / Wishes</span>
            <textarea
              v-model="rsvp.message"
              rows="3"
              placeholder="给新人留下一段话"
            />
          </label>
          <button
            type="submit"
            class="wd-btn wd-btn-dark wd-btn-block"
            :disabled="submitting"
          >
            {{ submitting ? '正在送出…' : '送出心意 →' }}
          </button>
          <p
            v-if="submitStatus"
            class="wd-rsvp-status"
          >
            {{ submitStatus }}
          </p>
        </form>
      </div>
    </section>

    <!-- Footer -->
    <footer class="wd-foot">
      <div class="wd-foot-mark">{{ couple.monogram }}</div>
      <p class="wd-foot-line">
        {{ couple.groomCn }} & {{ couple.brideCn }} · {{ wedding.dateLabel }}
      </p>
      <p class="wd-foot-meta">made with love · {{ wedding.venueName }}</p>
    </footer>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,400&family=Noto+Serif+SC:wght@300;400;500&family=Inter:wght@300;400;500&display=swap');

.wedding-page {
  /* Local design tokens — independent of xmt theme */
  --wd-bg: #faf3ec;
  --wd-bg-soft: #f5ede3;
  --wd-bg-pill: #ebd9c6;
  --wd-ink: #2a1f19;
  --wd-ink-soft: #5b4538;
  --wd-muted: #8b6f5d;
  --wd-line: rgba(139, 111, 93, 0.22);
  --wd-accent: #c9967a;
  --wd-dark: #1a1612;
  --wd-cream: #fffaf2;

  --wd-serif: 'Cormorant Garamond', 'Noto Serif SC', 'Source Serif 4', Georgia, serif;
  --wd-cn: 'Noto Serif SC', 'Source Han Serif SC', 'Songti SC', serif;
  --wd-sans: 'Inter', 'Avenir Next', 'Segoe UI', sans-serif;

  background: var(--wd-bg);
  color: var(--wd-ink);
  font-family: var(--wd-sans);
  min-height: 100vh;
  overflow-x: hidden;
}

/* Reveal */
[data-reveal] {
  opacity: 0;
  transform: translateY(18px);
  transition:
    opacity 700ms cubic-bezier(0.22, 0.61, 0.36, 1),
    transform 700ms cubic-bezier(0.22, 0.61, 0.36, 1);
  transition-delay: var(--reveal-delay, 0ms);
}
[data-reveal].is-revealed {
  opacity: 1;
  transform: none;
}

/* ===== Hero ===== */
.wd-hero {
  position: relative;
  min-height: 92vh;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--wd-cream);
  overflow: hidden;
}
.wd-hero-bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  transform: scale(1.04);
  filter: brightness(0.78) saturate(0.92);
}
.wd-hero-veil {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(26, 22, 18, 0.32) 0%, rgba(26, 22, 18, 0.12) 40%, rgba(26, 22, 18, 0.55) 100%),
    radial-gradient(60% 50% at 30% 50%, rgba(0, 0, 0, 0.18), transparent 60%);
}
.wd-hero-corner {
  position: absolute;
  width: 200px;
  height: 200px;
  color: rgba(255, 250, 242, 0.55);
  z-index: 2;
  pointer-events: none;
}
.wd-hero-corner-tl { top: 24px; left: 24px; }
.wd-hero-corner-br { bottom: 24px; right: 24px; }

.wd-hero-inner {
  position: relative;
  z-index: 3;
  max-width: 1180px;
  width: 100%;
  padding: 100px 48px;
}
.wd-hero-copy {
  max-width: 640px;
}
.wd-hero-eyebrow {
  font-family: var(--wd-serif);
  font-style: italic;
  font-size: 1.05rem;
  letter-spacing: 0.08em;
  margin: 0 0 18px;
  opacity: 0.92;
}
.wd-hero-title {
  font-family: var(--wd-serif);
  font-weight: 400;
  font-size: clamp(3rem, 7.2vw, 6.2rem);
  line-height: 1.02;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.2em;
}
.wd-hero-name { letter-spacing: 0.01em; }
.wd-hero-amp {
  font-style: italic;
  font-weight: 300;
  opacity: 0.85;
}
.wd-hero-sub {
  font-family: var(--wd-cn);
  font-size: 1.05rem;
  letter-spacing: 0.1em;
  margin: 22px 0 36px;
  opacity: 0.86;
}
.wd-hero-date {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 38px;
}
.wd-hero-date-num {
  font-family: var(--wd-serif);
  font-size: 1.7rem;
  letter-spacing: 0.32em;
}
.wd-hero-date-meta {
  font-size: 0.84rem;
  letter-spacing: 0.24em;
  opacity: 0.78;
  text-transform: uppercase;
}
.wd-hero-actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

/* ===== Buttons ===== */
.wd-btn {
  cursor: pointer;
  font-family: var(--wd-sans);
  font-size: 0.92rem;
  font-weight: 500;
  letter-spacing: 0.1em;
  padding: 14px 26px;
  border: none;
  border-radius: 2px;
  transition: transform 200ms ease, background 200ms ease, color 200ms ease;
}
.wd-btn-dark {
  background: var(--wd-dark);
  color: var(--wd-cream);
}
.wd-btn-dark:hover { background: #000; transform: translateY(-1px); }
.wd-btn-dark:disabled { opacity: 0.6; cursor: progress; }
.wd-btn-ghost {
  background: transparent;
  color: var(--wd-cream);
  border: 1px solid rgba(255, 250, 242, 0.6);
}
.wd-btn-ghost:hover { background: rgba(255, 250, 242, 0.1); }
.wd-btn-block { width: 100%; padding: 16px; }

/* ===== Stats ===== */
.wd-stats-wrap {
  padding: 0 24px;
  margin-top: -40px;
  position: relative;
  z-index: 4;
}
.wd-stats {
  max-width: 1080px;
  margin: 0 auto;
  background: var(--wd-bg-pill);
  border-radius: 12px;
  padding: 32px 48px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 32px;
  box-shadow: 0 12px 36px rgba(139, 111, 93, 0.18);
}
.wd-stat {
  text-align: center;
}
.wd-stat-num {
  font-family: var(--wd-serif);
  font-size: 3rem;
  font-weight: 500;
  line-height: 1;
  display: block;
  color: var(--wd-ink);
}
.wd-stat-label {
  font-size: 0.78rem;
  letter-spacing: 0.2em;
  color: var(--wd-muted);
  margin-top: 8px;
  display: block;
}

/* ===== Section base ===== */
.wd-section {
  max-width: 1180px;
  margin: 0 auto;
  padding: 120px 48px;
}
.wd-section-head {
  text-align: center;
  margin-bottom: 56px;
}
.wd-kicker {
  font-family: var(--wd-serif);
  font-style: italic;
  font-size: 1rem;
  color: var(--wd-accent);
  letter-spacing: 0.1em;
  margin: 0 0 12px;
}
.wd-h2 {
  font-family: var(--wd-serif);
  font-weight: 400;
  font-size: clamp(2.2rem, 4.6vw, 3.6rem);
  line-height: 1.1;
  margin: 0;
  color: var(--wd-ink);
}
.wd-paragraph {
  font-family: var(--wd-cn);
  font-size: 1rem;
  line-height: 1.95;
  color: var(--wd-ink-soft);
  margin: 0 0 14px;
  letter-spacing: 0.04em;
}
.wd-center { text-align: center; }
.wd-muted { color: var(--wd-muted); }

/* ===== Story ===== */
.wd-story {
  background: var(--wd-bg-soft);
  max-width: none;
  padding-left: 0;
  padding-right: 0;
}
.wd-story-grid {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 48px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 64px;
  align-items: center;
}
.wd-story-copy {
  max-width: 480px;
}
.wd-story-copy .wd-h2 { margin-bottom: 28px; }
.wd-rings {
  margin-top: 36px;
  color: var(--wd-accent);
  width: 140px;
}
.wd-story-portrait {
  position: relative;
  aspect-ratio: 3 / 4;
}
.wd-story-portrait img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  filter: brightness(0.95) saturate(0.94);
}
.wd-story-portrait-frame {
  position: absolute;
  inset: 18px -18px -18px 18px;
  border: 1px solid var(--wd-accent);
  z-index: -1;
}

/* ===== Gallery ===== */
.wd-gallery {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}
.wd-gallery-item {
  margin: 0;
  overflow: hidden;
  aspect-ratio: 4 / 5;
}
.wd-gallery-item.wd-gallery-tall { aspect-ratio: 4 / 6.2; }
.wd-gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 900ms cubic-bezier(0.22, 0.61, 0.36, 1);
  filter: brightness(0.96) saturate(0.92);
}
.wd-gallery-item:hover img { transform: scale(1.04); }

/* ===== Info ===== */
.wd-info-wrap { background: var(--wd-bg-soft); max-width: none; padding-left: 24px; padding-right: 24px; }
.wd-info-cards {
  max-width: 1180px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}
.wd-info-card {
  background: var(--wd-cream);
  padding: 40px 32px;
  text-align: center;
  border: 1px solid var(--wd-line);
}
.wd-info-icon {
  width: 44px;
  height: 44px;
  margin: 0 auto 22px;
  color: var(--wd-accent);
}
.wd-info-icon svg { width: 100%; height: 100%; }
.wd-info-title {
  font-family: var(--wd-serif);
  font-weight: 500;
  font-size: 1.5rem;
  margin: 0 0 14px;
  color: var(--wd-ink);
}
.wd-info-line {
  font-family: var(--wd-cn);
  font-size: 0.98rem;
  line-height: 1.7;
  color: var(--wd-ink-soft);
  margin: 0;
}

/* ===== Wishes (CommentBoard) ===== */
.wd-wishes-board {
  max-width: 880px;
  margin: 0 auto;
  /* Host tokens for embedded CommentBoard (consumed via --cmt-host-* in CommentBoard.vue) */
  --cmt-host-surface: var(--wd-cream);
  --cmt-host-surface-soft: rgba(201, 150, 122, 0.08);
  --cmt-host-border: var(--wd-line);
  --cmt-host-ink: var(--wd-ink);
  --cmt-host-ink-soft: var(--wd-ink-soft);
  --cmt-host-muted: var(--wd-muted);
  --cmt-host-accent: var(--wd-accent);
  --cmt-host-accent-soft: rgba(201, 150, 122, 0.16);
  --cmt-host-on-accent: var(--wd-cream);
  --cmt-host-radius: 4px;
  --cmt-host-font-serif: var(--wd-serif);
  --cmt-host-font-cn: var(--wd-cn);
}

/* ===== RSVP ===== */
.wd-rsvp-wrap { background: var(--wd-bg-soft); max-width: none; }
.wd-rsvp {
  max-width: 1080px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 72px;
  padding: 0 48px;
}
.wd-rsvp-form {
  display: flex;
  flex-direction: column;
  gap: 22px;
}
.wd-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.wd-field > span {
  font-size: 0.78rem;
  letter-spacing: 0.2em;
  color: var(--wd-muted);
  text-transform: uppercase;
}
.wd-field input[type='text'],
.wd-field input[type='number'],
.wd-field textarea {
  background: var(--wd-cream);
  border: 1px solid var(--wd-line);
  padding: 14px 16px;
  font-family: var(--wd-cn);
  font-size: 1rem;
  color: var(--wd-ink);
  outline: none;
  transition: border-color 200ms ease;
  width: 100%;
  resize: vertical;
}
.wd-field input:focus,
.wd-field textarea:focus { border-color: var(--wd-accent); }
.wd-radio-row { display: flex; gap: 24px; padding-top: 8px; }
.wd-radio {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--wd-cn);
  font-size: 0.98rem;
  color: var(--wd-ink-soft);
  cursor: pointer;
}
.wd-radio input { accent-color: var(--wd-dark); }
.wd-rsvp-status {
  font-family: var(--wd-cn);
  font-size: 0.92rem;
  color: var(--wd-accent);
  margin: 4px 0 0;
  text-align: center;
}

/* ===== Footer ===== */
.wd-foot {
  background: var(--wd-dark);
  color: var(--wd-cream);
  text-align: center;
  padding: 72px 24px;
}
.wd-foot-mark {
  font-family: var(--wd-serif);
  font-style: italic;
  font-size: 3rem;
  font-weight: 400;
  margin-bottom: 16px;
  letter-spacing: 0.08em;
}
.wd-foot-line {
  font-family: var(--wd-cn);
  font-size: 1rem;
  letter-spacing: 0.16em;
  margin: 0 0 10px;
  opacity: 0.9;
}
.wd-foot-meta {
  font-size: 0.78rem;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  margin: 0;
  opacity: 0.5;
}

/* ===== Responsive ===== */
@media (max-width: 899px) {
  .wd-stats { grid-template-columns: repeat(2, 1fr); padding: 24px 28px; gap: 24px; }
  .wd-stat-num { font-size: 2.4rem; }
  .wd-section { padding: 80px 24px; }
  .wd-hero-inner { padding: 80px 24px; }
  .wd-story-grid,
  .wd-info-cards,
  .wd-rsvp { grid-template-columns: 1fr; gap: 36px; padding: 0 24px; }
  .wd-gallery { grid-template-columns: 1fr 1fr; }
  .wd-hero-corner { width: 120px; height: 120px; }
  .wd-hero-title { font-size: clamp(2.4rem, 12vw, 4rem); }
  .wd-hero-date-num { font-size: 1.3rem; letter-spacing: 0.24em; }
}

@media (max-width: 540px) {
  .wd-gallery { grid-template-columns: 1fr; }
  .wd-hero-actions { flex-direction: column; align-items: stretch; }
  .wd-btn { text-align: center; }
  .wd-stats { grid-template-columns: 1fr 1fr; }
}

@media (prefers-reduced-motion: reduce) {
  [data-reveal],
  [data-reveal].is-revealed {
    opacity: 1;
    transform: none;
    transition: none;
  }
}
</style>
