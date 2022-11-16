<template>
  <div>
    <div class="sticky top-0 z-40 bg-indigo-600 px-5 py-3">
      <button @click="$emit('overview')" class="flex font-semibold text-white">
        <ArrowLeftIcon class="my-auto mr-1 h-4 w-4" />
        <span>Overview</span>
      </button>
    </div>
    <div v-if="run_data" class="mt-5 space-y-10 px-5">
      <div>
        <div>
          <div class="flex flex-col space-y-5 text-sm text-gray-900">
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
                <div v-for="constant in constants" class="flex justify-between">
                  <div>
                    ${{ constant.symbol }}$
                    <span class="ml-2 font-mono text-xs"
                      >({{ constant.code }})</span
                    >
                  </div>

                  <span class="font-light">{{ constant.value }}</span>
                </div>
                <div
                  v-for="constant in filter_variables(false)"
                  class="flex justify-between"
                >
                  <span class=""
                    >${{ constant.symbol }}$
                    <span class="ml-2 font-mono text-xs"
                      >({{ constant.code }})</span
                    >
                  </span>

                  <span class="font-light">{{ constant.value }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="flex flex-col">
        <h4 class="mb-2 text-xs font-semibold uppercase text-gray-400">
          Potential Function
        </h4>
        <div v-if="!edit_potential" class="flex flex-col">
          <hr />
          <span class="py-3 px-2 font-light text-gray-900">
            {{ run_data.config.potential }}
          </span>
          <hr />
        </div>

        <PotentialFunction
          class="mt-5"
          v-if="edit_potential"
          ref="potential"
          :header="false"
        />
        <div class="flex justify-end space-x-3">
          <button class="text-right" @click="edit_potential = !edit_potential">
            <span class="mt-3 text-xs text-gray-700 hover:text-indigo-800">{{
              edit_potential ? "Cancel" : "Edit"
            }}</span>
          </button>
          <button
            class="text-right"
            v-if="edit_potential"
            @click="eval_potential()"
          >
            <span
              class="inline-flex items-center rounded border border-indigo-600 bg-white px-2.5 py-1 text-xs font-medium text-indigo-700 shadow-sm hover:bg-indigo-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >Evaluate</span
            >
          </button>
        </div>
      </div>

      <div class="text-xs">
        <div class="relative mb-5">
          <div
            class="absolute ml-1.5 mb-5 block bg-white pr-0.5 pl-0.5 text-sm font-medium text-indigo-700"
          >
            Filters
          </div>
          <button
            @click="$emit('apply_filters', { init: false })"
            type="button"
            class="absolute right-0 inline-flex items-center rounded border border-indigo-600 bg-white px-2.5 py-1 text-xs font-medium text-indigo-700 shadow-sm hover:bg-indigo-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            Apply
          </button>
          <div class="flex h-6 w-full flex-col justify-center">
            <hr />
          </div>
        </div>
        <h4 class="mb-2 text-xs font-semibold uppercase text-gray-400">
          Location
        </h4>
        <div class="mb-8 space-y-5">
          <SingleFilterVariable
            @filter="filters.location[0] = $event"
            :extreme_values="run_data.config.location.vector[0]"
          >
            <template v-slot:title>$x_1$</template>
          </SingleFilterVariable>
          <SingleFilterVariable
            @filter="filters.location[1] = $event"
            :extreme_values="run_data.config.location.vector[1]"
          >
            <template v-slot:title>$x_2$</template>
          </SingleFilterVariable>
        </div>
        <h4 class="mb-2 text-xs font-semibold uppercase text-gray-400">
          Variables
        </h4>
        <div class="flex flex-col space-y-5">
          <SingleFilterVariable
            :extreme_values="extreme_values(filter_variable.code)"
            @filter="filters.variables[filter_variable.code] = $event"
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
              ><span>{{ filter_variable.code }}</span></template
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
  emits: ["overview", "filters", "apply_filters", "eval_potential"],
  data: () => {
    return {
      edit_potential: false,
      run_data: null,
      filters: {
        location: [],
        variables: {},
      },
    };
  },
  created() {
    db.runs
      .where({ uuid: this.run_id })
      .first()
      .then((data) => {
        this.run_data = data;
        this.$emit("apply_filters", { init: true });
      });
  },
  mounted() {
    this.$emit("filters", this.filters);
  },
  methods: {
    eval_potential() {
      this.$store.commit("eval_potential", this.$refs.potential.export());
    },
    extreme_values(code) {
      if (this.run_data.config.variables[code].variation)
        return {
          min: this.run_data.config.variables[code].min,
          max: this.run_data.config.variables[code].max,
        };
      //TODO for other distributions we need to extract min and max from the data
    },
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
      let algorithm_constants = alg_defs.find(
        (e) => e.algorithm === this.run_data.config.algorithm
      ).algorithm_constants;

      return Object.entries(this.run_data.config.constants).map(
        ([key, constant]) => {
          return {
            code: key,
            symbol: algorithm_constants.find((e) => e.code === key).symbol,
            value: constant,
          };
        }
      );
    },
  },
};
</script>

<style scoped></style>