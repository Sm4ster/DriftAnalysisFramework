<template>
  <div class="space-y-3">
    <div class="relative mb-10">
      <div class="absolute bg-white pr-0.5 pl-0.5  ml-1.5 block text-sm text-indigo-700 font-medium mb-5">Potential
        Function
      </div>
      <div class="h-6 flex w-full flex-col justify-center ">
        <hr>
      </div>
    </div>

    <div class="space-y-4">
      <div
          class="w-full relative border border-gray-300 rounded-md px-3 py-2 shadow-sm focus-within:ring-1 focus-within:ring-indigo-600 focus-within:border-indigo-600">
        <label class="absolute -top-2.5 left-4 -mt-px inline-block px-1 bg-white text-sm font-medium text-gray-900"> $
          V(\theta)$</label>
        <label
            class="absolute -top-2 right-4 -mt-px inline-block px-1 bg-white text-xs font-medium text-gray-900">JS</label>
        <textarea v-model="potential" ref="potential_textbox"
                  class="font-mono py-3 h-48 block w-full border-0 p-0 text-gray-900 placeholder-gray-500 focus:ring-0 focus:outline-0 sm:text-sm appearance-none"/>
      </div>
      <div class="space-y-4">
        <div class="flex flex-row px-2">
          <div class="text-xs space-x-3 flex text-sm">
            <label class="uppercase text-gray-500 mb-3">Usable Variables:</label>
            <div class="font-mono">
              <div>dim</div>
            </div>
          </div>
        </div>
      </div>
<!--      <div class="flex justify-right px-3">-->
<!--        <button @click="expand()" class="text-right font-semibold w-full text-xs text-indigo-700 hover:text-indigo-800">-->
<!--          <span v-if="expanded">Show less</span>-->
<!--          <span v-else >Show more</span>-->
<!--        </button>-->
<!--      </div>-->
    </div>
  </div>
</template>

<script>
export default {
  name: "SamplingOptions",
  data: function () {
    return {
      expanded: false,
      potential: "log(norm(m))",

    }
  },
  mounted() {
    MathJax.typeset()
    this.$nextTick(() => {
      MathJax.typeset()
    })

    this.$refs.potential_textbox.addEventListener('keydown', function (e) {
      if (e.key == 'Tab') {
        e.preventDefault();
        var start = this.selectionStart;
        var end = this.selectionEnd;

        // set textarea value to: text before caret + tab + text after caret
        this.value = this.value.substring(0, start) +
            "  " + this.value.substring(end);

        // put caret at right position again
        this.selectionStart =
            this.selectionEnd = start + 2;
      }
    });
  },


  methods: {
    eval_potential_function(m, sigma, cov_m) {
      const parser = math.parser()

      const scope = {
        "norm_m": math.norm(m),
        "sigma": sigma,
        "cond_cov_m": math.norm(cov_m, 2) * math.norm(math.inv(cov_m), 2)
      }

      return parser.evaluate(this.potential, scope)
    },
    expand() {
      this.expanded = !this.expanded;
      this.$nextTick(() => {
        MathJax.typeset()
      })
    },
    export() {
      return this.potential
    }
  }
}
</script>
