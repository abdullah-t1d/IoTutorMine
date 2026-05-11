<template>
  <main class="home">
    <div class="container">
      <!-- Extract Components Section -->
      <section class="home__section home__extract">
        <h2 class="home__heading">Extract Components</h2>
        <p class="home__subtitle">Paste a YouTube IoT tutorial URL and let our LLM extract the electrical components for you.</p>

        <div class="extract-bar">
          <input
            id="youtube-url-input"
            type="text"
            class="extract-input"
            v-model="youtubeUrl"
            placeholder="https://www.youtube.com/watch?v=..."
          />
          <button class="extract-btn" @click="showDevNotice = true">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
            Extract Components
          </button>
        </div>

        <div v-if="showDevNotice" class="extract-notice">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          This feature is currently under development. Stay tuned!
          <button class="extract-notice__close" @click="showDevNotice = false" aria-label="Dismiss">×</button>
        </div>
      </section>

      <!-- Videos Section -->
      <section class="home__section">
        <h1 class="home__heading">Videos</h1>
        <SearchBar v-model="searchQuery" @search="filterVideos" />

        <div class="video-grid">
          <VideoCard
            v-for="video in filteredVideos"
            :key="video.id"
            :video="video"
          />
        </div>

        <p v-if="filteredVideos.length === 0" class="home__empty">
          No videos found matching "{{ searchQuery }}".
        </p>
      </section>
    </div>
  </main>
</template>

<script setup>
import { ref, computed } from 'vue'
import SearchBar from '../components/SearchBar.vue'
import VideoCard from '../components/VideoCard.vue'
import { videos } from '../data/videos.js'

const searchQuery = ref('')
const youtubeUrl = ref('')
const showDevNotice = ref(false)

const filteredVideos = computed(() => {
  const q = searchQuery.value.toLowerCase().trim()
  if (!q) return videos
  return videos.filter(v =>
    v.title.toLowerCase().includes(q) ||
    v.tags.some(t => t.toLowerCase().includes(q)) ||
    v.components.some(c => c.name.toLowerCase().includes(q)) ||
    v.creator.toLowerCase().includes(q)
  )
})

function filterVideos() {
  // search is reactive via computed, this is a no-op placeholder
}
</script>

<style scoped>
.home {
  flex: 1;
  padding: var(--space-xl) 0 var(--space-2xl);
}

.home__section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
}

.home__extract {
  margin-bottom: var(--space-lg);
}

.home__heading {
  font-size: var(--font-size-xl);
  font-weight: 700;
  margin-bottom: var(--space-sm);
  color: var(--color-text-primary);
}

.home__subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--space-lg);
}

.extract-bar {
  display: flex;
  gap: var(--space-sm);
}

.extract-input {
  flex: 1;
  padding: 10px 16px;
  font-size: var(--font-size-base);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text-primary);
  outline: none;
  transition: border-color 0.15s;
}

.extract-input:focus {
  border-color: var(--color-accent);
}

.extract-input::placeholder {
  color: var(--color-text-muted);
}

.extract-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: #fff;
  background: var(--color-accent);
  border: none;
  border-radius: var(--radius-sm);
  white-space: nowrap;
  transition: background 0.15s;
}

.extract-btn:hover {
  background: var(--color-accent-hover);
}

.extract-notice {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: var(--space-md);
  padding: 12px 16px;
  font-size: var(--font-size-sm);
  color: var(--color-warning-text);
  background: var(--color-warning-bg);
  border: 1px solid var(--color-warning-border);
  border-radius: var(--radius-sm);
}

.extract-notice__close {
  margin-left: auto;
  background: none;
  border: none;
  font-size: 1.2rem;
  color: var(--color-warning-text);
  padding: 0 4px;
  line-height: 1;
}

.extract-notice__close:hover {
  opacity: 0.7;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-lg);
}

.home__empty {
  text-align: center;
  color: var(--color-text-muted);
  padding: var(--space-2xl) 0;
  font-size: var(--font-size-base);
}

@media (max-width: 1024px) {
  .video-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .video-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .extract-bar {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .video-grid {
    grid-template-columns: 1fr;
  }

  .home__section {
    padding: var(--space-md);
  }
}
</style>
