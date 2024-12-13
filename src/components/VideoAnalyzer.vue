<template>
    <video
        v-if="videoUrl"
        :src="videoUrl"
        autoplay
        loop
        muted
        playsinline
        class="video-player"
    ></video>
    <p v-else>Nincs videó</p>
</template>

<script>
export default {
    name: 'VideoAnalyzer',
    data() {
        return {
            videoUrl: null,
        };
    },
    mounted() {
        const fileName = this.$route.query.videoUrl;
        console.log("filename::: ", fileName)
        this.videoUrl = `http://localhost:5000/videos/${fileName}`;
        console.log("url:::", this.videoUrl);
    },
};
</script>