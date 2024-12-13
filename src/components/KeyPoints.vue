<template>
    <div>
      <MyCanvas :backgroundFile="videoUrl" />
    </div>
  </template>
  
  <script>
  import MyCanvas from "./MyCanvas.vue";
  
  export default {
    name: "KeyPoints",
    components: {
      MyCanvas,
    },
    data() {
      return {
        videoUrl: null,
      };
    },
    created() {
      // Videó URL lekérése a route query paramétereiből
      this.videoUrl = this.$route.query.videoUrl || "default-background.jpg";
    },
  };
  </script>