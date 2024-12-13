<template>
  <div>
    <h1>Upload Video</h1>
    <input type="file" @change="onFileChange" />
    <button @click="uploadVideo">Upload</button>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      selectedFile: null,
      message: '',
    };
  },
  methods: {
    onFileChange(event) {
      this.selectedFile = event.target.files[0];
    },
    async uploadVideo() {
      if (!this.selectedFile) {
        this.message = 'Please select a file first!';
        return;
      }

      const formData = new FormData();
      formData.append('file', this.selectedFile);

      try {
        const response = await axios.post('http://127.0.0.1:5000/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });

        const videoUrl = response.data.file_url;
        console.log(videoUrl)
        this.message = 'Upload successful!';
        this.$emit('videoUploaded', videoUrl); // Esemény a szülő számára (ha szükséges)

        // Navigáció a videóelemző oldalra
        this.$router.push({
          path: '/keypoints',
          query: { videoUrl }, // A videó URL-t átadjuk az elemzőnek
        });
      } catch (error) {
        this.message = `Error: ${error.response?.data?.error || 'Unknown error'}`;
      }
    },
  },
};
</script>

<style>
/* Adj egy kis stílust */
</style>
