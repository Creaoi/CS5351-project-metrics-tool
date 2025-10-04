<template>
  <canvas ref="canvas" class="star-canvas"></canvas>
</template>

<script setup>
import { onMounted, ref } from "vue";

const canvas = ref(null);

onMounted(() => {
  const ctx = canvas.value.getContext("2d");
  const stars = [];

  const resize = () => {
    canvas.value.width = window.innerWidth;
    canvas.value.height = window.innerHeight;
  };
  resize();
  window.addEventListener("resize", resize);

  for (let i = 0; i < 150; i++) {
    stars.push({
      x: Math.random() * canvas.value.width,
      y: Math.random() * canvas.value.height,
      radius: Math.random() * 1.5,
      dx: (Math.random() - 0.5) * 0.3,
      dy: (Math.random() - 0.5) * 0.3,
    });
  }

  function draw() {
    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, canvas.value.width, canvas.value.height);

    ctx.fillStyle = "white";
    stars.forEach((star) => {
      star.x += star.dx;
      star.y += star.dy;

      if (star.x < 0 || star.x > canvas.value.width) star.dx *= -1;
      if (star.y < 0 || star.y > canvas.value.height) star.dy *= -1;

      ctx.beginPath();
      ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
      ctx.fill();
    });

    requestAnimationFrame(draw);
  }
  draw();
});
</script>

<style scoped>
.star-canvas {
  position: fixed;   /* 👈 永远固定在屏幕 */
  top: 0;
  left: 0;
  width: 100vw;      /* 全屏宽度 */
  height: 100vh;     /* 全屏高度 */
  z-index: -1;       /* 在最底层 */
}
</style>
