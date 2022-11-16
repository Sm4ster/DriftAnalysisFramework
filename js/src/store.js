import { createStore } from "vuex";

export const store = createStore({
  state: {
    eval_potential: false,
    potential_function: "",
  },
  mutations: {
    eval_potential(state, potential_function) {
      state.potential_function = potential_function;
      state.eval_potential = true;
    },
    potential_evaluated(state) {
      state.eval_potential = false;
    },
  },
});
