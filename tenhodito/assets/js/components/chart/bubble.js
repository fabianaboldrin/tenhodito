import * as d3 from 'd3';
import { convertEm } from '../../utils/convert';


class BubbleChart {
  constructor(selector, width = null, height = null) {
    this.selector = selector;
    console.log(selector)
    this.paddingBottom = convertEm(5, document.querySelector(this.selector));
    if (width) this.width = width;
    else this.width = document.querySelector(this.selector).clientWidth;

    if (height) this.height = height;
    else this.height = document.querySelector(this.selector).clientHeight - this.paddingBottom;

    // this.radiusScale = d3.scalePow()
    //   .exponent(0.5)
    //   .range([2, 85]);

    // this.fillColor = d3.scaleOrdinal()
    //   .domain(['low', 'medium', 'high'])
    //   .range(['#d84b2a', '#beccae', '#7aa25c']);

    this.center = {x: this.width / 2, y: this.height / 2};
  }

  setup() {
    const diameter = 500;

    const bubble = d3.pack()
      .size([diameter, diameter])
      .padding(1.5)

    const svg = d3.select(this.selector)
      .append('svg')
        .attr('width', diameter)
        .attr('height', diameter)
        .attr('class', 'bubble')

    d3.json('/static/state-data.json', (error, data) => {
      console.log(data)
      const bubbles = svg.selectAll('.buble').data(data);
      console.log(bubbles)

    })

    // d3.queue()
    //   .defer(d3.json, '/static/state-data.json')
    //   .await((error, data) => {
    //     if (error) return console.error(error);
    //     console.log(data)
    //     const bubbles = svg.selectAll('.buble').data(data);
    //     console.log(bubbles)
    //     bubbles.enter().append('circle')
    //         .classed('bubble', true)
    //         .attr('r', 0)
    //         .attr('fill', (d) => {console.log(d)})
    //   })
  }
}

export default BubbleChart;
