<template>
  <div class="h-screen overflow-y-auto py-10 px-10">
    <div class="sm:flex sm:items-center">
      <div class="mb-4 sm:flex-auto">
        <button
          v-if="mode_idx >= 1"
          @click="mode_idx -= 1"
          class="flex space-x-1 text-indigo-600"
        >
          <ArrowLeftIcon class="my-auto h-3 w-3" />
          <span class="text-sm font-semibold">{{
            modes[mode_idx - 1].name
          }}</span>
        </button>

        <h1 class="text-3xl font-semibold text-gray-900">
          <span>{{ modes[mode_idx].name }}</span>
        </h1>
      </div>
    </div>

    <div class="mb-5 flex flex-col">
      <div
        v-if="
          modes[mode_idx].code === 'location' ||
          modes[mode_idx].code === 'state'
        "
        class="mb-3 flex space-x-5"
      >
        <div>
          <h4 class="text-xs font-semibold text-gray-300">Location</h4>
          <span class="text-sm text-gray-600">{{
            data[location_id].location
          }}</span>
        </div>
        <div>
          <h4 class="text-xs font-semibold text-gray-300">
            Average Location Drift
          </h4>
          <span class="text-sm text-gray-600">{{
            data[location_id].drift
          }}</span>
        </div>
      </div>

      <div v-if="modes[mode_idx].code === 'state'">
        <div>
          <h4 class="text-xs font-semibold text-gray-300">State</h4>
          <span class="text-sm text-gray-600">{{
            data[location_id].states[state_id].state
          }}</span>
        </div>
        <div>
          <h4 class="text-xs font-semibold text-gray-300">
            Average State Drift
          </h4>
          <span class="text-sm text-gray-600">{{
            data[location_id].states[state_id].drift
          }}</span>
        </div>
      </div>
    </div>

    <div v-if="modes[mode_idx].code === 'overview'">
      <LocationsTable
        :data="data"
        @location_selected="
          location_id = $event;
          mode_idx += 1;
        "
      />
    </div>

    <div v-if="modes[mode_idx].code === 'location'">
      <StateTable
        :run="$store.getters.selected_run_data"
        :data="data[location_id]"
        @state_selected="
          state_id = $event;
          mode_idx += 1;
        "
      />
    </div>

    <div v-if="modes[mode_idx].code === 'state'">
      <SamplesTable
        :run="$store.getters.selected_run_data"
        :data="data[location_id].states[state_id]"
        :potential_function="potential_function"
      />
    </div>
  </div>
</template>

<script>
import LocationsTable from "./LocationsTable.vue";
import StateTable from "./StateTable.vue";
import SamplesTable from "./SamplesTable.vue";
import { ArrowLeftIcon } from "@heroicons/vue/24/solid";

export default {
  name: "DataView",
  props: ["potential_function"],
  components: { LocationsTable, StateTable, SamplesTable, ArrowLeftIcon },
  data: () => {
    return {
      modes: [
        { code: "overview", name: "Overview" },
        { code: "location", name: "States" },
        { code: "state", name: "Samples" },
      ],
      mode_idx: 0,
      location_id: "",
      state_id: "",
    };
  },
  computed: {
    data(){
      return this.$store.state.locations
    },
  }
};
</script>