<template>
  <div ref="dataoptions">
    <div class="w-96 overflow-hidden rounded bg-white">
      <div
        ref="drag_surface"
        class="w-full cursor-move bg-indigo-600 px-2 py-1 text-sm font-medium text-white"
      >
        Data Display Options
      </div>
      <div class="block border border-y-0 border-indigo-600">
        <div class="border-b border-gray-200">
          <nav class="-mb-px flex" aria-label="Tabs">
            <!-- Current: "border-indigo-500 text-indigo-600", Default: "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300" -->
            <div
              @click="selected_menu = 'run_selection'"
              :class="[
                selected_menu === 'run_selection'
                  ? 'border-indigo-500 text-indigo-600'
                  : '',
                'flex-grow cursor-pointer border-b-2 border-transparent py-2 px-1 text-center text-sm font-medium text-gray-500 hover:border-gray-300 hover:text-gray-700',
              ]"
            >
              Runs
            </div>

            <div
              @click="selected_menu = 'data_filters'"
              :class="[
                selected_menu === 'data_filters'
                  ? 'border-indigo-500 text-indigo-600'
                  : '',
                'flex-grow cursor-pointer border-b-2 border-transparent py-2 px-1 text-center text-sm font-medium text-gray-500 hover:border-gray-300 hover:text-gray-700',
              ]"
            >
              Data Filters
            </div>
          </nav>
        </div>
      </div>

      <div
        class="flex overflow-hidden rounded-b border border-t-0 border-indigo-600 py-5"
      >
        <div
          v-if="selected_menu === 'run_selection'"
          class="flex w-96 flex-col"
        ></div>
        <div
          v-if="selected_menu === 'data_filters'"
          class="flex h-20 w-96 justify-center px-5"
        >
          <div class="w-full">
            <div class="">
              <label
                for="default-range"
                class="mb-2 flex justify-between text-sm font-medium text-gray-900 dark:text-gray-300"
              >
                <span class="">Minimum drift</span>
                <span class="">{{ min_drift }}</span>
              </label>
              <Slider v-model="min_drift" />
              <input
                type="range"
                :min="drift_range.min"
                :max="drift_range.max"
                v-model="min_drift"
                :step="stepSize"
                class="h-2 w-full cursor-pointer appearance-none rounded-lg bg-gray-200 accent-indigo-600 dark:bg-gray-700"
              />
              <div class="flex flex-col">
                <div>{{ drift_range.min }}</div>
                <div>{{ drift_range.max }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useObservable } from "@vueuse/rxjs/index";
import { liveQuery } from "dexie";
import { db } from "../../db";
import Slider from "@vueform/slider";

export default {
  name: "DataOptions",
  components: {
    Slider,
  },
  props: ["run_id", "runs", "drift_range"],
  emits: ["run_selected", "min_drift"],
  data: function () {
    return {
      min_drift: null,
      selected_menu: "run_selection",
      stored_runs: useObservable(liveQuery(() => db.runs.toArray())),
    };
  },
  created() {},
  mounted() {
    this.dragElement(this.$refs.dataoptions, this.$refs.drag_surface);
  },

  watch: {
    drift_range() {
      console.log(this.drift_range);
      this.min_drift = this.drift_range.min;
    },
    min_drift() {
      this.$emit("min_drift");
    },
  },
  computed: {
    stepSize() {
      return Math.pow(10, this.getNumberParts(this.drift_range.min).exponent);
    },
  },
  methods: {
    getNumberParts(x) {
      var float = new Float64Array(1),
        bytes = new Uint8Array(float.buffer);

      float[0] = x;

      var sign = bytes[7] >> 7,
        exponent = (((bytes[7] & 0x7f) << 4) | (bytes[6] >> 4)) - 0x3ff;

      bytes[7] = 0x3f;
      bytes[6] |= 0xf0;

      return {
        sign: sign,
        exponent: exponent,
        mantissa: float[0],
      };
    },
    show_locations(uuid) {
      this.$emit("run_selected", uuid);
    },

    dragElement(elmnt, drag_surface) {
      var pos1 = 0,
        pos2 = 0,
        pos3 = 0,
        pos4 = 0;
      drag_surface.onmousedown = dragMouseDown;

      function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        // get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // call a function whenever the cursor moves:
        document.onmousemove = elementDrag;
      }

      function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        // calculate the new cursor position:
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // set the element's new position:
        elmnt.style.top = elmnt.offsetTop - pos2 + "px";
        elmnt.style.left = elmnt.offsetLeft - pos1 + "px";
      }

      function closeDragElement() {
        /* stop moving when mouse button is released:*/
        document.onmouseup = null;
        document.onmousemove = null;
      }
    },
  },
};
</script>