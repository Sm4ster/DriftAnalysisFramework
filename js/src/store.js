import {createStore} from "vuex";
import {db} from "./db.js";

export const store = createStore({
    state: {
        websocket_connection: null,

        runs: [],
        selected_run_id: null,

        locations: [],
        sorted_locations_ids: [],
        location_filters: [],

        mode: "overview", // overview, run, new
        eval_potential: false,
        potential_function: "",
    },
    getters: {
        selected_run_data(state) {
            return state.runs[state.runs.findIndex(e => e.uuid === state.selected_run_id)]
        },
        locations_filtered(state, filters){
            let filtered_data = data.filter((d) => {
                            return (
                                d.location[0] > this.filters.location[0].min &&
                                d.location[1] > this.filters.location[1].min &&
                                d.location[0] < this.filters.location[0].max &&
                                d.location[1] < this.filters.location[1].max
                            );
                          });
        }
    },
    mutations: {
        update_websocket_connection(state, connection) {
            state.websocket_connection = connection;
        },
        eval_potential(state, potential_function) {
            state.potential_function = potential_function;
            state.eval_potential = true;
        },
        potential_evaluated(state) {
            state.eval_potential = false;
        },
        load_runs(state, data) {
            console.log(data)
            state.runs = data;
        },
        select_run(state, {run_id, locations}) {
            console.log("I am selecting")
            state.locations = locations
            state.selected_run_id = run_id;
            state.mode = "run"
        },
        change_mode(state, mode){
            state.mode = mode
        }
    },

    actions: {
        init({commit}) {
            // load stored runs into memory
            db.runs.toArray()
                .then((data) => {
                    commit("load_runs", data)
                })

        },
        select_run({commit}, run_id) {
            console.log("Start loading location data from database")
            db.locations
                .where({run_id: run_id})
                .toArray()
                .then((locations) => {
                    commit("select_run", {run_id: run_id, locations: locations});
                    console.log("Finished loading location data from database")
                })
        },
    },
});
