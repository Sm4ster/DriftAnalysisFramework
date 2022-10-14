<template>


  <svg ref="svg" width="100%" height="100%" preserveAspectRatio="xMidYMid slice"
       :viewBox="`${viewbox.x} ${viewbox.y} ${viewbox.width} ${viewbox.height}`">
    <defs>
      <marker id="arrowhead" markerWidth="10" markerHeight="7"
              refX="0" refY="3.5" orient="auto">
        <polygon points="0 0, 10 3.5, 0 7"/>
      </marker>
    </defs>
    <g v-if="Object.keys(params).length > 0" :transform="transformation_matrix">
      <circle v-for="radius in circle_array"
              cx="0" cy="0"
              :r="radius"
              stroke="#fff" stroke-width="0.5"
              :fill="color(radius * radius)"/>
    </g>

    <g v-if="Object.keys(params).length > 0">
      <circle cx="0" cy="0" r="0.8"></circle>
      <foreignObject
          :x="sign(2) *((ih_eigen[0].value * min_radius * ih_eigen[0].vector[0])/2 + ih_eigen[0].value * min_radius)"
          y="-26" width="40"
          height="25" :transform="'rotate('+ rotation_angle +') rotate(90) scale(0.33)'">$ \lambda_2 v_2 $
      </foreignObject>
      <line x1="0" y1="0" :x2="ih_eigen[0].value * min_radius * ih_eigen[0].vector[0]"
            :y2="ih_eigen[0].value * min_radius * ih_eigen[0].vector[1]" stroke="black" stroke-width="0.5"
            marker-end="url(#arrowhead)"></line>

      <foreignObject
          :x="sign(1) * ((ih_eigen[1].value * min_radius * ih_eigen[1].vector[0])/2 + ih_eigen[1].value * min_radius)"
          y="-26" width="40" height="25"
          :transform="'rotate('+ rotation_angle +') scale(0.33)'">$ \lambda_1 v_1 $
      </foreignObject>
      <line x1="0" y1="0" :x2="(ih_eigen[1].value * min_radius *ih_eigen[1].vector[0])"
            :y2="(ih_eigen[1].value * min_radius * ih_eigen[1].vector[1])" stroke="black" stroke-width="0.5"
            marker-end="url(#arrowhead)"></line>
    </g>
  </svg>


</template>

<script>
import * as d3 from "d3";
import * as math from 'mathjs'
import DataOptions from "./DataOptions.vue";

export default {
  components: {
    DataOptions
  },
  emits: ["svg"],
  props: ["params", "viewbox"],
  data: () => {
    return {
      color: d3.scaleSequential(d3.extent(d3.range(0, 500000)), d3.interpolateCool),
      color2: d3.scaleSequential(d3.extent(d3.range(0, 58000)), d3.interpolateCool),
      number_circles: 35,
      min_radius: 80,
      max_radius: 800,

      isPointerDown: false,
      pointerOrigin: null,


    }
  },

  mounted() {
    this.$emit("svg", this.$refs["svg"])
    MathJax.typeset();
  },

  watch: {
    zoom_factor(value) {
      this.render_axis();
    },
  },

  computed: {
    circle_array() {
      return d3.range(this.max_radius, this.min_radius, -((this.max_radius - this.min_radius) / this.number_circles))
    },
    x() {
      return d3.scaleLinear([-25, 25], [0, this.height])
    },
    y() {
      return d3.scaleLinear([-25, 25], [this.height, 0])
    },
    theta() {
      return Math.atan(this.params.B / (this.params.A - this.params.C)) / 2
    },

    eigenvalues() {
      let eigs = this.ih_eigen;

      let e0_0 = eigs[1].value * eigs[1].vector[0];
      let e0_1 = eigs[1].value * eigs[1].vector[1];
      let e1_0 = eigs[0].value * eigs[0].vector[0];
      let e1_1 = eigs[0].value * eigs[0].vector[1];

      return {"e0_0": e0_0, "e0_1": e0_1, "e1_0": e1_0, "e1_1": e1_1};
    },

    transformation_matrix() {
      let e = this.eigenvalues;

      if (this.params.A <= this.params.C) return `matrix(${e.e0_0} ${e.e0_1} ${e.e1_0} ${e.e1_1} 0 0)`
      if (this.params.A > this.params.C) return `matrix(${e.e1_0} ${e.e1_1} ${e.e0_0} ${e.e0_1} 0 0)`
    },

    rotation_angle() {
      let e = this.eigenvalues;
      if (this.params.A >= this.params.C) return Math.atan2(-e.e1_0, e.e1_1) * 180 / Math.PI;
      return -Math.atan2(e.e1_0, e.e1_1) * 180 / Math.PI;
    },

    ih_eigen() {
      let quadratic_matrix = [
        [this.params.A, 0.5 * this.params.B],
        [0.5 * this.params.B, this.params.C]
      ];

      let eigens = math.eigs(math.inv(math.add(quadratic_matrix, math.transpose(quadratic_matrix))));

      let eigen_list = [];
      for (let i = 0; i < eigens.values.length; i++) {
        eigen_list.push({value: eigens.values[i], vector: eigens.vectors[i]})
      }

      return eigen_list;
    },

  },
  methods: {
    sign(e) {

      if(this.params.B === 0){
        if (this.params.A === this.params.C) {
          if (this.params.A < 0)  return e === 1 ? 1.5 : -0.75 // done
          if (this.params.A > 0)  return e === 1 ? -1.75 : 0.75 // done
        }

        if (this.params.A > this.params.C) {
          if (Math.abs(this.params.A) === Math.abs(this.params.C)) return e === 1 ? -1.25 : 1 // done
          if (Math.abs(this.params.A) < Math.abs(this.params.C)) return e === 1 ? -0.75 : -1 // done
          if (Math.abs(this.params.A) > Math.abs(this.params.C)) return e === 1 ? -1.75 : 0.75 // done
        }

        if (this.params.A < this.params.C) {
          if (Math.abs(this.params.A) === Math.abs(this.params.C)) return e === 1 ? 1 : -0.75 // done
          if (Math.abs(this.params.A) < Math.abs(this.params.C)) return e === 1 ? 0.75 : 1 // done
          if (Math.abs(this.params.A) > Math.abs(this.params.C)) return e === 1 ? 1 : -0.75 // done
        }
      }
      if(this.params.B < 0){
        if (this.params.A === this.params.C) {
          if (this.params.A < 0)  return e === 1 ? -1 : -1 // done
          if (this.params.A > 0)  return e === 1 ? -2.5 : 0.75 // done
        }

        if (this.params.A > this.params.C) {
          if (Math.abs(this.params.A) === Math.abs(this.params.C)) return e === 1 ? -1.25 : 0.75 // done
          if (Math.abs(this.params.A) < Math.abs(this.params.C)) return e === 1 ? -1 : -1 // done
          if (Math.abs(this.params.A) > Math.abs(this.params.C)) return e === 1 ? -1 : 1
        }

        if (this.params.A < this.params.C) {
          if (Math.abs(this.params.A) === Math.abs(this.params.C)) return e === 1 ? 1 : -1 // done
          if (Math.abs(this.params.A) < Math.abs(this.params.C)) return e === 1 ? 1 : 1 // done
          if (Math.abs(this.params.A) > Math.abs(this.params.C)) return e === 1 ? 1 : -0.75 // done
        }

      }
      if(this.params.B > 0){
        if (this.params.A === this.params.C) {
          if (this.params.A < 0)  return e === 1 ? 1.5 : -0.75 // done
          if (this.params.A > 0)  return e === 1 ? 1 : 1 // done
        }

        if (this.params.A > this.params.C) {
          if (Math.abs(this.params.A) === Math.abs(this.params.C)) return e === 1 ? 1.25 : 1 // done
          if (Math.abs(this.params.A) < Math.abs(this.params.C)) return e === 1 ? -1 : -1.5 // done
          if (Math.abs(this.params.A) > Math.abs(this.params.C)) return e === 1 ? -1.5 : 1 // done
        }

        if (this.params.A < this.params.C) {
          if (Math.abs(this.params.A) === Math.abs(this.params.C)) return e === 1 ? 1 : -0.75 // done
          if (Math.abs(this.params.A) < Math.abs(this.params.C)) return e === 1 ? 1 : 1 // done
          if (Math.abs(this.params.A) > Math.abs(this.params.C)) return e === 1 ? 1 : -0.75 // done
        }
      }
    },

    target(x, y) {
      return this.params.A * x * x + x * y * this.params.B + y * y * this.params.C;
    },


    value(x, y) {
      // let rotated_vector = math.multiply([x,y], rotation_matrix);
      let base_vector = [x, y]
      let intermediate = math.multiply(math.transpose(base_vector), this.quadratic_matrix);
      return math.multiply(intermediate, base_vector)
      // return math.norm([rotated_vector[0]/params.a,rotated_vector[1]/params.b]);
    },

    render_axis() {
      const svg = d3.select(this.$refs["svg"])
      svg.select("g.xaxis")
          .attr("transform", `translate(${this.x_bias},${(parseInt(this.base_zoom) * this.zoom_factor) + parseInt(this.x_bias)})`)
          .call(d3.axisTop(this.x).ticks(this.zoom / this.zoom * 10))
          .call(g => g.select(".domain").remove())
          .call(g => g.selectAll(".tick").filter(d => this.x.domain().includes(d)).remove())

      svg.select("g.yaxis")
          .attr("transform", "translate(-1,0)")
          .call(d3.axisRight(this.y))
          .call(g => g.select(".domain").remove())
          .call(g => g.selectAll(".tick").filter(d => this.y.domain().includes(d)).remove())
    },
  }
}
</script>

