import { createStore } from "vuex";
import { db } from "./db.js";

export const store = createStore({
  state: {
    websocket_connection: null,

    eval_potential: false,
    potential_function: "",

    selected_run: null,
  },
  mutations: {
    update_websocket_connection(state, connection){
      state.websocket_connection = connection;
    },
    eval_potential(state, potential_function) {
      state.potential_function = potential_function;
      state.eval_potential = true;
    },
    potential_evaluated(state) {
      state.eval_potential = false;
    },
    select_run(state, run_data) {
      state.selected_run = run_data;
    },
  },

  actions: {
    select_run({ commit }, run_id) {
      db.runs
        .where({ uuid: run_id })
        .first()
        .then((data) => {
          commit("select_run", data);
        })
        .catch(() => {
          console.error("Could not fetch the data from the database!");
        });
    },
  },
});
