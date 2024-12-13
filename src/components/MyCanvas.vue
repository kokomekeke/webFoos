<template>
    <div class="canvas-container">
      <canvas
        ref="canvas"
        @mousedown="startDrawing"
        @mouseup="stopDrawing"
        @mouseleave="stopDrawing">
        Your browser doesn't support canvas
      </canvas>
    </div>
  </template>
  
  <script>
  export default {
    name: "MyCanvas",
    props: {
      backgroundFile: { type: String, required: true }, // Videó fájl elérési útvonala
    },
    data() {
      return {
        path: null,
        width: 0,
        height: 0,
        video: null,
        isDrawing: false,
        ctx: null,
        startPoint: null,
        lastPoint: null,
        lineCount: 0,
        maxLines: 4,
        squareCoordinates: []
      };
    },
    mounted() {
      this.video = document.createElement("video"); // Létrehozzuk a videó elemet
      this.video.src = this.backgroundFile;
      this.path = this.backgroundFile

      this.video.addEventListener("loadeddata", () => {
        // A videó betöltése után beállítjuk a vászon méreteit
        this.width = this.video.videoWidth;
        this.height = this.video.videoHeight;
        console.log(this.width)
        console.log(this.height)

        const canvas = this.$refs.canvas;
        canvas.width = this.width;
        canvas.height = this.height;

        this.ctx = canvas.getContext("2d");
        this.ctx.strokeStyle = 'red';

        // Az első frame kirajzolása
        this.ctx.drawImage(this.video, 0, 0, this.width, this.height);
      });

        // Ha automatikusan szeretnéd lejátszani a videót a frame betöltéséhez
        this.video.crossOrigin = "anonymous"; // Ha szükséges, kezeljük a CORS-t
        this.video.muted = true; // Nincs szükség hangra
        this.video.play();
    },
    methods: {
      loadVideoFrame() {
        this.video.crossOrigin = "anonymous"; // Ha szükséges, kezeljük a CORS-t
        this.video.muted = true; // Nincs szükség hangra
        this.video.play();
  
        this.video.addEventListener("loadeddata", () => {
          this.video.pause(); // Az első frame kirajzolása előtt megállítjuk a videót
          this.ctx.drawImage(this.video, 0, 0, this.$refs.video.width, this.$refs.video.height);
        });
      },
      startDrawing(event) {
        // Ellenőrizzük, hogy a maximális vonalak száma elért-e
        if (this.lineCount >= this.maxLines) {
          return; // További rajzolás tiltva
        }
  
        this.isDrawing = true;
        const rect = this.$refs.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        

        // Ha ez az első pont, akkor kezdjük itt
        if (!this.startPoint) {
            this.startPoint = { x, y }; // Mentjük az első pontot
          
            this.ctx.fillStyle = "blue"; // A kör színe
            const radius = 5; // A kör sugara
            this.ctx.arc(x, y, radius, 0, Math.PI * 2); // Kör rajzolása
            this.ctx.fill();
            //this.squareCoordinates.push({ x, y });
        }
          
        
  
        // Az előző pontból indulunk
        if (!this.lastPoint) {
          this.lastPoint = { x, y };
        }
  
        this.ctx.beginPath();
        this.ctx.moveTo(this.lastPoint.x, this.lastPoint.y);
      },
      stopDrawing(event) {
        if (this.isDrawing) {
            this.isDrawing = false;
            const rect = this.$refs.canvas.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            
          
            this.ctx.fillStyle = "blue"; // A kör színe
            const radius = 5; // A kör sugara
            this.ctx.arc(x, y, radius, 0, Math.PI * 2); // Kör rajzolása
            this.ctx.fill();
      

            // Rajzoljunk egy egyenest az aktuális pontig
            this.ctx.lineTo(x, y);
            this.ctx.stroke();
              
            
            this.squareCoordinates.push({ x, y });

            // Frissítsük az utolsó pontot
            this.lastPoint = { x, y };
            this.lineCount += 1;
            
          // Ellenőrizzük, hogy kész-e a négyszög
          if (this.lineCount === this.maxLines) {
            // Az aktuális pontból húzzunk vonalat az első ponthoz
            this.ctx.lineTo(this.startPoint.x, this.startPoint.y);
            this.ctx.stroke();
            this.ctx.closePath();
  
            // Tiltjuk a további rajzolást
            this.isDrawing = false;
            this.lastPoint = null;

            console.log(this.squareCoordinates)
            this.sendSquareCoordinatesToBackend();


          }
          //this.squareCoordinates.push({ x, y });
        }
      },
      sendSquareCoordinatesToBackend() {
        // Küldjük el a koordinátákat a backendnek
        fetch("http://localhost:5000/perspective", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            coordinates: this.squareCoordinates, // A négyzet koordinátái
          }),
        })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Hiba történt az adatok küldése során.");
          }
          return response.json();
        })
        .then((data) => {
          console.log("Backend válasz:", data);
          console.log("backgrounfile: ", this.backgroundFile)
          this.$router.push({
          path: '/analyzer',
          query: { videoUrl: this.backgroundFile }, // A videó URL-t átadjuk az elemzőnek
        });
        })
        .catch((error) => {
          console.error("Hiba:", error);
        });
      },
    },
  };
  </script>
  
  <style scoped>
  .canvas-container {
    position: relative;
    width: 100%;
    height: 100%;
    border: 2px  red;
  }
  
  canvas {
    display: block;
    position: absolute;
    top: 0;
    left: 0;
    cursor: crosshair;
    border: 2px  greenyellow;
  }
  </style>
  