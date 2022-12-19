<template>
  <div class="space-y-3">
    <div v-if="header" class="relative mb-10">
      <div
        class="absolute ml-1.5 mb-5 block bg-white pr-0.5 pl-0.5 text-sm font-medium text-indigo-700"
      >
        Potential Function
      </div>
      <div class="flex h-6 w-full flex-col justify-center">
        <hr />
      </div>
    </div>

    <div class="space-y-4">
      <div
        class="relative w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus-within:border-indigo-600 focus-within:ring-1 focus-within:ring-indigo-600"
      >
        <label
          class="absolute -top-2.5 left-4 -mt-px inline-block bg-white px-1 text-sm font-medium text-gray-900"
        >
          $ V(\theta)$</label
        >
        <label
          class="absolute -top-2 right-4 -mt-px inline-block bg-white px-1 text-xs font-medium text-gray-900"
          >JS</label
        >
        <textarea
          v-model="potential"
          ref="potential_textbox"
          class="block h-48 w-full appearance-none border-0 p-0 py-3 font-mono text-gray-900 placeholder-gray-500 focus:outline-0 focus:ring-0 sm:text-sm"
        />
      </div>
      <div class="space-y-4">
        <div class="flex flex-row px-2">
          <div class="flex space-x-3 text-xs text-sm">
            <label class="mb-3 uppercase text-gray-500"
              >Usable Variables:</label
            >
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
  name: "PotentialFunction",
  props: {
    header: {
      type: Boolean,
      default: true,
    },
  },
  data: function () {
    return {
      expanded: false,
      potential: "log(norm(m))",
    };
  },
  mounted() {
    MathJax.typeset();
    this.$nextTick(() => {
      MathJax.typeset();
    });

    this.$refs.potential_textbox.addEventListener("keydown", function (e) {
      if (e.key == "Tab") {
        e.preventDefault();
        var start = this.selectionStart;
        var end = this.selectionEnd;

        // set textarea value to: text before caret + tab + text after caret
        this.value =
          this.value.substring(0, start) + "  " + this.value.substring(end);

        // put caret at right position again
        this.selectionStart = this.selectionEnd = start + 2;
      }
    });
  },
  methods: {
    expand() {
      this.expanded = !this.expanded;
      this.$nextTick(() => {
        MathJax.typeset();
      });
    },
    export() {

      return this.potential.replace(/\r?\n|\r/g, " ");
    },
  },
};
</script>