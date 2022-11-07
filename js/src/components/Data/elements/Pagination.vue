<template>
  <nav class="flex items-center justify-between border-t border-gray-200 px-4">
    <div class="-mt-px flex w-0 flex-1">
      <button
        v-if="current_page > 1"
        @click="current_page -= 1"
        class="inline-flex items-center border-t-2 border-transparent pt-4 pr-1 text-sm font-medium text-gray-500 hover:border-gray-300 hover:text-gray-700"
      >
        <ArrowLongLeftIcon
          class="mr-3 h-5 w-5 text-gray-400"
          aria-hidden="true"
        />
        Previous
      </button>
    </div>
    <div class="hidden md:-mt-px md:flex">
      <button
        v-for="(page, index) in display"
        @click="select_page(page, index)"
        :class="[
          'inline-flex items-center border-t-2 px-4 pt-4 text-sm font-medium',
          page === current_page
            ? 'border-indigo-500 text-indigo-600'
            : ' border-transparent  text-gray-500 hover:border-gray-300 hover:text-gray-700',
        ]"
      >
        <span v-if="page !== '.'">{{ page }}</span>
        <span v-else>...</span>
      </button>
    </div>
    <div class="-mt-px flex w-0 flex-1 justify-end">
      <button
        v-if="current_page < total_pages"
        @click="current_page += 1"
        class="inline-flex items-center border-t-2 border-transparent pt-4 pl-1 text-sm font-medium text-gray-500 hover:border-gray-300 hover:text-gray-700"
      >
        Next
        <ArrowLongRightIcon
          class="ml-3 h-5 w-5 text-gray-400"
          aria-hidden="true"
        />
      </button>
    </div>
  </nav>
</template>

<script>
import { ArrowLongLeftIcon, ArrowLongRightIcon } from "@heroicons/vue/24/solid";

export default {
  name: "Pagination",
  components: { ArrowLongLeftIcon, ArrowLongRightIcon },
  props: ["total_pages"],
  data: () => {
    return {
      display: [1, 2, 3],
      current_page: 1,
    };
  },
  created() {
    this.update_display();
    this.$emit("current_page", this.current_page);
  },
  watch: {
    current_page() {
      this.update_display();
      this.$emit("current_page", this.current_page);
    },
  },
  methods: {
    select_page(page, index) {
      if (page === ".") {
        this.current_page =
          this.display[index - 1] +
          Math.floor((this.display[index + 1] - this.display[index - 1]) / 2);
      } else this.current_page = page;
    },
    update_display() {
      if (this.total_pages < 10) {
        let array = Array.from(Array(this.total_pages).keys());
        this.display = array.map((e) => e + 1);
      } else {
        this.display = [1, 2, 3];

        if (this.current_page < this.total_pages - 1 && this.current_page > 3)
          this.display.push(
            this.current_page - 1,
            this.current_page,
            this.current_page + 1
          );

        this.display.push(
          this.total_pages - 2,
          this.total_pages - 1,
          this.total_pages
        );

        this.display = [...new Set(this.display)];
        this.display.forEach(
          function (e, i) {
            if (e < 4) return;
            if (
              e !== "." &&
              this.display[i - 1] !== "." &&
              e !== this.display[i - 1] + 1
            )
              this.display.splice(i, 0, ".");
          }.bind(this)
        );
      }
    },
  },
};
</script>

<style scoped></style>