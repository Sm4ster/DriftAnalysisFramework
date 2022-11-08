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
                    v-for="(header, index) in table_headers"
                    scope="col"
                    :class="[
                      index > 0 ? 'px-3 py-3.5' : '',
                      index === 0 ? 'py-3.5 pl-4 pr-3 sm:pl-6 ' : '',
                      index === table_headers.length - 1
                        ? 'py-3.5 pl-3 pr-4 sm:pr-6'
                        : '',
                      'text-left text-sm font-semibold text-gray-900',
                    ]"
                  >
                    <button
                      class="flex"
                      @click="sort(header.code, header.state)"
                    >
                      <span v-if="'name' in header">{{ header.name }}</span>
                      <span v-if="'symbol' in header"
                        >${{ header.symbol }}$</span
                      >
                      <span
                        v-if="sort_by.find((e) => e.code === header.code)"
                        class="ml-2 flex flex-none rounded text-gray-400"
                      >
                        <ChevronDownIcon
                          v-if="
                            sort_by.find((e) => e.code === header.code).dir ===
                            'asc'
                          "
                          class="h-5 w-5"
                          aria-hidden="true"
                        />
                        <ChevronUpIcon
                          v-if="
                            sort_by.find((e) => e.code === header.code).dir ===
                            'desc'
                          "
                          class="h-5 w-5"
                          aria-hidden="true"
                        />
                        <span v-if="sort_by.length > 1">{{
                          sort_by.findIndex((e) => e.code === header.code) + 1
                        }}</span>
                      </span>
                    </button>
                  </th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span class="sr-only">Edit</span>
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white">
                <tr
                  v-for="(datapoint, datapointIdx) in data_"
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
            <div v-if="total_pages > 1" class="py-5">
              <Pagination
                :total_pages="total_pages"
                :current_page="current_page"
                @current_page="current_page = $event"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Pagination from "./elements/Pagination.vue";
import {
  ChevronDownIcon,
  ChevronUpIcon,
} from "@heroicons/vue/20/solid/index.js";
import { sort } from "fast-sort";

export default {
  name: "StateTable",
  components: { Pagination, ChevronDownIcon, ChevronUpIcon },
  props: ["data", "run"],
  emits: ["state_selected"],
  data: () => {
    return {
      table_headers: [
        { code: "id", name: "ID", sortable: true, state: false },
        { code: "drift", name: "Average Drift", sortable: true, state: false },
      ],
      variable_columns: [],
      current_page: 1,
      items_per_page: 20,
      sort_by: [],
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
      this.table_headers.push(
        ...this.variable_columns.map((e) => {
          return {
            symbol: e.symbol,
            code: e.code,
            state: true,
            sortable: true,
          };
        })
      );
    },
    sort(code, state = false) {
      let index = this.sort_by.findIndex((e) => e.code === code);

      if (!this.sort_by[index])
        this.sort_by.push({ code: code, state: state, dir: "asc" });
      else if (this.sort_by[index].dir === "asc")
        this.sort_by[index].dir = "desc";
      else if (this.sort_by[index].dir === "desc")
        this.sort_by.splice(index, 1);
    },
  },
  computed: {
    data_() {
      let sort_by = this.sort_by.map((e) => {
        let object = {};
        object[e.dir] = function (u) {
          return e.state ? u.state[e.code] : u[e.code];
        }.bind(e);
        return object;
      });

      let data = sort(this.data.states).by(sort_by);

      for (let i = 0; i < this.items_per_page; i++) {}
      return data.filter(
        (e, i) =>
          i >= (this.current_page - 1) * this.items_per_page &&
          i < this.current_page * this.items_per_page
      );
    },
    total_pages() {
      return Math.ceil(this.data.states.length / this.items_per_page);
    },
  },
};
</script>