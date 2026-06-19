<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { Icon } from '@iconify/vue'

const inputText = ref('')
const result = ref(null)
const loading = ref(false)
const copied = ref(false)
const errorMsg = ref(null)

// Bug 1 fix: wrap localStorage read in try/catch agar tidak crash
// jika nilai corrupt atau JSON.parse gagal
const loadHistory = () => {
  try {
    return JSON.parse(localStorage.getItem('syntaxerr-history')) || []
  } catch {
    return []
  }
}

const history = ref(loadHistory())

const copyCode = async () => {
  if (!result.value?.fixed_code) return
  // Potensi 2: tetap pakai fixed_code sebagai plain text, bukan v-html
  // sehingga aman dari XSS
  await navigator.clipboard.writeText(result.value.fixed_code)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

// Potensi 1 fix: gunakan abort controller untuk batalkan request lama
// jika user klik Analyze lagi sebelum request selesai
let currentController = null

// ── Floating Particles Background ──
const canvasRef = ref(null)
let animFrameId = null

onMounted(() => {
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  let W, H, pts

  const resize = () => {
    W = canvas.width = window.innerWidth
    H = canvas.height = window.innerHeight
    pts = Array.from({ length: 80 }, () => ({
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
      r: Math.random() * 1.4 + 0.4
    }))
  }

  resize()
  window.addEventListener('resize', resize)

  const draw = () => {
    ctx.clearRect(0, 0, W, H)
    for (let i = 0; i < pts.length; i++) {
      const p = pts[i]
      p.x += p.vx
      p.y += p.vy
      if (p.x < 0) p.x = W
      if (p.x > W) p.x = 0
      if (p.y < 0) p.y = H
      if (p.y > H) p.y = 0

      for (let j = i + 1; j < pts.length; j++) {
        const q = pts[j]
        const dx = p.x - q.x
        const dy = p.y - q.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < 100) {
          ctx.strokeStyle = `rgba(71,85,105,${0.45 * (1 - dist / 100)})`
          ctx.lineWidth = 0.5
          ctx.beginPath()
          ctx.moveTo(p.x, p.y)
          ctx.lineTo(q.x, q.y)
          ctx.stroke()
        }
      }

      ctx.fillStyle = 'rgba(100,116,139,0.6)'
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
      ctx.fill()
    }
    animFrameId = requestAnimationFrame(draw)
  }

  draw()

  onUnmounted(() => {
    cancelAnimationFrame(animFrameId)
    window.removeEventListener('resize', resize)
  })
})

const analyzeError = async () => {
  if (!inputText.value.trim()) return

  // Batalkan request sebelumnya jika masih berjalan
  if (currentController) {
    currentController.abort()
  }
  currentController = new AbortController()

  loading.value = true
  result.value = null
  errorMsg.value = null

  try {
    const response = await axios.post(
      'http://127.0.0.1:8000/analyze',
      { content: inputText.value },
      { signal: currentController.signal }
    )

    result.value = response.data
    const data = response.data || {}

    history.value.unshift({
      id: Date.now(),
      input: inputText.value,
      error: data.error_name || 'Unknown Error',
      language: data.language || 'Unknown'
    })

    history.value = history.value.slice(0, 5)

    // Bug 1 fix: wrap localStorage write juga dalam try/catch
    try {
      localStorage.setItem('syntaxerr-history', JSON.stringify(history.value))
    } catch {
      console.warn('Gagal menyimpan history ke localStorage.')
    }
  } catch (err) {
    // Abaikan error jika request sengaja dibatalkan (bukan bug)
    if (axios.isCancel(err) || err.name === 'CanceledError') return

    // Bug 2 fix: tampilkan pesan error ke user, bukan hanya console
    console.error(err)
    errorMsg.value = 'Gagal menghubungi server. Pastikan backend sudah berjalan di port 8000.'
  } finally {
    loading.value = false
    currentController = null
  }
}
</script>

<template>
  <canvas ref="canvasRef" class="particles-canvas"></canvas>
  <div class="app">

    <!-- Header -->
    <div class="header">
      <div class="header-icon">
        <Icon icon="mdi:bug-outline" width="20" />
      </div>
      <div>
        <div class="header-title">SyntaxErr.</div>
        <div class="header-sub">AI-powered programming error analyzer</div>
      </div>
      <div class="header-badge">Gemini · LangChain · LangGraph · LangSmith</div>
    </div>

    <!-- Input -->
    <div class="input-block">
      <div class="input-label">Error message or source code</div>
      <textarea
        v-model="inputText"
        rows="8"
        placeholder="Paste your error message or broken code here..."
      ></textarea>
      <div class="input-footer">
        <span class="input-hint">Supports Python, JS, TypeScript, Go, Rust, and more</span>
        <button
          class="analyze-btn"
          @click="analyzeError"
          :disabled="loading"
        >
          <Icon icon="mdi:magnify" width="16" />
          {{ loading ? 'Analyzing...' : 'Analyze' }}
        </button>
      </div>
    </div>

    <!-- History chips -->
    <div v-if="history.length" class="history-strip">
      <div
        v-for="item in history"
        :key="item.id"
        class="history-chip"
      >
        <Icon icon="mdi:history" width="13" />
        {{ item.error }}
        <span class="chip-lang">· {{ item.language }}</span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-row">
      <div class="spinner"></div>
      Menganalisis input...
    </div>

    <!-- Error banner (Bug 2 fix) -->
    <div v-if="errorMsg" class="error-banner">
      <Icon icon="mdi:alert-circle-outline" width="16" />
      {{ errorMsg }}
    </div>

    <!-- Empty state -->
    <div v-if="!loading && !result && !errorMsg" class="empty-state">
      <Icon icon="mdi:terminal" width="36" />
      <p>Paste an error message or source code above,<br>then click Analyze to get started.</p>
    </div>

    <!-- Result -->
    <div v-if="result && !loading" class="result-wrap">

      <!-- Meta cards -->
      <div class="meta-row">
        <div class="meta-card">
          <div class="meta-label">
            <Icon icon="mdi:shape-outline" width="13" />
            Input type
          </div>
          <div class="meta-val">{{ result.input_type }}</div>
        </div>
        <div class="meta-card">
          <div class="meta-label">
            <Icon icon="mdi:code-tags" width="13" />
            Language
          </div>
          <div class="meta-val">{{ result.language }}</div>
        </div>
        <div class="meta-card">
          <div class="meta-label">
            <Icon icon="mdi:alert-circle-outline" width="13" />
            Error type
          </div>
          <div class="meta-val">{{ result.error_name }}</div>
        </div>
      </div>

      <!-- Translation -->
      <div class="section-card">
        <div class="section-head">
          <div class="section-head-left">
            <Icon icon="mdi:translate" width="16" />
            Translation
          </div>
        </div>
        <div class="section-body">{{ result.translation }}</div>
      </div>

      <!-- Explanation -->
      <div class="section-card">
        <div class="section-head">
          <div class="section-head-left">
            <Icon icon="mdi:book-open-outline" width="16" />
            Explanation
          </div>
        </div>
        <div class="section-body">{{ result.explanation }}</div>
      </div>

      <!-- Solution -->
      <div class="section-card">
        <div class="section-head">
          <div class="section-head-left">
            <Icon icon="mdi:lightbulb-outline" width="16" />
            Solution
          </div>
        </div>
        <div class="section-body">
          <ul v-if="Array.isArray(result.solution)" class="solution-list">
            <li v-for="(item, index) in result.solution" :key="index">
              {{ item }}
            </li>
          </ul>
        </div>
      </div>

      <!-- Fixed code -->
      <div v-if="result.fixed_code" class="section-card">
        <div class="section-head">
          <div class="section-head-left">
            <Icon icon="mdi:code-braces" width="16" />
            Fixed code
          </div>
          <button class="copy-btn" @click="copyCode">
            <Icon :icon="copied ? 'mdi:check' : 'mdi:content-copy'" width="13" />
            {{ copied ? 'Copied!' : 'Copy' }}
          </button>
        </div>
        <pre>{{ result.fixed_code }}</pre>
      </div>

    </div>
  </div>
</template>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background: #0a0f1a;
  color: #e2e8f0;
  font-family: Inter, system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* ── Particles canvas ── */
.particles-canvas {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.app {
  position: relative;
  z-index: 1;
  max-width: 860px;
  margin: 0 auto;
  padding: 40px 24px 80px;
}

/* ── Header ── */
.header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 2.5rem;
}

.header-icon {
  width: 38px;
  height: 38px;
  background: #151d2e;
  border: 0.5px solid #2a3448;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  flex-shrink: 0;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #f1f5f9;
  letter-spacing: -0.3px;
}

.header-sub {
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

.header-badge {
  margin-left: auto;
  font-size: 11px;
  color: #64748b;
  background: #151d2e;
  border: 0.5px solid #2a3448;
  padding: 4px 10px;
  border-radius: 20px;
  white-space: nowrap;
}

/* ── Input block ── */
.input-block {
  background: #111827;
  border: 0.5px solid #1e2d45;
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.input-label {
  padding: 13px 16px 0;
  font-size: 11px;
  font-weight: 500;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.07em;
}

textarea {
  width: 100%;
  resize: none;
  border: none;
  outline: none;
  background: transparent;
  color: #e2e8f0;
  padding: 10px 16px 14px;
  font-size: 13.5px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  line-height: 1.75;
}

textarea::placeholder {
  color: #334155;
  font-family: Inter, sans-serif;
}

.input-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-top: 0.5px solid #1e2d45;
  background: #0d1520;
}

.input-hint {
  font-size: 12px;
  color: #475569;
}

.analyze-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  background: #e2e8f0;
  color: #0a0f1a;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.15s;
  font-family: inherit;
}

.analyze-btn:hover { opacity: 0.85; }
.analyze-btn:disabled { opacity: 0.35; cursor: not-allowed; }

/* ── History chips ── */
.history-strip {
  display: flex;
  gap: 7px;
  flex-wrap: wrap;
  margin-bottom: 1.25rem;
}

.history-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  background: #111827;
  border: 0.5px solid #1e2d45;
  border-radius: 20px;
  padding: 5px 11px;
  font-size: 12px;
  color: #64748b;
}

.chip-lang {
  color: #334155;
}

/* ── Loading ── */
.loading-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 0;
  font-size: 14px;
  color: #64748b;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 1.5px solid #1e2d45;
  border-top-color: #94a3b8;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Error banner (Bug 2 fix) ── */
.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #1f0f0f;
  border: 0.5px solid #4a1515;
  border-radius: 10px;
  padding: 12px 16px;
  font-size: 13px;
  color: #f87171;
  margin-bottom: 1rem;
}

/* ── Empty state ── */
.empty-state {
  padding: 3.5rem 1rem;
  text-align: center;
  color: #334155;
}

.empty-state p {
  font-size: 14px;
  margin-top: 12px;
  line-height: 1.7;
}

/* ── Result ── */
.result-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.meta-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.meta-card {
  background: #111827;
  border: 0.5px solid #1e2d45;
  border-radius: 10px;
  padding: 14px 16px;
}

.meta-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  font-weight: 500;
  margin-bottom: 7px;
}

.meta-val {
  font-size: 15px;
  font-weight: 500;
  color: #f1f5f9;
}

.section-card {
  background: #111827;
  border: 0.5px solid #1e2d45;
  border-radius: 12px;
  overflow: hidden;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 11px 16px;
  border-bottom: 0.5px solid #1e2d45;
}

.section-head-left {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.07em;
}

.section-body {
  padding: 14px 16px;
  font-size: 14px;
  color: #cbd5e1;
  line-height: 1.8;
}

.solution-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.solution-list li {
  display: flex;
  gap: 10px;
  line-height: 1.7;
}

.solution-list li::before {
  content: '';
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #334155;
  flex-shrink: 0;
  margin-top: 9px;
}

pre {
  margin: 0;
  background: #0d1520;
  padding: 14px 16px;
  font-size: 13px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  overflow-x: auto;
  line-height: 1.75;
  color: #e2e8f0;
}

.copy-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #64748b;
  background: none;
  border: 0.5px solid #2a3448;
  padding: 5px 10px;
  border-radius: 7px;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s;
}

.copy-btn:hover {
  background: #0d1520;
  color: #94a3b8;
}

/* ── Responsive ── */
@media (max-width: 600px) {
  .meta-row { grid-template-columns: 1fr; }
  .header-badge { display: none; }
  .app { padding: 24px 16px 60px; }
}
</style>