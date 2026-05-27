<script setup>
import { computed, reactive, shallowRef } from 'vue'

import ToolPageHeader from 'src/components/tools/ToolPageHeader.vue'
import { lolPlatformItems, searchLolProfile } from 'src/lib/lol'

const countItems = [
  { label: '最近 5 场', value: '5' },
  { label: '最近 10 场', value: '10' },
  { label: '最近 20 场', value: '20' }
]

const formState = reactive({
  riotId: '',
  platform: 'kr',
  count: '10'
})
const loading = shallowRef(false)
const errorMessage = shallowRef('')
const result = shallowRef(null)

const account = computed(() => result.value?.account || null)
const summoner = computed(() => result.value?.summoner || null)
const ranked = computed(() => result.value?.ranked || [])
const matches = computed(() => result.value?.matches || [])
const assets = computed(() => result.value?.assets || {})
const primaryRank = computed(() => ranked.value[0] || null)
const summary = computed(() => {
  const total = matches.value.length
  const wins = matches.value.filter(match => match.win).length
  const kills = matches.value.reduce((sum, match) => sum + (match.kills || 0), 0)
  const deaths = matches.value.reduce((sum, match) => sum + (match.deaths || 0), 0)
  const assists = matches.value.reduce((sum, match) => sum + (match.assists || 0), 0)

  return {
    total,
    wins,
    winRate: total ? Math.round((wins / total) * 100) : 0,
    averageKda: total ? `${(kills / total).toFixed(1)} / ${(deaths / total).toFixed(1)} / ${(assists / total).toFixed(1)}` : '-'
  }
})

function validate(state) {
  const errors = []
  if (!state.riotId.trim()) {
    errors.push({ name: 'riotId', message: '请输入 Riot ID，例如 Hide on bush#KR1' })
  } else if (!parseRiotId(state.riotId)) {
    errors.push({ name: 'riotId', message: '格式应为 游戏名#Tag，例如 Hide on bush#KR1' })
  }
  return errors
}

function parseRiotId(value) {
  const [gameName, tagLine, ...rest] = value.split('#')
  if (!gameName?.trim() || !tagLine?.trim() || rest.length) return null
  return {
    gameName: gameName.trim(),
    tagLine: tagLine.trim()
  }
}

function formatDuration(seconds) {
  const minutes = Math.floor((seconds || 0) / 60)
  const rest = Math.floor((seconds || 0) % 60)
  return `${minutes}:${String(rest).padStart(2, '0')}`
}

function formatMatchTime(value) {
  if (!value) return ''
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value))
}

function itemIconUrl(item) {
  if (!item?.image || !assets.value.item_base_url) return ''
  return `${assets.value.item_base_url}/${item.image}`
}

function spellIconUrl(spell) {
  if (!spell?.image || !assets.value.spell_base_url) return ''
  return `${assets.value.spell_base_url}/${spell.image}`
}

async function submitSearch() {
  const parsed = parseRiotId(formState.riotId)
  if (!parsed) return

  loading.value = true
  errorMessage.value = ''
  try {
    result.value = await searchLolProfile({
      gameName: parsed.gameName,
      tagLine: parsed.tagLine,
      platform: formState.platform,
      count: Number(formState.count)
    })
  } catch (error) {
    errorMessage.value = error.message || '查询失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="lol-page">
    <ToolPageHeader
      kicker="League of Legends · Riot API"
      title="LoL 战绩查询"
    />

    <section class="lol-shell">
      <div class="lol-toolbar">
        <div class="lol-toolbar-head">
          <div>
            <div class="lol-kicker">查询</div>
            <p class="lol-toolbar-meta">Riot ID 使用 “游戏名#Tag” 格式。API Key 由后端代理，不会暴露到浏览器。</p>
          </div>
          <span
            v-if="result"
            class="lol-toolbar-status"
          >
            {{ result.meta?.platform?.toUpperCase() }} · {{ matches.length }} 场
          </span>
        </div>

        <UForm
          :state="formState"
          :validate="validate"
          class="lol-search-form"
          @submit="submitSearch"
        >
          <UFormField
            class="lol-id-field"
            label="Riot ID"
            name="riotId"
            required
          >
            <UInput
              v-model="formState.riotId"
              class="lol-control"
              placeholder="Hide on bush#KR1"
              :disabled="loading"
            />
          </UFormField>

          <UFormField
            label="服务器"
            name="platform"
          >
            <USelect
              v-model="formState.platform"
              class="lol-control lol-select"
              :items="lolPlatformItems"
              value-key="value"
              label-key="label"
              :disabled="loading"
            />
          </UFormField>

          <UFormField
            label="场次"
            name="count"
          >
            <USelect
              v-model="formState.count"
              class="lol-control lol-select"
              :items="countItems"
              value-key="value"
              label-key="label"
              :disabled="loading"
            />
          </UFormField>

          <UButton
            class="lol-submit brand-action-button"
            label="查询战绩"
            type="submit"
            :loading="loading"
            :disabled="loading"
          />
        </UForm>

        <UAlert
          v-if="errorMessage"
          class="lol-alert"
          color="error"
          variant="soft"
          title="查询失败"
          :description="errorMessage"
        />
      </div>

      <div class="lol-grid">
        <section class="lol-profile-panel">
          <template v-if="result">
            <div class="lol-profile-card">
              <img
                class="lol-avatar"
                :src="summoner?.profile_icon_url"
                alt=""
              >
              <div class="lol-profile-main">
                <div class="lol-name">{{ account?.game_name }}#{{ account?.tag_line }}</div>
                <div class="lol-muted">等级 {{ summoner?.summoner_level || 0 }}</div>
              </div>
            </div>

            <div class="lol-rank-card">
              <div class="lol-kicker">段位</div>
              <template v-if="primaryRank">
                <div class="lol-rank-title">{{ primaryRank.tier }} {{ primaryRank.rank }}</div>
                <div class="lol-muted">
                  {{ primaryRank.queue_label }} · {{ primaryRank.league_points }} LP ·
                  {{ primaryRank.wins }}胜 {{ primaryRank.losses }}负 · {{ primaryRank.win_rate }}%
                </div>
              </template>
              <div
                v-else
                class="lol-empty-text"
              >
                暂无排位数据
              </div>
            </div>

            <div class="lol-stat-strip">
              <div>
                <span>{{ summary.total }}</span>
                <small>对局</small>
              </div>
              <div>
                <span>{{ summary.winRate }}%</span>
                <small>胜率</small>
              </div>
              <div>
                <span>{{ summary.averageKda }}</span>
                <small>场均 K/D/A</small>
              </div>
            </div>
          </template>

          <div
            v-else
            class="lol-empty-text"
          >
            输入 Riot ID 后，这里会显示玩家头像、等级和排位概览。
          </div>
        </section>

        <section class="lol-match-panel">
          <div class="lol-match-head">
            <div>
              <div class="lol-kicker">最近战绩</div>
              <p class="lol-toolbar-meta">展示胜负、英雄、KDA、补刀、伤害和装备。</p>
            </div>
          </div>

          <div
            v-if="loading"
            class="lol-empty-text"
          >
            正在连接 Riot API...
          </div>

          <div
            v-else-if="!matches.length"
            class="lol-empty-text"
          >
            查询后会显示最近比赛。
          </div>

          <div
            v-else
            class="lol-match-list"
          >
            <article
              v-for="match in matches"
              :key="match.match_id"
              class="lol-match-row"
              :class="{ 'lol-match-row-win': match.win }"
            >
              <div class="lol-result">
                <span>{{ match.win ? '胜利' : '失败' }}</span>
                <small>{{ match.queue_label }}</small>
                <small>{{ formatMatchTime(match.game_creation) }}</small>
              </div>

              <img
                class="lol-champion"
                :src="match.champion_icon_url"
                :alt="match.champion.name"
              >

              <div class="lol-match-main">
                <div class="lol-match-title">{{ match.champion.name }}</div>
                <div class="lol-muted">
                  {{ match.kills }} / {{ match.deaths }} / {{ match.assists }}
                  · KDA {{ match.kda }}
                  · {{ formatDuration(match.game_duration) }}
                </div>
                <div class="lol-spells">
                  <img
                    v-for="spell in match.summoner_spells"
                    :key="`${match.match_id}-${spell.id}`"
                    :src="spellIconUrl(spell)"
                    :alt="spell.name"
                  >
                </div>
              </div>

              <div class="lol-match-metrics">
                <span>{{ match.cs }} CS</span>
                <span>{{ match.cs_per_minute }}/分</span>
                <span>{{ match.damage_to_champions.toLocaleString() }} 伤害</span>
              </div>

              <div class="lol-items">
                <span
                  v-for="slot in 7"
                  :key="`${match.match_id}-slot-${slot}`"
                  class="lol-item-slot"
                >
                  <img
                    v-if="match.items[slot - 1]"
                    :src="itemIconUrl(match.items[slot - 1])"
                    :alt="match.items[slot - 1].name"
                  >
                </span>
              </div>
            </article>
          </div>
        </section>
      </div>
    </section>
  </main>
</template>

<style scoped>
.lol-page {
  min-height: calc(100vh - 76px);
  padding-bottom: 72px;
}

.lol-shell {
  margin: 0 auto;
  max-width: 1180px;
  padding: 28px 20px 0;
}

.lol-toolbar,
.lol-profile-panel,
.lol-match-panel {
  background: var(--shell-panel);
  border: 1px solid var(--brand-color-border);
  border-radius: var(--brand-radius-lg, 24px);
  box-shadow: var(--brand-shadow-card, var(--shell-shadow));
  min-width: 0;
}

.lol-toolbar {
  padding: 20px;
}

.lol-toolbar-head,
.lol-match-head,
.lol-profile-card {
  align-items: center;
  display: flex;
  gap: 14px;
  justify-content: space-between;
}

.lol-kicker {
  color: var(--brand-color-muted);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.lol-toolbar-meta,
.lol-muted,
.lol-empty-text {
  color: var(--brand-color-muted);
  font-size: 0.9rem;
  line-height: 1.55;
  margin: 6px 0 0;
}

.lol-toolbar-status {
  color: var(--brand-color-accent);
  font-size: 0.88rem;
  font-weight: 800;
  white-space: nowrap;
}

.lol-search-form {
  align-items: flex-start;
  display: grid;
  gap: 12px;
  grid-template-columns: minmax(220px, 1fr) minmax(150px, 0.34fr) minmax(130px, 0.24fr) auto;
  margin-top: 16px;
}

.lol-submit {
  align-self: end;
  min-height: 40px;
}

.lol-alert {
  margin-top: 14px;
}

.lol-grid {
  display: grid;
  gap: 20px;
  grid-template-columns: minmax(280px, 0.38fr) minmax(0, 1fr);
  margin-top: 20px;
}

.lol-profile-panel,
.lol-match-panel {
  padding: 22px;
}

.lol-profile-card {
  justify-content: flex-start;
}

.lol-avatar,
.lol-champion {
  background: var(--brand-color-surface-2);
  border: 1px solid var(--brand-color-border);
  border-radius: var(--brand-radius-md, 16px);
  object-fit: cover;
}

.lol-avatar {
  height: 72px;
  width: 72px;
}

.lol-profile-main {
  min-width: 0;
}

.lol-name {
  color: var(--brand-color-text);
  font-size: 1.2rem;
  font-weight: 900;
  overflow-wrap: anywhere;
}

.lol-rank-card,
.lol-stat-strip {
  border-top: 1px solid var(--brand-color-border);
  margin-top: 18px;
  padding-top: 18px;
}

.lol-rank-title {
  color: var(--brand-color-text);
  font-size: 1.45rem;
  font-weight: 900;
  margin-top: 6px;
}

.lol-stat-strip {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.lol-stat-strip span {
  color: var(--brand-color-text);
  display: block;
  font-size: 1.05rem;
  font-weight: 900;
}

.lol-stat-strip small {
  color: var(--brand-color-muted);
  font-size: 0.76rem;
}

.lol-match-list {
  display: grid;
  gap: 10px;
  margin-top: 16px;
}

.lol-match-row {
  align-items: center;
  background: var(--brand-color-surface);
  border: 1px solid var(--brand-color-border);
  border-left: 4px solid #e14d4d;
  border-radius: var(--brand-radius-md, 16px);
  display: grid;
  gap: 12px;
  grid-template-columns: 86px 56px minmax(0, 1fr) 130px 180px;
  padding: 12px;
}

.lol-match-row-win {
  border-left-color: var(--brand-color-accent);
}

.lol-result {
  display: grid;
  gap: 3px;
}

.lol-result span {
  color: var(--brand-color-text);
  font-weight: 900;
}

.lol-result small,
.lol-match-metrics span {
  color: var(--brand-color-muted);
  font-size: 0.78rem;
}

.lol-champion {
  height: 52px;
  width: 52px;
}

.lol-match-main {
  min-width: 0;
}

.lol-match-title {
  color: var(--brand-color-text);
  font-size: 1rem;
  font-weight: 900;
}

.lol-spells,
.lol-items {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 7px;
}

.lol-spells img,
.lol-item-slot,
.lol-item-slot img {
  border-radius: var(--brand-radius-sm, 8px);
  height: 24px;
  width: 24px;
}

.lol-spells img,
.lol-item-slot img {
  display: block;
}

.lol-item-slot {
  background: var(--brand-color-surface-2);
  border: 1px solid var(--brand-color-border);
}

.lol-match-metrics {
  display: grid;
  gap: 4px;
  justify-items: end;
}

.lol-items {
  justify-content: flex-end;
  margin-top: 0;
}

@media (max-width: 1023px) {
  .lol-search-form,
  .lol-grid,
  .lol-match-row {
    grid-template-columns: 1fr;
  }

  .lol-submit {
    align-self: auto;
    width: 100%;
  }

  .lol-match-row {
    align-items: start;
  }

  .lol-match-metrics,
  .lol-items {
    justify-items: start;
    justify-content: flex-start;
  }
}

@media (max-width: 599px) {
  .lol-shell {
    padding-inline: 14px;
  }

  .lol-toolbar-head,
  .lol-match-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .lol-stat-strip {
    grid-template-columns: 1fr;
  }
}
</style>
