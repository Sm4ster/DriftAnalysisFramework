<template>
  <div class="my-auto">
    <div class="my-auto flex space-x-2 text-center mb-3 justify-between">
      <div class="my-auto flex">
        <span class="font-mono text-sm">
          <slot name="code"></slot>
        </span>
      </div>

      <div class="space-x-3">
        <label class="text-xs font-semibold">Enable Variation</label>
        <Switch v-model="variation_enabled"
                class="my-auto flex-shrink-0 group relative rounded-full inline-flex items-center justify-center h-3 w-9 cursor-pointer focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          <span class="sr-only">Use setting</span>
          <span aria-hidden="true" class="pointer-events-none absolute bg-white w-full h-full rounded-md"/>
          <span aria-hidden="true"
                :class="[variation_enabled ? 'bg-indigo-600' : 'bg-gray-200', 'pointer-events-none absolute h-2.5 w-6 mx-auto rounded-full transition-colors ease-in-out duration-200']"/>
          <span aria-hidden="true"
                :class="[variation_enabled ? 'translate-x-5' : 'translate-x-0', 'pointer-events-none absolute left-0 inline-block h-4 w-4 border border-gray-200 rounded-full bg-white shadow transform ring-0 transition-transform ease-in-out duration-200']"/>
        </Switch>
      </div>
    </div>


    <div class="flex justify-between">
      <div class="text-lg">
        <slot name="title"></slot>
      </div>

      <div v-if="variation_enabled" class="flex space-x-3">
        <div
            :class="[has_error('field_1') ?  'bg-red-400 border-red-500': 'bg-white border-gray-300', 'w-12 relative border rounded-md px-3 py-2 shadow-sm focus-within:ring-1 focus-within:ring-indigo-600 focus-within:border-indigo-600']">
          <label
              class="absolute -top-2 left-2 -mt-px inline-block rounded px-1 bg-white text-xs font-medium text-gray-900">
            <span
                v-if="typeof selected_distribution.fields[0] === 'string'">{{
                selected_distribution.fields[0]
              }}</span>
            <span v-else>$\{{ selected_distribution.fields[0].symbol }}$</span>
          </label>
          <input v-model="variable.field_1" type="number"
                 :class="[has_error('field_1') ? 'bg-red-400' : 'bg-white',  'block w-full border-0 p-0 text-gray-900 placeholder-gray-500 focus:ring-0 focus:outline-0 sm:text-sm appearance-none']"/>
        </div>
        <div
            :class="[has_error('field_2') ?  'bg-red-400 border-red-500': 'bg-white border-gray-300', 'w-12 relative border rounded-md px-3 py-2 shadow-sm focus-within:ring-1 focus-within:ring-indigo-600 focus-within:border-indigo-600']">
          <label
              class="absolute -top-2 left-2 -mt-px inline-block rounded px-1 bg-white text-xs font-medium text-gray-900">
            <span
                v-if="typeof selected_distribution.fields[1] === 'string'">{{
                selected_distribution.fields[1]
              }}</span>
            <span v-else>$\{{ selected_distribution.fields[1].symbol }}$</span>
          </label>
          <input v-model="variable.field_2" type="number"
                 :class="[has_error('field_2') ? 'bg-red-400' : 'bg-white', 'block w-full border-0 p-0 text-gray-900 placeholder-gray-500 focus:ring-0 focus:outline-0 sm:text-sm appearance-none']"/>
        </div>
        <div
            :class="[has_error('quantity') ?  'bg-red-400 border-red-500': 'bg-white border-gray-300', 'w-16 relative border border-gray-300 rounded-md px-3 py-2 shadow-sm focus-within:ring-1 focus-within:ring-indigo-600 focus-within:border-indigo-600']">
          <label
              class="absolute -top-2 left-2 rounded -mt-px inline-block px-1 bg-white text-xs font-medium text-gray-900">
            n</label>
          <input v-model="variable.quantity" type="number"
                 :class="[has_error('quantity') ? 'bg-red-400' : 'bg-white','block w-full border-0 p-0 text-gray-900 placeholder-gray-500 focus:ring-0 focus:outline-0 sm:text-sm appearance-none']"/>
        </div>

        <StateVariableOptions :init="{distribution: init.distribution, scale: init.scale}"
                              @rand_alg="selected_distribution = $event" @rand_scale="selected_scale = $event"/>
      </div>

      <div v-else
           class="w-24 relative border border-gray-300 rounded-md px-3 py-2 shadow-sm focus-within:ring-1 focus-within:ring-indigo-600 focus-within:border-indigo-600">
        <input v-model="variable.field_1"
               class="block w-full border-0 p-0 text-gray-900 placeholder-gray-500 focus:ring-0 focus:outline-0 sm:text-sm appearance-none"/>
      </div>

    </div>
  </div>
</template>

<script>
import StateVariableOptions from "./StateVariableOptions.vue"
import {Switch} from '@headlessui/vue'
import Validation from "../../../mixins";
import options from "../../../../../options/options.json"

export default {
  name: "SingleStateVariable",
  components: {
    StateVariableOptions,
    Switch,
  },
  mixins: [Validation],
  props: ['init', 'validation', 'quantity'],
  data() {
    return {
      selected_distribution: null,
      selected_scale: null,


      variation_enabled: true,

      variable: {
        field_1: 0,
        field_2: 10,
        quantity: 1000,
      },
    }
  },
  created() {
    this.selected_scale = options.scales.find(e => e.id === this.init.scale);
    this.selected_distribution = options.distributions.find(e => e.id === this.init.distribution);

    this.initialize();
  },
  mounted() {
    MathJax.typeset()
  },
  updated() {
    MathJax.typeset()
  },
  watch: {
    init() {
      this.initialize();
    }
  },
  methods: {
    initialize() {
      if (this.init) {
        this.variable.field_1 = this.init.field_1;
        this.variable.field_2 = this.init.field_2;
        this.variable.quantity = this.init.quantity;

        this.variation_enabled = this.init.variation_enabled
      }
    },
    has_error(key) {
      if (key in this.errors) return this.errors[key];
      return false;
    },
    export() {
      let data = {};
      if (this.variation_enabled) {
        this.validate(this.variable, this.validation);
        if (this.validation_error) throw "validation_error in the state variables"

        for (let i = 0; i < 2; i++) {
          let name = this.selected_distribution.fields[i];
          if (typeof name === 'string') data[name] = this.variable["field_" + (i + 1)];
          else data[name.code] = this.variable["field_" + (i + 1)];
        }
        data['quantity'] = this.variable.quantity;
        data['scale'] = this.selected_scale.id
        data['distribution'] = this.selected_distribution.id
      } else {
        this.validate(
            {field_1: this.variable.field_1},
            {field_1: this.validation.field_1}
        )
        if (this.validation_error) throw "validation_error in the state variables"
        data = {value: this.variable.field_1};
      }

      return {variation: this.variation_enabled, ...data}
    }
  }
}
</script>

<style scoped>
input[type=number]::-webkit-inner-spin-button,
input[type=number]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>