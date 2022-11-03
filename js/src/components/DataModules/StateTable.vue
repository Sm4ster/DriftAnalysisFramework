<template>
  <div>
    <div class="flex flex-col">
      <div class="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div class="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
          <div
            class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg"
          >
            <table class="min-w-full divide-y divide-gray-300">
              <thead class="bg-gray-50">
                <tr>
                  <th
                    scope="col"
                    class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6"
                  >
                    Name
                  </th>
                  <th
                    scope="col"
                    class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                  >
                    Average Drift
                  </th>
                  <th
                    v-for="column in variable_columns"
                    scope="col"
                    class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                  >
                    ${{ column.symbol }}$
                  </th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span class="sr-only">Edit</span>
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white">
                <tr
                  v-for="(datapoint, datapointIdx) in data.states"
                  :class="datapointIdx % 2 === 0 ? undefined : 'bg-gray-50'"
                >
                  <td
                    class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6"
                  >
                    {{ datapoint.id }}
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    {{ datapoint.drift }}
                  </td>
                  <td
                    v-for="column in variable_columns"
                    class="whitespace-nowrap px-3 py-4 text-sm text-gray-500"
                  >
                    {{ datapoint.state[column.code] }}
                  </td>
                  <td
                    class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6"
                  >
                    <button
                      @click="$emit('state_selected', datapoint.id)"
                      class="text-indigo-600 hover:text-indigo-900"
                    >
                      Details
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "StateTable",
  props: ["data", "run"],
  emits: ["state_selected"],
  data: () => {
    return {
      variable_columns: [],
    };
  },
  updated() {
    MathJax.typeset();
  },
  created() {
    this.update_columns();
  },
  mounted() {
    MathJax.typeset();
  },
  methods: {
    update_columns() {
      this.variable_columns = Object.entries(this.run.config.variables)
        .filter(([key, value]) => value.variation)
        .map((e) =>
          alg_defs
            .find((e) => e.algorithm === this.run.config.algorithm)
            .state_variables.find((e_) => e_.code === e[0])
        );
    },
  },
};
</script>