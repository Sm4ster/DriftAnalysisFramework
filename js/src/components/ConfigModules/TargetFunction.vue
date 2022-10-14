<template>
  <div class="space-y-4">
    <div class="relative mb-10">
      <div class="absolute bg-white pr-0.5 pl-0.5  ml-1.5 block text-sm text-indigo-700 font-medium mb-5">Target
        Function
      </div>
      <div class="h-6 flex w-full flex-col justify-center ">
        <hr>
      </div>
    </div>
    <div class="flex justify-between space-x-3">
      <div
          class="relative border border-gray-300 rounded-md px-3 py-2 shadow-sm focus-within:ring-1 focus-within:ring-indigo-600 focus-within:border-indigo-600">
        <label
            class="absolute -top-2 left-2 -mt-px inline-block px-1 bg-white text-xs font-medium text-gray-900">A</label>
        <input type="number" v-model="base.A" step="0.1"
               class="block w-full border-0 p-0 text-gray-900 placeholder-gray-500 focus:ring-0 focus:outline-0 sm:text-sm appearance-none"/>
      </div>

      <div
          class="relative border border-gray-300 rounded-md px-3 py-2 shadow-sm focus-within:ring-1 focus-within:ring-indigo-600 focus-within:border-indigo-600">
        <label
            class="absolute -top-2 left-2 -mt-px inline-block px-1 bg-white text-xs font-medium text-gray-900">B</label>
        <input type="number" v-model="base.B" step="0.1" :max="Math.sqrt(4 * base.A * base.C)"
               class="block w-full border-0 p-0 text-gray-900 placeholder-gray-500 focus:ring-0 focus:outline-0 sm:text-sm appearance-none"/>
      </div>
      <div
          class="relative border border-gray-300 rounded-md px-3 py-2 shadow-sm focus-within:ring-1 focus-within:ring-indigo-600 focus-within:border-indigo-600">
        <label
            class="absolute -top-2 left-2 -mt-px inline-block px-1 bg-white text-xs font-medium text-gray-900">C</label>
        <input type="number" v-model="base.C" step="0.1"
               class="block w-full border-0 p-0 text-gray-900 placeholder-gray-500 focus:ring-0 focus:outline-0 sm:text-sm appearance-none"/>
      </div>
      <div class="flex justify-between space-x-3">
      </div>
    </div>



    <div v-if="expanded" class="space-y-4">
      <div>
        <label class="text-xs uppercase text-gray-500">Explicit form</label>
        <div class="py-3">
          $$ f(x,y) =
          {{ base.A !== 1 ? base.A : "" }}x^2 +
          {{ base.B !== 1 && base.B !== 0 ? base.B : "" }} {{ base.B !== 0 ? "xy +" : "" }}
          {{ base.C !== 1 ? base.C : "" }}y^2 $$
        </div>
      </div>
      <div class="">
        <label class="text-xs uppercase text-gray-500">Matrix form</label>
        <div class="py-3">
          $$
          \begin{pmatrix}
          x & y
          \end{pmatrix}

          \begin{pmatrix}
          {{ base.A }} & {{ 1 / 2 * base.B }} \\
          {{ 1 / 2 * base.B }} & {{ base.C }}
          \end{pmatrix}

          \begin{pmatrix}
          x \\ y
          \end{pmatrix}
          $$
        </div>

      </div>
      <div class="">
        <label class="text-xs uppercase text-gray-500">Inverse Hessian</label>
        <div class="py-3">
          $$
          H_f^{-1} =
          \begin{pmatrix}
          {{ round(inverse_hessian[0][0]) }} & {{ round(inverse_hessian[0][1]) }} \\
          {{ round(inverse_hessian[1][0]) }} & {{ round(inverse_hessian[1][1]) }}
          \end{pmatrix}
          $$
        </div>
        <label class="text-xs uppercase text-gray-500">Eigenvectors and values</label>
        <div class="py-3">
          $$
          \lambda_1 v_1 = {{ round(ih_eigen[0].value) }}
          \begin{pmatrix}
          {{ round(ih_eigen[0].vector[0]) }} \\
          {{ round(ih_eigen[0].vector[1]) }}
          \end{pmatrix}
          $$
        </div>
        <div class="">
          $$
          \lambda_2 v_2 = {{ round(ih_eigen[1].value) }}
          \begin{pmatrix}
          {{ round(ih_eigen[1].vector[0]) }} \\
          {{ round(ih_eigen[1].vector[1]) }}
          \end{pmatrix}
          $$
        </div>
      </div>
    </div>
    <div class="flex justify-right px-3">
      <button @click="expand()" class="text-right font-semibold w-full text-xs text-indigo-700 hover:text-indigo-800">
        <span v-if="expanded">Show less</span>
        <span v-else >Show more</span>
      </button>
    </div>

  </div>
</template>

<script>

import * as math from "mathjs";

export default {
  props: ["init_params"],
  name: "TargetFunction",
  emits: ["param_update"],
  data: function () {

    return {
      init: false,
      expanded: false,
      base: {
        A: null,
        B: null,
        C: null,
      },
    }
  },
  created() {
    this.base.A = this.init_params.A
    this.base.B = this.init_params.B
    this.base.C = this.init_params.C
    this.init = true;
  },
  mounted() {
    MathJax.typeset();
  },
  watch: {
    base: {
      handler() {
        this.$nextTick(() => {
          MathJax.typeset()
        })
        this.$emit("param_update", this.base);
      },
      deep: true
    },
  },
  computed: {
    inverse_hessian() {
      let quadratic_matrix = [
        [this.base.A, 0.5 * this.base.B],
        [0.5 * this.base.B, this.base.C]
      ];

      return math.inv(math.add(quadratic_matrix, math.transpose(quadratic_matrix)));
    },

    ih_eigen() {
      let eigens = math.eigs(this.inverse_hessian)
      let eigen_list = [];
      for (let i = 0; i < eigens.values.length; i++) {
        eigen_list.push({value: eigens.values[i], vector: eigens.vectors[i]})
      }
      return eigen_list;
    },

    theta_deg: {
      set(input) {
        return input
      },
      get() {
        return (180 / Math.PI) * this.canonical.theta;
      }
    }
  },
  methods: {
    expand() {
      this.expanded = !this.expanded;
      this.$nextTick(() => {
        MathJax.typeset()
      })
    },
    round(num) {
      return Math.round(num * 1000) / 1000
    },
    export() {
      return {
        A: this.base.A,
        B: this.base.B,
        C: this.base.C
      }
    }
  }
}
</script>
