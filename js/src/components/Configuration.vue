<template>
  <div class="relative flex flex-col justify-between border-l border-indigo-600">
    <div class="flex flex-col sticky top-0 z-50 bg-white ">

      <h1 class="text-4xl mx-auto mt-5 font-cuprum font-bold mb-10">DriftAnalysis</h1>
<!--      <div class=" h-12 flex font-thin justify-between">-->
<!--        <button class="w-1/2 bg-indigo-600">-->
<!--          <div class="mx-auto text-white  font-semibold my-auto">New run</div></button>-->
<!--        <button  class="w-1/2 ">Examine runs</button>-->
<!--      </div>-->


      <div class="flex flex-col px-5 py-5 bg-indigo-600">
<!--        <label class="my-auto text-sm mb-1 text-white font-thin">Name</label>-->
        <div
            :class="[has_error('name') ?  'bg-red-400 border-red-500': 'bg-white border-gray-300', 'mr-2 w-full relative border rounded-md px-3 py-2 shadow-sm focus-within:ring-1 focus-within:ring-indigo-600 focus-within:border-indigo-600']">
          <input v-model="name" type="text"
                 :class="[has_error('name') ? 'bg-red-400' : 'bg-white', 'block w-full border-0 p-0 text-gray-900 placeholder-gray-500 focus:ring-0 focus:outline-0 sm:text-sm appearance-none']"/>
        </div>
      </div>

    </div>
    <div class="px-5 py-10 space-y-10">
      <TargetFunction ref="target" :init_params="target_params"
                      @param_update="$emit('target_changed', $event)"></TargetFunction>
      <StateLocation ref="location" :algorithm="algorithm"/>
      <PotentialFunction ref="potential"/>

      <AlgorithmOptions ref="algorithm" @selected="algorithm = $event"/>
      <StateVariables ref="variables" :algorithm="algorithm"/>


    </div>


    <div class="flex flex-col sticky bottom-0 border-t-2 border-indigo-600">
      <button class="bg-indigo-600 hover:bg-indigo-500 text-white pt-3 pb-5 font-semibold" @click="start_run">
        Start run
      </button>
    </div>
  </div>
</template>

<script>
import TargetFunction from "./ConfigModules/TargetFunction.vue";
import PotentialFunction from "./ConfigModules/PotentialFunction.vue";
import AlgorithmOptions from "./ConfigModules/AlgorithmOptions.vue";
import StateLocation from "./ConfigModules/StateLocation.vue";
import StateVariables from "./ConfigModules/StateVariables.vue";
import Validation from "../mixins";

export default {
  name: "Configuration",
  components: {TargetFunction, StateLocation, StateVariables, PotentialFunction, AlgorithmOptions},
  mixins: [Validation],
  emits: ["start_run", "target_changed"],
  data: function () {
    return {
      name: "DriftAnalysisRun",
      algorithm: "",
      target_params:
          {
            A: 1,
            B: 0,
            C: 1,
          },
    }
  },
  created() {
    this.$emit("target_changed", this.target_params)
  },
  methods: {
    start_run() {
      try {

        const algorithm = this.$refs.algorithm.export();
        this.$emit("start_run", {
              "name": this.name,
              "algorithm": algorithm.selected,
              "target": this.$refs.target.export(),
              "potential": this.$refs.potential.export(),
              "constants": algorithm.options,
              "location": this.$refs.location.export(),
              "variables": this.$refs.variables.export(),
            }
        );
      } catch (e) {
        alert("cannot start because of " + e)
      }

    }
  }

}
</script>


