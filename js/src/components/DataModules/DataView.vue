<template>
  <div class="py-10 px-10">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Data Overview</h1>
        <p class="mt-2 text-sm text-gray-700">
          A raw list of all datapoints and their drift.
        </p>
      </div>
    </div>

    <DataTable :data="data"></DataTable>
  </div>
</template>

<script>
import DataTable from "./DataTable.vue";

export default {
  name: "DataView",
  props: ["data"],
  components: { DataTable },
};
</script>

<style scoped></style>
