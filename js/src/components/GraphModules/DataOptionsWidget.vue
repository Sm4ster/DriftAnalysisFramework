<template>

</template>

<script>
import {liveQuery} from "dexie";
import {useObservable} from "@vueuse/rxjs";
import {db} from "../../db.js"

export default {
  name: "DataOptionsWidget",
  props: ['selected_run_id', 'runs', 'drift_range'],
  emits: ['run_selected', 'min_drift'],
  data: function () {
    return {

    }
  },

  watch: {
    min_drift(){
      this.$emit("min_drift");
    }
  },
  methods: {

  }


}
</script>
