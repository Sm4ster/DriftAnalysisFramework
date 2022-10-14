<template>
  <div ref="eventlayer" class="h-full w-full"></div>
</template>

<script>
import * as d3 from "d3";

export default {
  name: "EventLayer",
  props: ["svg"],
  emits: ["viewbox"],
  data: function () {
    return {
      base_zoom: 250,
      zoom_scale: d3.scalePow([0.01, 1], [1 / 100, 10]),

      viewbox_params: {
        x_bias: -240,
        y_bias: -240,
        zoom_factor: 0.2,
      },

      isPointerDown: null,
      has_zoomed: null,
      point: null,

      x_ratio: null,
      y_ratio: null,

      drag_x: 0,
      drag_y: 0,
    }
  },
  mounted() {
    let event_layer = this.$refs["eventlayer"]
    event_layer.addEventListener('wheel', this.zoom_wheel, {passive: false});
    event_layer.addEventListener('mousemove', this.drag);
    event_layer.addEventListener('mousedown', this.start_move);
    event_layer.addEventListener('mouseup', this.stop_move);
    event_layer.addEventListener('mouseleave', this.stop_move);

    this.x_ratio = parseInt(this.base_zoom) * this.zoom_scale(this.viewbox_params.zoom_factor) / event_layer.getBoundingClientRect().width;
    this.y_ratio = parseInt(this.base_zoom) * this.zoom_scale(this.viewbox_params.zoom_factor) / event_layer.getBoundingClientRect().height;

    window.addEventListener('resize', function () {
      this.x_ratio = parseInt(this.base_zoom) * this.zoom_scale(this.viewbox_params.zoom_factor) / event_layer.getBoundingClientRect().width;
      this.y_ratio = parseInt(this.base_zoom) * this.zoom_scale(this.viewbox_params.zoom_factor) / event_layer.getBoundingClientRect().height;
    }.bind(this));


    // init the viewbox
    this.$emit("viewbox",
        {
          x: this.viewbox_params.x_bias,
          y: this.viewbox_params.y_bias,
          width: parseInt(this.base_zoom) * this.zoom_scale(this.viewbox_params.zoom_factor),
          height: parseInt(this.base_zoom) * this.zoom_scale(this.viewbox_params.zoom_factor),
        }
    )

  },
  watch: {
    viewbox_params: {
      handler: function () {
        this.$emit("viewbox",
            {
              x: this.viewbox_params.x_bias,
              y: this.viewbox_params.y_bias,
              width: parseInt(this.base_zoom) * this.zoom_scale(this.viewbox_params.zoom_factor),
              height: parseInt(this.base_zoom) * this.zoom_scale(this.viewbox_params.zoom_factor),
            }
        )
      },
      deep: true
    }
  },
  methods: {
    zoom_wheel(event) {
      event.preventDefault();
      this.viewbox_params.zoom_factor += event.deltaY > 0 ? 0.01 : -0.01;
    },

    getPointFromEvent(event) {
      let point = this.svg.createSVGPoint();
      point.x = event.clientX;
      point.y = event.clientY;

      // We get the current transformation matrix of the SVG and we inverse it
      var invertedSVGMatrix = this.svg.getScreenCTM().inverse();

      return point.matrixTransform(invertedSVGMatrix);
    },

    start_move(event) {
      this.isPointerDown = true; // We set the pointer as down

      // We get the pointer position on click/touchdown, so we can get the value once the user starts to drag
      this.pointerOrigin = this.getPointFromEvent(event);
    },

    stop_move(event) {
      // The pointer is no longer considered as down
      this.isPointerDown = false;
    },

    drag(event) {
      // Only run this function if the pointer is down
      if (!this.isPointerDown) {
        return;
      }
      // This prevent user to do a selection on the page
      event.preventDefault();

      // Get the pointer position
      var pointerPosition = this.getPointFromEvent(event);

      // We calculate the distance between the pointer origin and the current position
      // The viewBox x & y values must be calculated from the original values and the distances

      this.drag_x += (pointerPosition.x - this.pointerOrigin.x);
      this.drag_y += (pointerPosition.y - this.pointerOrigin.y);

      this.viewbox_params.x_bias = this.viewbox_params.x_bias - (pointerPosition.x - this.pointerOrigin.x) * this.x_ratio;
      this.viewbox_params.y_bias = this.viewbox_params.y_bias - (pointerPosition.y - this.pointerOrigin.y) * this.y_ratio;


    },


  },

}
</script>

