<template>
    <VideoPlayer
        class="videoplayer"
        :path="videoUrl"
        :muted="false"
        :autoplay="false"
        :controls="true"
        :loop="false"
        @play="onPlayerPlay"
        @pause="onPlayerPause"
        @ended="onPlayerEnded"
        @loadeddata="onPlayerLoadeddata"
        @waiting="onPlayerWaiting"
        @playing="onPlayerPlaying"
        @timeupdate="onPlayerTimeupdate"
        @canplay="onPlayerCanplay"
        @canplaythrough="onPlayerCanplaythrough"
        @statechanged="playerStateChanged"
    >
        <template
            v-slot:controls="{
            togglePlay,
            playing,
            percentagePlayed,
            seekToPercentage,
            duration,
            convertTimeToDuration,
            videoMuted,
            toggleMute,
        }"
        >
            <div class="videoplayer-controls">
                <button @click="togglePlay()" class="videoplayer-controls-toggleplay">
                    {{ playing ? "pause" : "play" }}
                </button>
                <div class="videoplayer-controls-time">
                    {{ convertTimeToDuration(time) }} / {{ convertTimeToDuration(duration) }}
                </div>
                <videoplayer-track
                    :percentage="percentagePlayed"
                    @seek="seekToPercentage"
                    class="videoplayer-controls-track"
                />
                <button @click="toggleMute()" class="videoplayer-controls-togglemute">
                    {{ videoMuted ? "unmute" : "mute" }}
                </button>
                <button v-if="progress >= 100" class="download-processed-button">
                    Process Finished
                </button>
            </div>
        </template>
    </VideoPlayer>
    <div class="progress-container">
        <div class="progress-bar" :style="{ width: progress + '%' }"></div>
    </div>
</template>


  
<script>
import VideoPlayer from './VideoPlayer.vue';

export default {
    components: {
        VideoPlayer,
    },
    data() {
        return {
            videoUrl: null,
            time: 0,
            progress: 0,
        };
    },
    created() {
        this.videoUrl = this.$route.query.videoUrl ? `http://127.0.0.1:5000/videos/${this.$route.query.videoUrl}` : null;
        console.log("url:::", this.videoUrl);
        this.startProgressStream();
        console.log("started processing stream");
    },
    methods: {
        startProgressStream() {
            const eventSource = new EventSource('http://localhost:5000/stream');
            eventSource.onmessage = (event) => {
                this.progress = parseInt(event.data);
                if (this.progress >= 100) {
                    this.videoUrl = 'processed.mp4'
                    eventSource.close();
                }
            };
        },
        onPlayerPlay({ event, player }) {
            console.log(event.type);
            player.setPlaying(true);
        },
        onPlayerPause({ event, player }) {
            console.log(event.type);
            player.setPlaying(false);
        },
        onPlayerEnded({ event, player }) {
            console.log(event.type);
            player.setPlaying(false);
        },
        onPlayerLoadeddata({ event }) {
            console.log(event.type);
        },
        onPlayerWaiting({ event }) {
            console.log(event.type);
        },
        onPlayerPlaying({ event }) {
            console.log(event.type);
        },
        onPlayerTimeupdate({ event }) {
            this.time = event.target.currentTime;
            console.log({ event: event.type, time: event.target.currentTime });
        },
        onPlayerCanplay({ event }) {
            console.log(event.type);
        },
        onPlayerCanplaythrough({ event }) {
            console.log(event.type);
        },
        playerStateChanged({ event }) {
            console.log(event.type);
        },
    },
};
</script>


<style>
.progress-container {
    width: 100%;
    height: 10px;
    background-color: #e0e0e0;
    border-radius: 5px;
    overflow: hidden;
    margin-top: 20px;
}

.progress-bar {
    height: 100%;
    background-color: #76c7c0;
    width: 0;
    transition: width 0.1s ease;
}

.play-processed-button {
    margin-top: 20px;
    padding: 10px 20px;
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

.play-processed-button:hover {
    background-color: #45a049;
}
</style>
