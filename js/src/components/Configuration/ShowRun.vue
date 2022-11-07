<template>
  <div>
    <div class="sticky top-0 z-40 bg-indigo-600 px-5 py-3">
      <button @click="$emit('overview')" class="flex font-semibold text-white">
        <ArrowLeftIcon class="my-auto mr-1 h-4 w-4" />
        <span>Overview</span>
      </button>
    </div>
    <div v-if="run_data">{{ run_data.config }}</div>
    <PotentialFunction />

    <SingleFilterVariable v-for="filter_variable in filter_variables">
      <template v-slot:title>
        <div :class="[filter_variable.bottom_bias ? 'mt-1.5' : '']">
          ${{ filter_variable.symbol }}$
        </div>
      </template>
      <template v-slot:code>{{ filter_variable.code }}</template>
    </SingleFilterVariable>
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
  computed: {
    filter_variables() {
      let variables = [];

      if (this.run_data) {
        console.log(this.run_data);
        let algorithm = alg_defs.find(
          (e) => e.algorithm === this.run_data.config.algorithm
        ).state_variables;

        for (const [key, value] of Object.entries(
          this.run_data.config.variables
        )) {
          let state_variable = algorithm.find((e) => e.code === key);
          variables.push({
            code: key,
            symbol: state_variable.symbol,
            bottom_bias: state_variable.bottom_bias,
            name: key,
            ...value,
          });
        }
      }

      return variables;
    },
  },
};
</script>

<style scoped></style>
