<template>
  <div class="h-screen overflow-y-auto py-10 px-10">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Data Overview</h1>
      </div>
    </div>

    <div v-if="mode === 'overview'" class="mt-8">
      <LocationsTable
        :data="data"
        @location_selected="
          location_id = $event;
          mode = 'location';
        "
      />
    </div>

    <div v-if="mode === 'location'" class="mt-8">
      <div class="my-3 px-3">
        <button
          @click="mode = 'overview'"
          class="flex space-x-2 font-semibold text-indigo-600"
        >
          <ArrowLeftIcon class="my-auto h-5 w-5" />
          <span class="text-lg">Locations</span>
        </button>
      </div>
      <StateTable
        :run="run"
        :data="data[location_id]"
        @state_selected="
          state_id = $event;
          mode = 'state';
        "
      />
    </div>

    <div v-if="mode === 'state'" class="mt-8">
      <div class="my-3 px-3">
        <button
          @click="mode = 'location'"
          class="flex space-x-2 font-semibold text-indigo-600"
        >
          <ArrowLeftIcon class="my-auto h-5 w-5" />
          <span class="text-lg">State</span>
        </button>
      </div>
      <SamplesTable :run="run" :data="data[location_id].states[state_id]" />
    </div>
  </div>
</template>

<script>
import LocationsTable from "./LocationsTable.vue";
import StateTable from "./StateTable.vue";
import SamplesTable from "./SamplesTable.vue";
import { ArrowLeftIcon } from "@heroicons/vue/outline";

export default {
  name: "DataView",
  props: ["data", "run"],
  components: { LocationsTable, StateTable, SamplesTable, ArrowLeftIcon },
  data: () => {
    return {
      mode: "overview", // overview, location, state
      location_id: "",
      state_id: "",
    };
  },
  watch: {
    run() {
      this.mode = "overview";
    },
  },
};
</script>