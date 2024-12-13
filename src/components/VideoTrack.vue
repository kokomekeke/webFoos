<template>
    <div class="video-track">
      <input
        type="range"
        min="0"
        max="100"
        step="1"
        :value="percentage.toFixed(1)"
        @input="onInput"
      />
    </div>
  </template>
  
  <script>
  export default {
    name: "VideoTrack",
    props: {
      percentage: { type: Number, required: true },
    },
    methods: {
      onInput(e) {
        this.$emit("seek", e.target.value);
      },
    },
  };
  </script>
  
  <style>
  input[type="range"] {
    position: relative;
    top: -1px;
    overflow: hidden;
    width: 245px;
    -webkit-appearance: none;
    background-color: #ccc;
    border-radius: 5px;
  }
  
  input[type="range"]:focus {
    outline: none;
  }
  
  input[type="range"]::-webkit-slider-runnable-track {
    height: 8px;
    -webkit-appearance: none;
    color: #333;
    margin-top: -1px;
  }
  
  input[type="range"]::-webkit-slider-thumb {
    width: 8px;
    -webkit-appearance: none;
    height: 8px;
    cursor: ew-resize;
    background: #333;
    box-shadow: -245px 0 0 245px #333;
  }
  </style>