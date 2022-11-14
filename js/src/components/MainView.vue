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
        :potential_function="potential_function"
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
      <DataView
        :run="run_data"
        :data="data"
        :potential_function="potential_function"
      />
    </div>
  </div>
</template>

<script>
import EventLayer from "./Graph/EventLayer.vue";
import DataOptions from "./Graph/DataOptions.vue";
import ContourGraph from "./Graph/ContourGraph.vue";
import DataGraph from "./Graph/DataGraph.vue";
import ViewOptions from "./Graph/ViewOptions.vue";
import DataView from "./Data/DataView.vue";
import { db } from "../db";

export default {
  name: "MainView",
  components: {
    EventLayer,
    DataOptions,
    ContourGraph,
    DataGraph,
    ViewOptions,
    DataView,
  },
  props: [
    "run_id",
    "run_data_updated",
    "target_params",
    "filters",
    "potential_function",
    "apply_filters",
    "init_filters",
  ],
  emits: [
    "run_selected",
    "update_received",
    "filters_applied",
    "filters_inited",
  ],
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

      flags: {
        run_id: false,
        filters: false,
      },
    };
  },

  watch: {
    run_id() {
      if (this.run_id) {
        db.runs
          .where({ uuid: this.run_id })
          .first()
          .then((data) => {
            this.run_data = data;
          });
      } else {
        this.run_data = [];
        this.data = [];
      }
    },
    run_data_updated() {
      this.$emit("update_received");
      this.update_data().then((result) => {
        this.data = result;
      });
    },
    apply_filters: function () {
      this.update_data().then((result) => {
        this.data = result;
        this.$emit("filters_applied");
      });
    },
    init_filters() {
      this.update_data().then((result) => {
        this.data = result;
        this.$emit("filters_inited");
      });
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
      if (this.filters && this.run_id) {
        return db.locations
          .where({ run_id: this.run_id })
          .toArray()
          .then((data) => {
            let filtered_data = data.filter((d) => {
              return (
                d.location[0] > this.filters.location[0].min &&
                d.location[1] > this.filters.location[1].min &&
                d.location[0] < this.filters.location[0].max &&
                d.location[1] < this.filters.location[1].max
              );
            });

            return filtered_data
              .map((e) => {
                return {
                  ...e,
                  significance: e.results
                    ? e.results.reduce(
                        (pv, cv) =>
                          pv &&
                          (cv.significance.drift || cv.significance.drift),
                        true
                      )
                    : undefined,
                  mean_drift: e.results
                    ? e.results.reduce((pv, cv) => pv + cv.drift, 0) /
                      e.results.length
                    : undefined,
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
                  states: d.results.filter((state) => {
                    return Object.entries(this.filters.variables).every(
                      ([code, filter]) => {
                        return (
                          state.state[code] > filter.min &&
                          state.state[code] < filter.max
                        );
                      }
                    );
                  }),
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