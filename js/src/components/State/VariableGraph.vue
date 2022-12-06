<template>
<svg>
  <g>
    <rect x="0" y="0" width="20" height="50" fill="#000fff"></rect>
    <rect x="20" y="0" width="20" height="50" fill="#002ffb"></rect>
    <rect x="40" y="0" width="20" height="50" fill="#001ffd"></rect>
    <rect x="60" y="0" width="20" height="50" fill="#005ffe"></rect>
  </g>
</svg>

</template>

<script>
export default {
  name: "VariableGraph",
  created(){
    // // Construct scales, axes, and formats.
    // const xScale = xType(xDomain, xRange);
    // const yScale = d3.scaleBand(yDomain, yRange).paddingInner(yPadding);
    // const color = d3.scaleOrdinal(zDomain, colors);
    // const xAxis = d3.axisTop(xScale).ticks(width / 80, xFormat);
    // const yAxis = d3.axisLeft(yScale).tickSizeOuter(0);
    //
    //
    // svg.append("g")
    //     .selectAll("g")
    //     .data(series)
    //     .join("g")
    //     .attr("fill", ([{i}]) => color(Z[i]))
    //     .selectAll("rect")
    //     .data(d => d)
    //     .join("rect")
    //     .attr("x", ([x1, x2]) => Math.min(xScale(x1), xScale(x2)))
    //     .attr("y", ({i}) => yScale(Y[i]))
    //     .attr("width", ([x1, x2]) => Math.abs(xScale(x1) - xScale(x2)))
    //     .attr("height", yScale.bandwidth());
  }
}
</script>

<style scoped>

</style>