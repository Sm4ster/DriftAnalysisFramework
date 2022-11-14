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
                    v-show="!('dynamic' in header)"
                    :class="[
                      index > 0 ? 'px-3 py-3.5' : '',
                      index === 0 ? 'py-3.5 pl-4 pr-3 sm:pl-6 ' : '',
                      index === table_headers.length - 1
                        ? 'py-3.5 pl-3 pr-4 sm:pr-6'
                        : '',
                      header.dynamic
                        ? 'text-indigo-700'
                        : 'font-normal text-gray-900',
                      'w-10 text-left text-sm',
                    ]"
                  >
                    <button
                      v-if="header.sortable"
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
                        <span v-if="sort_by.length > 1">
                          {{
                            sort_by.findIndex((e) => e.code === header.code) + 1
                          }}
                        </span>
                      </span>
                    </button>
                    <span v-else>{{ header.name }}</span>
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white">
                <tr
                  v-for="(datapoint, datapointIdx) in data_"
                  :class="datapointIdx % 2 === 0 ? undefined : 'bg-gray-50'"
                >
                  <td
                    class="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-900 sm:pl-6"
                  >
                    {{ datapointIdx }}
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    {{ datapoint.follow_up_state.m }}
                  </td>
                  <td
                    v-for="column in variable_columns"
                    class="whitespace-nowrap px-3 py-4 text-sm text-gray-500"
                  >
                    {{
                      column.code in matrix_keys
                        ? datapoint.follow_up_state[
                            matrix_keys[column.code][0]
                          ][matrix_keys[column.code][1]][
                            matrix_keys[column.code][2]
                          ].toFixed(4)
                        : datapoint.follow_up_state[column.code].toFixed(4)
                    }}
                  </td>
                  <td
                    v-for="(column, idx) in potential_columns"
                    v-show="!('dynamic' in column)"
                    :class="[
                      idx === 0 ? 'border-l-2' : '',
                      'whitespace-nowrap px-3 py-4 text-sm text-gray-500',
                    ]"
                  >
                    {{ datapoint[column.code] }}
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
import { sort } from "fast-sort";
import {
  ChevronDownIcon,
  ChevronUpIcon,
} from "@heroicons/vue/20/solid/index.js";

export default {
  name: "SamplesTable",
  props: ["data", "run", "potential_function"],
  components: { Pagination, ChevronDownIcon, ChevronUpIcon },
  created() {
    this.update_columns();
  },
  data: () => {
    return {
      table_headers: [
        { code: "id", name: "ID", sortable: false },
        { code: "m", symbol: "m", sortable: true },
      ],
      variable_columns: [],
      potential_columns: [
        {
          name: "Potential",
          code: "potential",
          sortable: true,
        },
        {
          name: "Potential",
          code: "potential_frontend",
          dynamic: true,
          sortable: true,
        },
        { name: "Drift", code: "drift", sortable: true },
        {
          name: "Drift",
          code: "drift_frontend",
          dynamic: true,
          sortable: true,
        },
      ],
      matrix_keys: {},
      current_page: 1,
      items_per_page: 20,
      sort_by: [],
      b: {},
    };
  },
  updated() {
    MathJax.typeset();
  },
  mounted() {
    MathJax.typeset();
  },
  watch: {},
  methods: {
    update_columns() {
      let algorithm = alg_defs.find(
        (e) => e.algorithm === this.run.config.algorithm
      );

      // some after state values are trapped in matrices. We make a dictionary
      // such that the values can be accessed
      this.matrix_keys = {};
      algorithm.matrices.forEach((matrix) => {
        matrix.definition.forEach((e, i) => {
          e.forEach((code, j) => {
            this.matrix_keys[code] = [matrix.name, i, j];
          });
        });
      });

      this.variable_columns = Object.entries(this.run.config.variables).map(
        (e) => algorithm.state_variables.find((e_) => e_.code === e[0])
      );

      this.table_headers.push(
        ...this.variable_columns.map((e) => {
          return {
            symbol: e.symbol,
            code: e.code,
            sortable: true,
          };
        }),
        ...this.potential_columns
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
      console.log(this.sort_by);
      let sort_by = this.sort_by.map(
        function (e) {
          let object = {};
          let matrix_keys = this.matrix_keys;
          let b = [e, matrix_keys];

          object[e.dir] = function (u) {
            u = u.follow_up_state;
            return b[0].code in b[1]
              ? u[b[1][b[0].code][0]][b[1][b[0].code][1]][b[1][b[0].code][2]]
              : u[b[0].code];
          }.bind(this);
          return object;
        }.bind(this)
      );

      let data = sort(this.data.samples).by(sort_by);
      console.log(data);
      return data.filter(
        (e, i) =>
          i >= (this.current_page - 1) * this.items_per_page &&
          i < this.current_page * this.items_per_page
      );
    },
    total_pages() {
      return Math.ceil(this.data.samples.length / this.items_per_page);
    },
  },
};
</script>