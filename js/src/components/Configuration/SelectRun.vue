<template>
  <div class="flex flex-col space-y-10">
    <div>
      <div class="flex justify-end bg-indigo-600 px-5 py-3">
        <button
          @click="$emit('new_run')"
          class="flex space-x-1 font-semibold text-white"
        >
          <PlusIcon class="my-auto h-4 w-4" />
          <span>New Run</span>
        </button>
      </div>

      <div v-for="run in runs" class="flex w-full py-3 pl-5 hover:bg-indigo-50">
        <div class="w-full">
          <div class="flex w-full justify-between">
            <div class="font-mono">
              <div>
                <span>{{ run.uuid.slice(run.uuid.length - 5) }}</span>
                <span> - </span>
                <span>{{ run.config.algorithm }}</span>
              </div>
              <div class="text-xs text-gray-500">
                <span>{{ run.started_at }}</span>
              </div>
            </div>
            <button
              v-if="'finished_at' in run"
              @click="
                $store.dispatch('select_run', run.uuid);
                $emit('run_selected', run.uuid);
              "
              class="px-5 py-1"
            >
              <ArrowRightIcon class="my-auto h-4 w-4" />
            </button>
            <div v-else class="my-auto flex px-5 py-1">
              <span class="my-auto mr-3 text-xs"
                >{{ percentage_completed(run) }}%</span
              >
              <CpuChipIcon class="my-auto h-5 w-5" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useObservable } from "@vueuse/rxjs";
import { liveQuery } from "dexie";
import { db } from "../../db.js";
import {
  PlusIcon,
  ArrowRightIcon,
  CpuChipIcon,
} from "@heroicons/vue/24/outline/index.js";
import { sort } from "fast-sort";

export default {
  name: "SelectRun",
  props: ["run_id"],
  emits: ["run_selected"],
  components: {
    PlusIcon,
    ArrowRightIcon,
    CpuChipIcon,
  },
  data: () => {
    return {
      selected_run_uuid: null,
      stored_runs: useObservable(liveQuery(() => db.runs.toArray())),
      locations: useObservable(
        liveQuery(async () => {
          return await db.locations
            .where("run_id", run_id)
            .where("has_results", true)
            .toArray();
        })
      ),
    };
  },
  computed: {
    runs() {
      return sort(this.stored_runs).asc((u) => u.started_at);
    },
  },
  methods: {
    percentage_completed(run) {
      // console.log(this.locations);
      return 100;
    },
  },
};
</script>

<style scoped></style>