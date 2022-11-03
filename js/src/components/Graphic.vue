<template>
  <div ref="wrapper" class="relative h-full w-full">
    <ViewOptions
      class="absolute top-3 right-6 z-40"
      :view="view"
      @view_selected="view = $event"
    />
    <div v-if="view === 'map'" class="relative flex h-full w-full">
      <ContourGraph
        v-if="target_params"
        class="z-10 h-full w-full"
        :viewbox="viewbox"
        :params="target_params"
        @svg="set_svg"
      />

      <DataGraph
        class="absolute z-20 h-full w-full"
        :viewbox="viewbox"
        :data="data"
        :draw="draw"
        @has_drawn="draw = false"
      />
      <EventLayer
        ref="event_component"
        class="absolute z-30 h-full w-full"
        :svg="svg"
        @viewbox="viewbox = $event"
      />
    </div>
    <div v-if="view === 'raw'">
      <DataView :run="run_data" :data="data" />
    </div>
  </div>
</template>

<script>
import EventLayer from "./GraphModules/EventLayer.vue";
import DataOptions from "./GraphModules/DataOptions.vue";
import ContourGraph from "./GraphModules/ContourGraph.vue";
import DataGraph from "./GraphModules/DataGraph.vue";
import ViewOptions from "./GraphModules/ViewOptions.vue";
import DataView from "./DataModules/DataView.vue";
import { db } from "../db";

export default {
  name: "Graphic",
  components: {
    EventLayer,
    DataOptions,
    ContourGraph,
    DataGraph,
    ViewOptions,
    DataView,
  },
  props: ["run_id", "run_data_updated", "target_params", "filters"],
  emits: ["run_selected", "update_received"],
  data() {
    return {
      view: "map", // raw, map

      run_data: [],
      data: [],
      min_drift: 0,

      viewbox: {
        x: 0,
        y: 0,
        width: 250,
        height: 250,
      },

      svg: null,
      draw: null,
    };
  },

  watch: {
    run_id() {
      this.update_data();
      db.runs
        .where({ uuid: this.run_id })
        .first()
        .then((data) => {
          this.run_data = data;
        });
    },
    run_data_updated() {
      this.$emit("update_received");
      this.update_data();
    },
  },

  computed: {
    drift_range() {
      return {
        min: Math.min(...this.data.map((e) => e.drift)),
        max: Math.max(...this.data.map((e) => e.drift)),
      };
    },
  },
  methods: {
    update_data() {
      if (this.run_id) {
        db.locations
          .where({ run_id: this.run_id })
          .toArray()
          .then((data) => {
            this.data = data
              .map((e) => {
                return {
                  ...e,
                  significance: e.results.reduce(
                    (pv, cv) =>
                      pv && (cv.significance.drift || cv.significance.drift),
                    true
                  ),
                  mean_drift:
                    e.results.reduce((pv, cv) => pv + cv.drift, 0) /
                    e.results.length,
                };
              })
              .filter((e) => {
                return true;
              })
              .map((d) => {
                let color = "blue";
                if (!d.has_results) color = "white";
                if (d.mean_drift < this.min_drift) color = "red";
                return {
                  id: d.location_id,
                  states: d.results,
                  location: d.location,
                  color: color,
                  drift: d.mean_drift,
                };
              });
          });
      }
    },

    set_svg(event) {
      this.svg = event;
    },
  },
};
</script>