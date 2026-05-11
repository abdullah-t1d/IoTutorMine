<template>
  <router-link :to="`/video/${video.id}`" class="video-card" :id="`video-card-${video.id}`">
    <div class="video-card__thumb">
      <img :src="video.thumbnail" :alt="video.title" loading="lazy" />
      <span class="video-card__duration">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        {{ video.durationRange }} min
      </span>
    </div>

    <div class="video-card__body">
      <h3 class="video-card__title">{{ video.title }}</h3>

      <div class="video-card__meta">
        <span class="video-card__creator">{{ video.creator }}</span>
      </div>

      <div class="video-card__components">
        <span
          v-for="comp in video.components.slice(0, 3)"
          :key="comp"
          class="component-badge"
        >
          {{ comp }}
        </span>
        <span v-if="video.components.length > 3" class="component-badge component-badge--more">
          +{{ video.components.length - 3 }}
        </span>
      </div>
    </div>
  </router-link>
</template>

<script setup>
defineProps({
  video: { type: Object, required: true }
})
</script>

<style scoped>
.video-card {
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.2s, border-color 0.2s;
}

.video-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-accent);
  text-decoration: none;
}

.video-card__thumb {
  position: relative;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: #e5e7eb;
}

.video-card__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-card__duration {
  position: absolute;
  bottom: 8px;
  left: 8px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: #fff;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 4px;
}

.video-card__body {
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  flex: 1;
}

.video-card__title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  line-height: 1.4;
  color: var(--color-text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.video-card__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.video-card__creator {
  font-weight: 500;
}

.video-card__comments {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.video-card__components {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: auto;
}

.component-badge {
  display: inline-block;
  padding: 2px 8px;
  font-size: 0.6875rem;
  font-weight: 500;
  color: var(--color-badge-text);
  background: var(--color-badge-bg);
  border-radius: 100px;
  white-space: nowrap;
}

.component-badge--more {
  color: var(--color-accent);
  background: var(--color-accent-light);
}
</style>
