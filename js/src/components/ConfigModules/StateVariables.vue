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
      console.log("initing the algorithm now");
      this.init_algorithm();
    },
  },
  updated() {
    MathJax.typeset();
  },
  methods: {
    init_algorithm() {
      this.definition = alg_defs.find(
        (e) => e.algorithm === this.algorithm
      ).state_variables;
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

      console.log(variables);
      for (const el of this.definition) {
        variables[el.code] = this.$refs[el.code][0].export();
      }

      return variables;
    },
  },
};
</script>