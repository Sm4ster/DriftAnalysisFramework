<template>
  <div class="">
    <div class="relative mb-5">
      <div
        class="absolute ml-1.5 mb-5 block bg-white pr-0.5 pl-0.5 text-sm font-medium text-indigo-700"
      >
        Sampling Options
      </div>
      <div class="flex h-6 w-full flex-col justify-center">
        <hr />
      </div>
    </div>

    <div class="mb-5 flex flex-col space-y-3">
      <div v-for="value in values" class="flex justify-between">
        <label class="my-auto">$x_{{ value.dimension }}$</label>
        <div class="flex space-x-3">
          <div
            :class="[
              has_value_error(value.dimension, 'field_1')
                ? 'border-red-500 bg-red-400'
                : 'border-gray-300 bg-white',
              'relative w-20 rounded-md border px-3 py-2 shadow-sm focus-within:border-indigo-600 focus-within:ring-1 focus-within:ring-indigo-600',
            ]"
          >
            <label
              class="absolute -top-2 left-2 -mt-px inline-block rounded bg-white px-1 text-xs font-medium text-gray-900"
            >
              <span v-if="typeof value.distribution.fields[0] === 'string'">{{
                value.distribution.fields[0]
              }}</span>
              <span v-else>$\{{ value.distribution.fields[0].symbol }}$</span>
            </label>
            <input
              v-model="value.field_1"
              type="number"
              :class="[
                has_value_error(value.dimension, 'field_1')
                  ? 'bg-red-400'
                  : 'bg-white',
                'block w-full appearance-none border-0 p-0 text-gray-900 placeholder-gray-500 focus:outline-0 focus:ring-0 sm:text-sm',
              ]"
            />
          </div>
          <div
            :class="[
              has_value_error(value.dimension, 'field_2')
                ? 'border-red-500 bg-red-400'
                : 'border-gray-300 bg-white',
              'relative w-20 rounded-md border px-3 py-2 shadow-sm focus-within:border-indigo-600 focus-within:ring-1 focus-within:ring-indigo-600',
            ]"
          >
            <label
              class="absolute -top-2 left-2 -mt-px inline-block rounded bg-white px-1 text-xs font-medium text-gray-900"
            >
              <span v-if="typeof value.distribution.fields[1] === 'string'">{{
                value.distribution.fields[1]
              }}</span>
              <span v-else>$\{{ value.distribution.fields[1].symbol }}$</span>
            </label>
            <input
              v-model="value.field_2"
              type="number"
              :class="[
                has_value_error(value.dimension, 'field_2')
                  ? 'bg-red-400'
                  : 'bg-white',
                'block w-full appearance-none border-0 p-0 text-gray-900 placeholder-gray-500 focus:outline-0 focus:ring-0 sm:text-sm',
              ]"
            />
          </div>
          <StateVariableOptions
            :init="{ distribution: 'uniform', scale: 'linear' }"
            @rand_alg="select_rand_alg($event, value)"
            @scale="select_scale($event, value)"
          />
        </div>
      </div>
    </div>
    <div class="flex w-full flex-col justify-between">
      <label class="mb-3 flex justify-between text-xs font-light text-gray-800">
        <span>Quantity</span>
        <span
          >{{
            quantity.reduce((sum, value) => (sum *= value), 1)
          }}
          Locations</span
        >
      </label>
      <div class="flex space-x-2">
        <div class="flex space-x-2" v-for="(q, i) in quantity">
          <span v-if="i > 0" class="my-auto text-sm text-gray-800">x</span>
          <div
            :class="[
              has_error('quantity_' + i)
                ? 'border-red-500 bg-red-400'
                : 'border-gray-300 bg-white',
              'relative w-full rounded-md border px-3 py-2 shadow-sm focus-within:border-indigo-600 focus-within:ring-1 focus-within:ring-indigo-600',
            ]"
          >
            <input
              v-model="quantity[i]"
              type="number"
              :class="[
                has_error('quantity') ? 'bg-red-400' : 'bg-white',
                'block w-full appearance-none border-0 p-0 text-gray-900 placeholder-gray-500 focus:outline-0 focus:ring-0 sm:text-sm',
              ]"
            />
            <label
              class="absolute -top-3 left-2 -mt-px inline-block rounded bg-white px-1 text-sm font-semibold text-gray-600"
            >
              <span> $x_{{ i + 1 }}$ </span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import StateVariables from "./StateVariables.vue";
import StateVariableOptions from "../elements/StateVariableOptions.vue";
import Validation from "../../../mixins.js";
import options from "../../../../../definitions/options/options.json";

export default {
  name: "StateLocation",
  components: {
    StateVariables,
    StateVariableOptions,
  },
  mixins: [Validation],
  props: ["algorithm"],
  data() {
    return {
      dimensions: 2,
      values: [],
      value_errors: {},
      quantity: [],
    };
  },
  created() {
    for (let i = 0; i < this.dimensions; i++) {
      this.quantity[i] = 10;

      this.value_errors[i + 1] = {};
      this.values.push({
        dimension: i + 1,
        field_1: -100,
        field_2: 100,
        distribution: options.distributions.find((e) => e.id === "uniform"),
        scale: options.scales.find((e) => e.id === "linear"),
      });
    }
  },
  updated() {
    MathJax.typeset();
  },
  computed: {
    total_locations() {
      return this.quantity.reduce((sum, value) => (sum += value), 0);
    },
  },
  methods: {
    select_rand_alg(e, v) {
      v.distribution = e;
    },
    select_scale(e, v) {
      v.scale = e;
    },
    has_value_error(index, name) {
      return name in this.value_errors[index]
        ? this.value_errors[index][name].length > 0
        : false;
    },
    export() {
      for (let i = 1; i <= this.dimensions; i++) {
        this.value_errors[i] = this.validate(
          {
            field_1: this.values[i - 1].field_1,
            field_2: this.values[i - 1].field_2,
          },
          {
            field_1: "required|numeric",
            field_2: "required|numeric",
          }
        );
        if (this.value_errors[i].length > 0) throw "validation error";
      }

      this.validate(
        {
          quantity: this.quantity,
        },
        {
          quantity: "required|numeric|gt:0",
        }
      );

      if (this.validation_error) throw "validation error";

      return {
        vector: this.values.map((e, i) => {
          let obj = {
            distribution: e.distribution.id,
            scale: e.scale.id,
            quantity: this.quantity[i],
          };
          obj[
            typeof e.distribution.fields[0] === "object"
              ? e.distribution.fields[0].code
              : e.distribution.fields[0]
          ] = e.field_1;
          obj[
            typeof e.distribution.fields[1] === "object"
              ? e.distribution.fields[1].code
              : e.distribution.fields[1]
          ] = e.field_2;
          return obj;
        }),
      };
    },
  },
};
</script>