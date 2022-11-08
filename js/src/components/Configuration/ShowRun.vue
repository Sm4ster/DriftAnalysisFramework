<template>
  <div>
    <div class="sticky top-0 z-40 bg-indigo-600 px-5 py-3">
      <button @click="$emit('overview')" class="flex font-semibold text-white">
        <ArrowLeftIcon class="my-auto mr-1 h-4 w-4" />
        <span>Overview</span>
      </button>
    </div>
    <div class="mt-5 space-y-10 px-5">
      <div>
        <div>
          <div
            v-if="run_data"
            class="flex flex-col space-y-5 text-sm text-gray-900"
          >
            <div class="">
              <h4 class="mb-2 text-xs font-semibold uppercase text-gray-400">
                Algorithm
              </h4>
              <span>{{ run_data.config.algorithm }}</span>
            </div>
            <div class="">
              <h4 class="mb-2 text-xs font-semibold uppercase text-gray-400">
                Constants
              </h4>
              <div class="space-y-2">
                <div
                  v-for="[key, constant] in constants"
                  class="flex justify-between"
                >
                  <span class="">{{ key }}</span>
                  <span class="font-light">{{ constant }}</span>
                </div>
                <div
                  v-for="constant in filter_variables(false)"
                  class="flex justify-between"
                >
                  <span class="">${{ constant.symbol }}$</span>
                  <span class="font-light">{{ constant.value }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <PotentialFunction />

      <div class="text-xs">
        <div class="relative mb-5">
          <div
            class="absolute ml-1.5 mb-5 block bg-white pr-0.5 pl-0.5 text-sm font-medium text-indigo-700"
          >
            Filters
          </div>
          <div class="flex h-6 w-full flex-col justify-center">
            <hr />
          </div>
        </div>
        <div>
          <SingleFilterVariable
            v-for="filter_variable in filter_variables(true)"
          >
            <template v-slot:title>
              <div
                :class="[
                  filter_variable.bottom_bias ? 'mt-1.5' : '',
                  'text-base',
                ]"
              >
                ${{ filter_variable.symbol }}$
              </div>
            </template>
            <template v-slot:code
              ><span class="text-xs">{{ filter_variable.code }}</span></template
            >
          </SingleFilterVariable>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ArrowLeftIcon } from "@heroicons/vue/24/solid/index.js";
import { db } from "../../db.js";
import PotentialFunction from "./modules/PotentialFunction.vue";
import SingleFilterVariable from "./elements/SingleFilterVariable.vue";

export default {
  name: "ShowRun",
  components: {
    ArrowLeftIcon,
    PotentialFunction,
    SingleFilterVariable,
  },
  props: ["run_id"],
  emits: ["overview"],
  data: () => {
    return {
      run_data: null,
    };
  },
  created() {
    db.runs
      .where({ uuid: this.run_id })
      .first()
      .then((data) => {
        this.run_data = data;
      });
  },
  methods: {
    filter_variables(variation) {
      let variables = [];

      if (this.run_data) {
        let algorithm = alg_defs.find(
          (e) => e.algorithm === this.run_data.config.algorithm
        ).state_variables;

        for (const [key, value] of Object.entries(
          this.run_data.config.variables
        )) {
          let state_variable = algorithm.find((e) => e.code === key);
          if (
            this.run_data.config.variables[state_variable.code].variation ===
            variation
          ) {
            variables.push({
              code: key,
              symbol: state_variable.symbol,
              bottom_bias: state_variable.bottom_bias,
              name: key,
              ...value,
            });
          }
        }
      }

      return variables;
    },
  },
  computed: {
    constants() {
      return Object.entries(this.run_data.config.constants);
    },
  },
};
</script>

<style scoped></style>