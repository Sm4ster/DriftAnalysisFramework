<template>
  <div
    class="flex rounded-lg border-2 border bg-gray-300 bg-opacity-50 text-white"
  >
    <div v-for="view_ in views">
      <button
        :class="[
          view === view_.id ? 'bg-white bg-opacity-60 text-indigo-600' : '',
          'rounded px-3 py-2',
        ]"
        @click="select_view(view_.id)"
      >
        {{ view_.name }}
      </button>
    </div>
  </div>
</template>

<script>
const views = [
  { id: "map", name: "Map" },
  { id: "state", name: "State" },
  { id: "raw", name: "Data" },
];

export default {
  name: "ViewOptions",

  props: ["view"],
  emits: ["view_selected"],
  data: function () {
    return {
      views: views,
    };
  },
  created() {},
  mounted() {},

  watch: {},
  computed: {},
  methods: {
    select_view(view) {
      this.$emit("view_selected", view);
    },
  },
};
</script>