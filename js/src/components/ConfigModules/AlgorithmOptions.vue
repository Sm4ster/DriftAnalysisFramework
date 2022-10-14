<template>
  <div class="space-y-3">
    <div class="space-y-4">
      <div class="relative mb-5">
        <div class="absolute bg-white pr-0.5 pl-0.5  ml-1.5 block text-sm text-indigo-700 font-medium mb-5">
          Algorithm
        </div>
        <div class="h-6 flex w-full flex-col justify-center ">
          <hr>
        </div>
      </div>
      <div class="mb-5">
        <div>
          <RadioGroup v-model="selected_algorithm" class="mt-2">
            <div class="flex flex-grow space-x-5">
              <RadioGroupOption as="template" v-for="algorithm in algorithms" :value="algorithm"
                                :disabled="!algorithm.available" v-slot="{ active, checked }">
                <div
                    :class="[algorithm.available ? 'cursor-pointer focus:outline-none' : 'opacity-25 cursor-not-allowed', active ? 'ring-2 ring-offset-2 ring-indigo-500' : '', checked ? 'bg-indigo-600 border-transparent text-white hover:bg-indigo-700' : 'bg-white border-gray-200 text-gray-900 hover:bg-gray-50', 'border rounded-md py-2 px-2 flex items-center justify-center text-sm font-medium uppercase sm:flex-1']">
                  <RadioGroupLabel as="p">
                    {{ algorithm.name }}
                  </RadioGroupLabel>
                </div>
              </RadioGroupOption>
            </div>
          </RadioGroup>
        </div>
        <StateConstants ref="constants" class="mt-5" :algorithm="selected_algorithm.name" />
      </div>
    </div>
  </div>
</template>

<script>

import {RadioGroup, RadioGroupDescription, RadioGroupLabel, RadioGroupOption} from '@headlessui/vue'
import StateConstants from "./StateConstants.vue";

export default {
  name: "AlgorithmOptions",
  components: {
    StateConstants,
    RadioGroup,
    RadioGroupDescription,
    RadioGroupLabel,
    RadioGroupOption,
  },
  data: function () {
    return {
      algorithms: [
        {name: "1+1-ES", available: true},
        {name: "CMA-ES", available: true},
      ],
      selected_algorithm: null,
    }
  },
  created() {
    this.selected_algorithm = this.algorithms[0];
  },
  mounted() {
    MathJax.typeset()
  },
  watch: {
    selected_algorithm(e){
      this.$emit("selected", e.name)
      this.$nextTick(() => {
        MathJax.typeset()
      })
    }
  },
  computed: {},
  methods: {
    export() {
      return {
        selected: this.selected_algorithm.name,
        options: this.$refs.constants.export()
      }
    }
  }
}
</script>