<template>
  <div class="canvas-wrapper"></div>
</template>

<script>
import { createCanvas } from "vb-canvas";

export default {
  props: ["viewbox", "draw"],
  emits: ["has_drawn"],
  data: () => {
    return {
      ctx: null,
      canvas: null,
    };
  },
  mounted() {
    let { ctx, el } = createCanvas({
      // viewBox (x, y, width, height)
      viewBox: [0, 0, this.viewbox.width, this.viewbox.height], // this.viewbox.x, this.viewbox.y, this.viewbox.width, this.viewbox.height]
      target: ".canvas-wrapper",
      scaleMode: "fill",
      autoAspectRatio: false,
    });

    this.ctx = ctx;
    this.canvas = el;
    this.ctx.clearRect(
      -this.canvas.width,
      -this.canvas.height,
      2 * this.canvas.width,
      2 * this.canvas.height
    );
    this.transformContextMatrix(
      this.ctx,
      this.viewbox,
      window.devicePixelRatio,
      "fill"
    );
  },

  watch: {
    data() {
      this.ctx.clearRect(
        -this.canvas.width,
        -this.canvas.height,
        2 * this.canvas.width,
        2 * this.canvas.height
      );
      this.draw_data();
      this.$emit("has_drawn");
    },
    viewbox(viewbox) {
      this.transformContextMatrix(
        this.ctx,
        viewbox,
        window.devicePixelRatio,
        "fill"
      );
      this.ctx.clearRect(
        -this.canvas.width,
        -this.canvas.height,
        2 * this.canvas.width,
        2 * this.canvas.height
      );
      this.draw_data();
    },

    draw(el) {
      if (el) {
        this.ctx.clearRect(
          -this.canvas.width,
          -this.canvas.height,
          2 * this.canvas.width,
          2 * this.canvas.height
        );
        this.draw_data();
        this.$emit("has_drawn");
      }
    },
  },

  computed: {
    data(){
      console.log("something happenning here?")
      return this.$store.state.locations
    }
  },
  methods: {
    draw_data() {
      this.data.forEach(
        function (el) {
          this.draw_circle(el.location[0], el.location[1], el.color);
        }.bind(this)
      );
    },

    draw_circle(x, y, color) {
      this.ctx.fillStyle = color;
      this.ctx.beginPath();
      this.ctx.arc(x, y, 1, 0, 2 * Math.PI, true);
      this.ctx.fill();
    },

    transformContextMatrix(ctx, viewBox, resolution, scaleMode) {
      const viewBoxWidth = viewBox.width;
      const viewBoxHeight = viewBox.height;

      let { width: canvasWidth, height: canvasHeight } =
        ctx.canvas.getBoundingClientRect();

      canvasWidth *= resolution;
      canvasHeight *= resolution;

      const { fitWidth, fitHeight, ratio } = this.calculateAspectRatio(
        viewBoxWidth,
        viewBoxHeight,
        canvasWidth,
        canvasHeight,
        scaleMode
      );

      const scaleX = fitWidth / viewBoxWidth;
      const scaleY = fitHeight / viewBoxHeight;

      const translateX = -viewBox.x * ratio + (canvasWidth - fitWidth) / 2;
      const translateY = -viewBox.y * ratio + (canvasHeight - fitHeight) / 2;

      this.ctx.setTransform(scaleX, 0, 0, scaleY, translateX, translateY);

      // this.clipCtx(ctx, viewBoxWidth, viewBoxHeight);
    },
    calculateAspectRatio(srcWidth, srcHeight, maxWidth, maxHeight, scaleMode) {
      let ratio;

      if (scaleMode === "fit") {
        ratio = Math.min(maxWidth / srcWidth, maxHeight / srcHeight);
      } else {
        ratio = Math.max(maxWidth / srcWidth, maxHeight / srcHeight);
      }

      return {
        fitWidth: srcWidth * ratio,
        fitHeight: srcHeight * ratio,
        ratio: ratio,
      };
    },
    clipCtx(ctx, viewBoxWidth, viewBoxHeight) {
      ctx.beginPath(viewBoxWidth, viewBoxHeight);
      ctx.rect(0, 0, viewBoxWidth, viewBoxHeight);
      ctx.clip();
      ctx.closePath();
    },
  },
};
</script>

<style>
.vb-canvas {
  width: 100vw;
  height: 100vh;
}
</style>