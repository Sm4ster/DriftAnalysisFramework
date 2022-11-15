import { createStore } from "vuex";

export const store = createStore({
  state: {
    eval_potential: false,
    potential_function: "",
  },
  mutations: {
    eval_potential(state) {
      state.eval_potential = true;
    },
    potential_evaluated(state) {
      state.eval_potential = false;
    },
  },
});
