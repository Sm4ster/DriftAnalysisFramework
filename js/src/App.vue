<template>
  <div>
    <div class="flex h-screen w-screen">
      <Graphic
          :run_id="current_run"
          :target_params="target_params"
          :run_data_updated="run_data_updated"
          @run_selected="current_run = $event"
          @update_received="run_data_updated = false;"
      />

      <Configuration ref="config" class="w-96 h-full overflow-auto hide-scrollbar"
                     @start_run="start_run($event)"
                     @target_changed="target_params=$event"
      />
    </div>
  </div>
</template>

<script>

import Configuration from './components/Configuration.vue'
import Graphic from './components/Graphic.vue'
import {db} from './db.js'

export default {
  name: 'App',
  components: {
    Configuration,
    Graphic
  },
  data: function () {
    return {
      current_run: null,
      target_params: {},
      run_data_updated: false,
    }
  },
  created() {
    this.connect_websocket();
  },

  methods: {
    connect_websocket() {
      // connect to the websocket server for data transmission
      this.connection = new WebSocket("ws://localhost:8000/ws")

      this.connection.onopen = function () {
        console.log("Connection to server established.")
      }

      // reaction to data from the server
      this.connection.onmessage = function ({data}) {
        data = JSON.parse(data);
        if (data.message === "run_started") {
          this.add_run(data.data);
        }
        if (data.message === "locations") {
          this.add_locations(data.data.run_id, data.data.locations);
        }

        if (data.message === "partial_results") {
          console.log(data)
          this.add_data(data.data.run_id, data.data.results);
        }
      }.bind(this)

      this.connection.onclose = function (e) {
        console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
        setTimeout(function () {
          this.connect_websocket();
        }.bind(this), 1000);
      }.bind(this);

      this.connection.onerror = function (err) {
        console.error('Socket encountered error: ', err.message, 'Closing socket');
        this.connection.close();
      }.bind(this);
    },

    start_run(config) {
      this.connection.send(JSON.stringify({
        "message": "start_run",
        "config": config,
      }))
    },

    async add_run(data) {
      await db.runs.add({
        uuid: data.uuid,
        config: data.config,
        name: data.config.name,
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

    async add_data(run_id, results) {
      results.forEach(d => {
        db.locations.update(run_id + "-" + d.id, {
          has_results: true,
          results: d.data,
        });
      });
      // make sure we tell the graphics component to update
      if (this.current_run === run_id) this.run_data_updated = true;
    }
  }
}

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
