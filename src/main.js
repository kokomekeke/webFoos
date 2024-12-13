import { createApp } from 'vue'
import {createWebHistory, createRouter} from 'vue-router'

import App from './App.vue'
import FileUploader from './components/FileUploader.vue'
import FoosballAnalyzer from './components/FoosballAnalyzer.vue'
import KeyPoints from './components/KeyPoints.vue'
import VideoAnalyzer from "@/components/VideoAnalyzer.vue";

const routes = [
    {path: '/', redirect: '/upload'},
    {path: '/upload', component: FileUploader},
    {path: '/keypoints', component: KeyPoints},
    {path: '/analyzer', component: FoosballAnalyzer},
    {path: '/analyzed', component: VideoAnalyzer}
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')

export default router;


