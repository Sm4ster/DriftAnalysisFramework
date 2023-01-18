<template>
  <div class="flex justify-between">
    <div>Precision</div>
    <div class="w-32 flex rounded-md shadow-sm">
      <button @click="precision -= 1" type="button" class="relative -mr-px inline-flex items-center space-x-2 rounded-l-md border border-gray-300 bg-gray-50 px-2 py-1 text-sm font-medium text-gray-700 hover:bg-gray-100 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500">
        <MinusIcon class="h-3 w-3 text-gray-600" aria-hidden="true" />
      </button>
      <div class="relative flex flex-grow justify-center border-y">
        <span class="my-auto text-sm font-light text-gray-600">{{ 1 / Math.pow(10, precision)}}</span>
      </div>
      <button @click="precision += 1" type="button" class="relative -ml-px inline-flex items-center space-x-2 rounded-r-md border border-gray-300 bg-gray-50 px-2 py-1 text-sm font-medium text-gray-700 hover:bg-gray-100 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500">
        <PlusIcon class="h-3 w-3 text-gray-600" aria-hidden="true" />
      </button>
    </div></div>
</template>

<script>
import {PlusIcon, MinusIcon} from "@heroicons/vue/24/outline";

export default {
  name: "Precision",
  components: {
    PlusIcon,
    MinusIcon
  },
  data: ()=> {
    return {

      precision: 2
    }
  }
}
</script>
