<template>
  <div
    class="relative flex flex-col justify-between border-l border-indigo-600"
  >
    <div class="sticky top-0 z-50 flex flex-col bg-white">
      <h1 class="mx-auto mt-5 mb-10 font-cuprum text-4xl font-bold">
        DriftAnalysis
      </h1>
      <!--      <div class=" h-12 flex font-thin justify-between">-->
      <!--        <button class="w-1/2 bg-indigo-600">-->
      <!--          <div class="mx-auto text-white  font-semibold my-auto">New run</div></button>-->
      <!--        <button  class="w-1/2 ">Examine runs</button>-->
      <!--      </div>-->

      <div v-show="mode === 'overview'" class="flex flex-col space-y-10">
        <div class="flex bg-indigo-600 px-5 py-3">
          <div
            :class="[
              has_error('name')
                ? 'border-red-500 bg-red-400'
                : 'border-gray-300 bg-white',
              'relative mr-2 w-full rounded-md border border-indigo-600 px-3 py-2 shadow-sm ring-1 ring-indigo-600',
            ]"
          >
            <input
              v-model="name"
              type="text"
              :class="[
                has_error('name') ? 'bg-red-400' : 'bg-white',
                'block w-full appearance-none border-0 p-0 text-gray-900 placeholder-gray-500 outline-0 ring-0 sm:text-sm',
              ]"
            />
          </div>
          <button
            @click="mode = 'new'"
            class="rounded-md bg-white hover:bg-gray-100"
          >
            <PlusIcon class="h-5 w-10" />
          </button>
        </div>

        <div>
          <div v-for="run in stored_runs" class="flex justify-center">
            <button
              @click="$emit('run_selected', run.uuid)"
              :class="[
                run.uuid === this.run_id
                  ? 'bg-indigo-600 font-semibold text-white'
                  : 'hover:bg-indigo-50',
                'flex w-full justify-center py-1',
              ]"
            >
              <div class="">
                {{ run.uuid.slice(run.uuid.length - 5) }} - {{ run.name }}
              </div>
            </button>
          </div>
        </div>
      </div>

      <div v-show="mode === 'new'">
        <div class="sticky top-0 z-40 bg-indigo-600 px-5 py-3">
          <button
            @click="mode = 'overview'"
            class="flex font-semibold text-white"
          >
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
    </div>
  </div>
</template>

<script>
import { PlusIcon, ArrowLeftIcon } from "@heroicons/vue/outline";
import TargetFunction from "./ConfigModules/TargetFunction.vue";
import PotentialFunction from "./ConfigModules/PotentialFunction.vue";
import AlgorithmOptions from "./ConfigModules/AlgorithmOptions.vue";
import StateLocation from "./ConfigModules/StateLocation.vue";
import StateVariables from "./ConfigModules/StateVariables.vue";
import Validation from "../mixins";
import { useObservable } from "@vueuse/rxjs";
import { liveQuery } from "dexie";
import { db } from "../db.js";

export default {
  name: "Configuration",
  components: {
    TargetFunction,
    StateLocation,
    StateVariables,
    PotentialFunction,
    AlgorithmOptions,
    PlusIcon,
    ArrowLeftIcon,
  },
  props: ["run_id"],
  mixins: [Validation],
  emits: ["start_run", "target_changed", "run_selected"],
  data: function () {
    return {
      mode: "overview", // overview, new

      stored_runs: useObservable(liveQuery(() => db.runs.toArray())),

      name: "DriftAnalysisRun",
      algorithm: "",
      target_params: {
        A: 1,
        B: 0,
        C: 1,
      },
    };
  },
  created() {
    this.$emit("target_changed", this.target_params);
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