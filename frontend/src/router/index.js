import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import VideoDetailPage from '../views/VideoDetailPage.vue'


const routes = [
  { path: '/', name: 'Home', component: HomePage },
  { path: '/video/:id', name: 'VideoDetail', component: VideoDetailPage, props: true },

]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router
