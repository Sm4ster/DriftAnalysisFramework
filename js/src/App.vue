<template>
  <div>
    <div class="flex h-screen w-screen">
      <MainView
          :run_id="current_run"
          :target_params="target_params"
          :run_data_updated="run_data_updated"
          :filters="filters"
          :potential_function="potential_function"
          :apply_filters="apply_filters"
          :init_filters="init_filters"
          @filters_applied="apply_filters = false"
          @filters_inited="init_filters = false"
          @update_received="run_data_updated = false"
      />

      <SideBar
          ref="config"
          class="hide-scrollbar h-full w-96 overflow-auto"
          :run_id="current_run"
          @apply_filters="
          $event.init ? (init_filters = true) : (apply_filters = true)
        "
          @filters="filters = $event"
          @run_selected="current_run = $event"
          @start_run="start_run($event)"
          @target_changed="target_params = $event"
          @eval_potential="potential_function = $event"
      />

      <Settings/>
    </div>
  </div>
</template>

<script>
import SideBar from "./components/Sidebar.vue";
import MainView from "./components/MainView.vue";
import Settings from "./components/Settings/Settings.vue";
import {db} from "./db.js";

export default {
  name: "App",
  components: {
    SideBar,
    MainView,
    Settings,
  },
  data: function () {
    return {
      current_run: null,
      apply_filters: false,
      init_filters: false,
      filters: null,
      target_params: {},
      run_data_updated: false,
      potential_function: "",
    };
  },
  created() {
    this.connect_websocket();
  },

  methods: {
    connect_websocket() {
      // connect to the websocket server for data transmission
      let connection = new WebSocket("ws://localhost:8000/ws");
      this.connection = connection;

      this.$store.commit("update_websocket_connection", connection)

      this.connection.onopen = function () {
        db.runs.toArray().then((data) => {
          this.$store.state.websocket_connection.send(JSON.stringify(
              {
                message: "open_runs",
                data: data.filter(e => !("finished_at" in e)).map(e => e.uuid)
              }
          ))
        })
      }.bind(this);

      // reaction to data from the server
      this.connection.onmessage = function ({data}) {
        data = JSON.parse(data);
        if (data.message === "pong") {
          console.log("pong");
        }
        if (data.message === "run_started") {
          this.add_run(data.data);
        }
        if (data.message === "run_finished") {
          this.finish_run(data.data).then(() => {
            this.$store.state.websocket_connection.send(JSON.stringify(
                {
                  message: "run_finished",
                  data: {
                    uuid: data.data.uuid
                  }
                }
            ))
          });
        }
        if (data.message === "locations") {
          this.add_locations(data.data.run_id, data.data.locations);
          this.add_min_max(data.data.run_id, data.data.min_max);
          // this.current_run = data.data.run_id;
        }
        if (data.message === "partial_results") {
          this.add_data(data.data.run_id, data.data.results).then(
              (e) => {
                this.$store.state.websocket_connection.send(JSON.stringify(
                    {
                      message: "results_received",
                      data: {
                        run_id: data.data.run_id,
                        location_ids: data.data.results.map(e => e.id)
                      }
                    }
                ))
              }
          );
        }
      }.bind(this);

      this.connection.onclose = function (e) {
        console.log(
            "Socket is closed. Reconnect will be attempted in 1 second.",
            e.reason
        );
        setTimeout(
            function () {
              this.connect_websocket();
            }.bind(this),
            1000
        );
      }.bind(this);

      this.connection.onerror = function (err) {
        console.error(
            "Socket encountered error: ",
            err.message,
            "Closing socket"
        );
        this.connection.close();
      }.bind(this);
    },

    start_run(config) {
      this.connection.send(
          JSON.stringify({
            message: "start_run",
            config: config,
          })
      );
    },

    async add_run(data) {
      await db.runs.add({
        uuid: data.uuid,
        config: data.config,
        name: data.config.name,
        started_at: data.started_at,
      });
    },

    async finish_run(data) {
      return db.runs.update(data.uuid, {
        finished_at: data.finished_at,
      });
    },

    async add_locations(run_id, locations) {
      locations.forEach((d, i) => {
        db.locations.add({
          uuid: run_id + "-" + d.id,
          run_id: run_id,
          location_id: d.id,
          location: d.location,
          has_results: false,
        });
      });
    },

    async add_min_max(run_id, min_max) {
      db.runs.update(run_id, {
        min_max: min_max,
      });
    },

    async add_data(run_id, results) {
      results.forEach((d) => {
        db.locations.update(run_id + "-" + d.id, {
          has_results: true,
          results: d.data,
        });
      });
    },
  },
};
</script>

<style>
/* Hide scrollbar for Chrome, Safari and Opera */
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}

/* Hide scrollbar for IE, Edge and Firefox */
.hide-scrollbar {
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
}
</style>