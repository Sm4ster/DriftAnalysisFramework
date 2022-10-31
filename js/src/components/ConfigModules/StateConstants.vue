<template>
  <div class="space-y-5">
    <div class="space-y-3">
      <label class="text-xs uppercase text-gray-500">Algorithm Constants</label>
      <div
        v-for="algorithm_constant in definition"
        class="my-auto flex justify-between space-x-3"
      >
        <div class="my-auto" :key="algorithm_constant.code + counter">
          ${{ algorithm_constant.symbol }}$
          <span class="font-mono text-sm">({{ algorithm_constant.code }})</span>
        </div>
        <div
          :class="[
            has_error(algorithm_constant.code)
              ? 'border-red-500 bg-red-400'
              : 'border-gray-300 bg-white',
            'relative w-24 rounded-md  border px-3 py-2 shadow-sm focus-within:border-indigo-600 focus-within:ring-1 focus-within:ring-indigo-600',
          ]"
        >
          <input
            v-model="values[algorithm_constant.code]"
            type="number"
            :class="[
              has_error(algorithm_constant.code) ? 'bg-red-400' : 'bg-white',
              'block w-full appearance-none border-0 p-0 text-gray-900 placeholder-gray-500 focus:outline-0 focus:ring-0 sm:text-sm',
            ]"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Validation from "../../mixins.js";
import CMA_ES from "../../../../definitions/algorithms/CMA-ES.json";
import OnePlusOne_ES from "../../../../definitions/algorithms/1+1-ES.json";
import StateVariableOptions from "./elements/StateVariableOptions.vue";

export default {
  props: ["algorithm"],
  name: "StateConstants",
  components: { StateVariableOptions },
  mixins: [Validation],
  data() {
    return {
      init: false,
      counter: 0,

      definition: null,
      values: {},
    };
  },
  beforeUpdate() {
    this.counter += 1;
  },
  updated() {
    MathJax.typeset();
  },
  created() {
    this.init_algorithm();
    this.init_defaults();
    MathJax.typeset();
  },
  watch: {
    algorithm() {
      this.init_algorithm();
      if (!this.init) this.init_defaults();
      MathJax.typeset();
    },
  },
  methods: {
    init_algorithm() {
      let algorithm;
      if (this.algorithm === "CMA-ES") algorithm = CMA_ES;
      if (this.algorithm === "1+1-ES") algorithm = OnePlusOne_ES;

      this.definition = algorithm.algorithm_constants;
      this.values = {};
    },
    init_defaults() {
      this.definition.forEach(
        function (constant) {
          this.values[constant.code] = constant.default;
        }.bind(this)
      );
    },
    export() {
      let rules = {};
      this.definition.forEach((e) => {
        rules[e.code] = e.validation;
      });
      this.validate(this.values, rules);
      if (this.validation_error)
        throw "validation_error in the state constants";

      return this.values;
    },
  },
};
</script>