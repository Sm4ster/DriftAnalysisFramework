<template>
  <div
    class="relative flex flex-col justify-between border-l border-indigo-600"
  >
    <div class="sticky top-0 flex flex-col bg-white">
      <h1 class="mx-auto mt-5 mb-10 font-cuprum text-4xl font-bold">
        DriftAnalysis
      </h1>

      <SelectRun
        v-show="mode === 'overview'"
        :run_id="run_id"
        @new_run="mode = 'new'"
        @run_selected="
          $emit('run_selected', $event);
          mode = 'run';
        "
      />
      <ShowRun
        class="mb-10"
        v-if="mode === 'run'"
        :run_id="run_id"
        @filters="$emit('filters', $event)"
        @apply_filters="$emit('apply_filters', $event)"
        @overview="
          $emit('run_selected', null);
          mode = 'overview';
        "
      ></ShowRun>
      <NewRun
        v-show="mode === 'new'"
        @target_changed="$emit('target_changed', $event)"
        @overview="mode = 'overview'"
        @start_run="
          $emit('start_run', $event);
          mode = 'overview';
        "
      />
    </div>
  </div>
</template>

<script>
import NewRun from "./Configuration/NewRun.vue";
import SelectRun from "./Configuration/SelectRun.vue";
import ShowRun from "./Configuration/ShowRun.vue";

export default {
  name: "SideBar",
  components: {
    SelectRun,
    NewRun,
    ShowRun,
  },

  props: ["run_id"],
  emits: [
    "start_run",
    "target_changed",
    "run_selected",
    "filters",
    "apply_filters",
  ],
  data: function () {
    return {
      mode: "overview", // overview, run, new
    };
  },
};
</script>