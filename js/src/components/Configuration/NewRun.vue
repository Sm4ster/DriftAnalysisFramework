<template>
  <div>
    <div class="sticky top-0 z-40 bg-indigo-600 px-5 py-3">
      <button @click="$emit('overview')" class="flex font-semibold text-white">
        <ArrowLeftIcon class="my-auto mr-1 h-4 w-4" />
        <span>Overview</span>
      </button>
    </div>

    <div class="space-y-10 px-5 py-10">
      <TargetFunction
        ref="target"
        :init_params="target_params"
        @param_update="$emit('target_changed', $event)"
      ></TargetFunction>
      <StateLocation ref="location" :algorithm="algorithm" />
      <PotentialFunction ref="potential" />

      <AlgorithmOptions ref="algorithm" @selected="algorithm = $event" />
      <StateVariables ref="variables" :algorithm="algorithm" />
    </div>

    <div class="sticky bottom-0 flex flex-col">
      <button
        class="bg-indigo-600 pt-2.5 pb-2.5 font-semibold text-white hover:bg-indigo-500"
        @click="start_run"
      >
        Start run
      </button>
    </div>
  </div>
</template>

<script>
import { ArrowLeftIcon } from "@heroicons/vue/24/solid/index.js";
import TargetFunction from "./modules/TargetFunction.vue";
import StateLocation from "./modules/StateLocation.vue";
import StateVariables from "./modules/StateVariables.vue";
import PotentialFunction from "./modules/PotentialFunction.vue";
import AlgorithmOptions from "./modules/AlgorithmOptions.vue";

export default {
  name: "NewRun",
  components: {
    ArrowLeftIcon,
    TargetFunction,
    StateLocation,
    StateVariables,
    PotentialFunction,
    AlgorithmOptions,
  },
  emits: ["target_changed", "overview"],
  data: () => {
    return {
      algorithm: "",
      target_params: {
        A: 1,
        B: 0,
        C: 1,
      },
    };
  },
  methods: {
    start_run() {
      try {
        const algorithm = this.$refs.algorithm.export();
        this.$emit("start_run", {
          name: this.name,
          algorithm: algorithm.selected,
          target: this.$refs.target.export(),
          potential: this.$refs.potential.export(),
          constants: algorithm.options,
          location: this.$refs.location.export(),
          variables: this.$refs.variables.export(),
        });
      } catch (e) {
        alert("cannot start because of " + e);
      } finally {
        this.mode = "overview";
      }
    },
  },
};
</script>

<style scoped></style>
