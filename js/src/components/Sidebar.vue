<template>
  <div
    class="relative flex flex-col justify-between border-l border-indigo-600"
  >
    <div class="sticky top-0 z-50 flex flex-col bg-white">
      <h1 class="mx-auto mt-5 mb-10 font-cuprum text-4xl font-bold">
        DriftAnalysis
      </h1>

      <div v-show="mode === 'overview'" class="flex bg-indigo-600 px-5 py-3">
        <div
          :class="[
            has_error('name')
              ? 'border-red-500 bg-red-400'
              : 'border-gray-300 bg-white',
            'relative mr-2 w-full rounded-md border border-indigo-600 px-3 py-2 shadow-sm ring-1 ring-indigo-600',
          ]"
        >
          <input
            v-show="mode === 'overview'"
            v-model="new_name"
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

      <SelectRun
        v-show="mode === 'overview'"
        :run_id="run_id"
        @run_selected="
          $emit('run_selected', $event);
          mode = 'run';
        "
      />
      <ShowRun
        v-if="mode === 'run'"
        :run_id="run_id"
        @overview="
          $emit('run_selected', null);
          mode = 'overview';
        "
      ></ShowRun>
      <NewRun
        v-show="mode === 'new'"
        @target_changed="$emit('target_changed', $event)"
        @overview="mode = 'overview'"
      />
    </div>
  </div>
</template>

<script>
import NewRun from "./Configuration/NewRun.vue";
import SelectRun from "./Configuration/SelectRun.vue";
import ShowRun from "./Configuration/ShowRun.vue";
import { PlusIcon } from "@heroicons/vue/24/solid/index.js";
import Validation from "../mixins.js";

export default {
  name: "SideBar",
  components: {
    SelectRun,
    NewRun,
    ShowRun,
    PlusIcon,
  },
  mixins: [Validation],
  props: ["run_id"],
  emits: ["start_run", "target_changed", "run_selected"],
  data: function () {
    return {
      new_name: "",
      mode: "overview", // overview, run, new
    };
  },
};
</script>