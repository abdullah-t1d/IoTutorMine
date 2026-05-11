<template>
  <main class="detail" v-if="video">
    <div class="container">
      <!-- Back Button -->
      <router-link to="/" class="detail__back">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        Back
      </router-link>

      <!-- Title -->
      <h1 class="detail__title">{{ video.title }}</h1>

      <!-- Video Info Card -->
      <div class="detail__card">
        <!-- Metadata Row -->
        <div class="detail__meta-row">
          <span class="detail__meta-item">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            {{ video.durationRange }} min
          </span>
          <span class="detail__meta-item">
            Created By: <strong>{{ video.creator }}</strong>
          </span>
          <span class="detail__meta-item">
            Published At: {{ video.publishDate }}
          </span>
        </div>

        <!-- Two Column Layout -->
        <div class="detail__content">
          <!-- Left: Video Player -->
          <div class="detail__player">
            <div class="detail__player-wrapper">
              <iframe
                :src="`https://www.youtube.com/embed/${video.youtubeId}`"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen
                title="Video player"
              ></iframe>
            </div>
          </div>

          <!-- Right: Info Panel -->
          <div class="detail__info">
            <div class="detail__info-section">
              <h3 class="detail__info-label">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                Search Query
              </h3>
              <p class="detail__info-value">{{ video.searchQuery }}</p>
            </div>

            <div class="detail__info-section">
              <h3 class="detail__info-label">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
                Tags
              </h3>
              <div class="detail__tags">
                <span v-for="tag in video.tags" :key="tag" class="detail__tag">{{ tag }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Electrical Components Card -->
      <div class="detail__card">
        <h2 class="detail__section-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>
          Electrical Components
        </h2>
        <div class="components-table-wrap">
          <table class="components-table">
            <thead>
              <tr>
                <th>Component</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="comp in video.components.filter(c => c.status === 'USED')" :key="comp.name">
                <tr>
                  <td>{{ comp.name }}</td>
                  <td><span class="status-badge status-badge--used">Used</span></td>
                </tr>
                <tr
                  v-for="alt in video.components.filter(c => c.status === 'ALTERNATIVE' && c.alternativeTo === comp.name)"
                  :key="alt.name"
                  class="alt-row"
                >
                  <td>
                    <span class="alt-branch">↳</span> {{ alt.name }}
                  </td>
                  <td><span class="status-badge status-badge--alt">Alternative</span></td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>


    </div>
  </main>

  <main v-else class="detail">
    <div class="container">
      <div class="detail__not-found">
        <h2>Video not found</h2>
        <p>The video you're looking for doesn't exist.</p>
        <router-link to="/" class="detail__back">← Back to Home</router-link>
      </div>
    </div>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { videos } from '../data/videos.js'

const route = useRoute()
const video = computed(() => videos.find(v => v.id === Number(route.params.id)))
</script>

<style scoped>
.detail {
  flex: 1;
  padding: var(--space-lg) 0 var(--space-2xl);
}

.detail__back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  text-decoration: none;
  padding: 6px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  margin-bottom: var(--space-md);
  transition: border-color 0.15s;
}

.detail__back:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  text-decoration: none;
}

.detail__title {
  font-size: var(--font-size-xl);
  font-weight: 700;
  margin-bottom: var(--space-lg);
  line-height: 1.3;
}

.detail__card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  margin-bottom: var(--space-lg);
}

.detail__meta-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-lg);
  padding-bottom: var(--space-lg);
  border-bottom: 1px solid var(--color-border-light);
  margin-bottom: var(--space-lg);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.detail__meta-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.detail__content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-xl);
}

.detail__player-wrapper {
  position: relative;
  padding-bottom: 56.25%;
  height: 0;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: #000;
}

.detail__player-wrapper iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.detail__info {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.detail__info-section {
  /* spacing handled by parent gap */
}

.detail__info-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-xs);
}

.detail__info-value {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
}

.detail__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.detail__tag {
  display: inline-block;
  padding: 4px 10px;
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: var(--color-badge-text);
  background: var(--color-badge-bg);
  border-radius: 100px;
  border: 1px solid var(--color-border);
}

.detail__hashtags {
  font-size: var(--font-size-sm);
  color: var(--color-accent);
  font-weight: 500;
}

.detail__description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.7;
}

/* --- Components Table --- */
.detail__section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--font-size-lg);
  font-weight: 600;
  margin-bottom: var(--space-lg);
}

.components-table-wrap {
  overflow-x: auto;
}

.components-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-sm);
}

.components-table th {
  text-align: left;
  padding: 10px 16px;
  font-weight: 600;
  font-size: var(--font-size-xs);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
  border-bottom: 2px solid var(--color-border);
}

.components-table td {
  padding: 10px 16px;
  border-bottom: 1px solid var(--color-border-light);
  color: var(--color-text-primary);
}

.components-table tr:last-child td {
  border-bottom: none;
}

.status-badge {
  display: inline-block;
  padding: 2px 10px;
  font-size: var(--font-size-xs);
  font-weight: 500;
  border-radius: 100px;
}

.status-badge--used {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge--alt {
  background: #fff3e0;
  color: #e65100;
}

.alt-row td {
  background: var(--color-surface-hover, #f9fafb);
}

.alt-branch {
  color: var(--color-text-muted);
  margin-right: 4px;
  font-weight: 600;
}

/* --- Ask Section --- */
.detail__model-selector {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
}

.detail__model-selector select {
  padding: 5px 10px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.detail__notice {
  padding: 12px 16px;
  font-size: var(--font-size-sm);
  color: var(--color-warning-text);
  background: var(--color-warning-bg);
  border: 1px solid var(--color-warning-border);
  border-radius: var(--radius-sm);
  margin-bottom: var(--space-lg);
}

.detail__ask-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.detail__form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.detail__form-label {
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.detail__textarea {
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  resize: vertical;
  min-height: 100px;
  outline: none;
  transition: border-color 0.15s;
}

.detail__textarea:focus {
  border-color: var(--color-accent);
}

.detail__input {
  padding: 10px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  outline: none;
  transition: border-color 0.15s;
}

.detail__input:focus {
  border-color: var(--color-accent);
}

.detail__form-row {
  display: flex;
  align-items: flex-end;
  gap: var(--space-md);
}

.detail__form-group--name {
  flex: 0 0 250px;
}

.detail__submit-btn {
  margin-left: auto;
  padding: 10px 24px;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: #fff;
  background: var(--color-accent);
  border: none;
  border-radius: var(--radius-sm);
  opacity: 0.5;
  cursor: not-allowed;
}

.detail__not-found {
  text-align: center;
  padding: var(--space-2xl);
}

/* Responsive */
@media (max-width: 768px) {
  .detail__content {
    grid-template-columns: 1fr;
  }

  .detail__form-row {
    flex-direction: column;
    align-items: stretch;
  }

  .detail__form-group--name {
    flex: 1;
  }

  .detail__submit-btn {
    margin-left: 0;
  }

  .detail__meta-row {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-sm);
  }
}
</style>
