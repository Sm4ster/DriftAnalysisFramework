<template>
  <Menu as="div" class="relative my-auto inline-block text-left">
    <div class="my-auto">
      <MenuButton
        class="flex items-center rounded-full text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100"
      >
        <span class="sr-only">Open options</span>
        <EllipsisVerticalIcon class="my-auto h-5 w-5" aria-hidden="true" />
      </MenuButton>
    </div>

    <transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <MenuItems
        class="absolute right-4 bottom-4 mt-2 w-56 origin-bottom-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
      >
        <div class="z-50 bg-white py-1">
          <MenuItem>
            <Listbox v-model="selected_scale">
              <ListboxOptions
                static
                as="dl"
                class="mt-1 w-full overflow-auto bg-white py-1 text-base ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm"
              >
                <label class="mx-3 text-xs font-semibold text-indigo-600"
                  >Scale</label
                >
                <ListboxOption
                  as="dd"
                  v-for="_scale in scales"
                  :key="_scale.id"
                  :value="_scale"
                  v-slot="{ selected }"
                >
                  <div
                    class="group relative cursor-pointer select-none py-2 pl-3 pr-9 text-gray-900 hover:bg-gray-100"
                  >
                    <span
                      :class="[
                        selected ? 'font-semibold' : 'font-normal',
                        'block truncate',
                      ]"
                    >
                      {{ _scale.name }}
                    </span>

                    <span
                      v-if="selected"
                      class="absolute inset-y-0 right-0 flex items-center pr-4 text-indigo-600"
                    >
                      <CheckIcon class="h-5 w-5" aria-hidden="true" />
                    </span>
                  </div>
                </ListboxOption>
              </ListboxOptions>
            </Listbox>
          </MenuItem>
          <MenuItem>
            <Listbox v-model="selected_distribution">
              <ListboxOptions
                static
                as="dl"
                class="mt-1 w-full overflow-auto bg-white py-1 text-base ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm"
              >
                <label class="mx-3 text-xs font-semibold text-indigo-600"
                  >Distribution Algorithm</label
                >
                <ListboxOption
                  as="dd"
                  v-for="dist_algo in distribution_algorithms"
                  :key="dist_algo.id"
                  :value="dist_algo"
                  v-slot="{ selected }"
                >
                  <div
                    class="group relative cursor-pointer select-none py-2 pl-3 pr-9 text-gray-900 hover:bg-gray-100"
                  >
                    <span
                      :class="[
                        selected ? 'font-semibold' : 'font-normal',
                        'block truncate',
                      ]"
                    >
                      {{ dist_algo.name }}
                    </span>

                    <span
                      v-if="selected"
                      class="absolute inset-y-0 right-0 flex items-center pr-4 text-indigo-600"
                    >
                      <CheckIcon class="h-5 w-5" aria-hidden="true" />
                    </span>
                  </div>
                </ListboxOption>
              </ListboxOptions>
            </Listbox>
          </MenuItem>
        </div>
      </MenuItems>
    </transition>
  </Menu>
</template>

<script>
import {
  Listbox,
  ListboxOption,
  ListboxOptions,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
} from "@headlessui/vue";
import { CheckIcon, EllipsisVerticalIcon } from "@heroicons/vue/24/solid";
import options from "../../../../../definitions/options/options.json";

export default {
  name: "StateVariableOptions",
  components: {
    Menu,
    MenuButton,
    MenuItem,
    MenuItems,
    EllipsisVerticalIcon,
    ListboxOption,
    ListboxOptions,
    Listbox,
    CheckIcon,
  },
  props: ["init"],
  emits: ["rand_alg", "scale"],
  data: function () {
    return {
      inited: false,
      selected_distribution: null,
      selected_scale: null,
      scales: options.scales,
      distribution_algorithms: options.distributions,
    };
  },
  created() {
    this.selected_scale = options.scales.find((e) => e.id === this.init.scale);
    this.selected_distribution = options.distributions.find(
      (e) => e.id === this.init.distribution
    );

    this.inited = true;
  },
  watch: {
    selected_distribution() {
      if (this.inited) this.$emit("rand_alg", this.selected_distribution);
    },
    selected_scale() {
      if (this.inited) this.$emit("scale", this.selected_scale);
    },
  },
};
</script>