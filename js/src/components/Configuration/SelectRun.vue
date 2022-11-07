<template>
  <div class="flex flex-col space-y-10">
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
</template>

<script>
import { useObservable } from "@vueuse/rxjs";
import { liveQuery } from "dexie";
import { db } from "../../db.js";

export default {
  name: "SelectRun",
  props: ["run_id"],
  emits: ["run_selected"],
  components: {},
  data: () => {
    return {
      new_name: "DriftAnalysisRun",
      stored_runs: useObservable(liveQuery(() => db.runs.toArray())),
    };
  },
};
</script>

<style scoped></style>
