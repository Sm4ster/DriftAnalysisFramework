<template>
  <div class="my-auto">
    <div class="my-auto flex justify-between space-x-2 text-center">
      <div class="my-auto flex">
        <span class="font-mono text-xs">
          <slot name="code"></slot>
        </span>
      </div>
    </div>

    <div class="flex justify-between">
      <div class="text-lg">
        <slot name="title"></slot>
      </div>

      <div class="flex space-x-3">
        <div
          :class="[
            'relative w-20 rounded-md border px-3 py-2 shadow-sm focus-within:border-indigo-600 focus-within:ring-1 focus-within:ring-indigo-600',
          ]"
        >
          <label
            class="absolute -top-2 left-2 -mt-px inline-block rounded bg-white px-1 text-xs font-medium text-gray-900"
          >
            <span> min </span>
          </label>
          <label
            class="absolute -bottom-2 left-2 -mt-px inline-block rounded bg-white px-1 text-xs font-light text-gray-600"
          >
            <span> {{ extreme_values.min }} </span>
          </label>
          <input
            v-model="variable.field_1"
            type="number"
            :class="[
              'block w-full appearance-none border-0 p-0 text-gray-900 placeholder-gray-500 focus:outline-0 focus:ring-0 sm:text-sm',
            ]"
          />
        </div>
        <div
          :class="[
            'relative w-20 rounded-md border px-3 py-2 shadow-sm focus-within:border-indigo-600 focus-within:ring-1 focus-within:ring-indigo-600',
          ]"
        >
          <label
            class="absolute -top-2 left-2 -mt-px inline-block rounded bg-white px-1 text-xs font-medium text-gray-900"
          >
            <span> max </span>
          </label>
          <label
            class="absolute -bottom-2 right-2 -mt-px inline-block rounded bg-white px-1 text-xs font-light text-gray-600"
          >
            <span> {{ extreme_values.max }} </span>
          </label>
          <input
            v-model="variable.field_2"
            type="number"
            :class="[
              'block w-full appearance-none border-0 p-0 text-gray-900 placeholder-gray-500 focus:outline-0 focus:ring-0 sm:text-sm',
            ]"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import StateVariableOptions from "./StateVariableOptions.vue";
import { Switch } from "@headlessui/vue";

export default {
  name: "SingleFilterVariable",
  components: {
    StateVariableOptions,
    Switch,
  },
  emits: ["filter"],
  props: ["extreme_values"],
  data() {
    return {
      variation_enabled: true,

      variable: {
        field_1: 0,
        field_2: 10,
      },
    };
  },
  created() {
    this.initialize();
  },
  mounted() {
    MathJax.typeset();
  },
  updated() {
    MathJax.typeset();
  },
  watch: {
    variable: {
      handler: function () {
        this.$emit("filter", {
          min: this.variable.field_1,
          max: this.variable.field_2,
        });
      },
      deep: true,
    },
  },
  methods: {
    initialize() {
      this.variable.field_1 = this.extreme_values.min;
      this.variable.field_2 = this.extreme_values.max;
    },
  },
};
</script>

<style scoped></style>