<template>
  <div class="space-y-5">
    <div class="space-y-6">
      <label class="text-xs uppercase text-gray-500">State Variables</label>
      <SingleStateVariable
        v-for="state_variable in definition"
        :ref="state_variable.code"
        :init="defaults(state_variable)"
        :validation="validation(state_variable)"
      >
        <template v-slot:title>
          <div :class="[state_variable.bottom_bias ? 'mt-1.5' : '']">
            ${{ state_variable.symbol }}$
          </div>
        </template>
        <template v-slot:code>{{ state_variable.code }}</template>
      </SingleStateVariable>
    </div>
  </div>
</template>

<script>
import CMA_ES from "../../../../definitions/algorithms/CMA-ES.json";
import OnePlusOne_ES from "../../../../definitions/algorithms/1+1-ES.json";
import SingleStateVariable from "./elements/SingleStateVariable.vue";

export default {
  props: ["algorithm"],
  name: "StateVariables",
  components: { SingleStateVariable },
  data() {
    return {
      definition: null,
      data: {},
    };
  },
  watch: {
    algorithm() {
      this.init_algorithm();
    },
  },
  updated() {
    MathJax.typeset();
  },
  methods: {
    init_algorithm() {
      let algorithm;
      if (this.algorithm === "CMA-ES") algorithm = CMA_ES;
      if (this.algorithm === "1+1-ES") algorithm = OnePlusOne_ES;

      this.definition = algorithm.state_variables;
    },
    defaults(variable) {
      let defaults = {};
      Object.entries(variable.fields).map((e) => {
        defaults[e[0]] = e[1].default;
      });
      return {
        ...defaults,
        ...variable.defaults,
        variation_enabled: variable.variation_enabled,
      };
    },
    validation(variable) {
      let validation = {};
      Object.entries(variable.fields).map((e) => {
        validation[e[0]] = e[1].validation;
      });
      return validation;
    },
    export() {
      let variables = {};

      for (const el of this.definition) {
        variables[el.code] = this.$refs[el.code][0].export();
      }
      console.log(variables);
      return variables;
    },
  },
};
</script>