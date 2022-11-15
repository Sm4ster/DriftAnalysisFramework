import { createApp } from "vue";
import App from "./App.vue";
import "./index.css";

import CMA_ES from "../../definitions/algorithms/CMA-ES.json";
import OnePlusOne_ES from "../../definitions/algorithms/1+1-ES.json";

window.alg_defs = [CMA_ES, OnePlusOne_ES];

import { store } from "./store.js";

createApp(App).use(store).mount("#app");
