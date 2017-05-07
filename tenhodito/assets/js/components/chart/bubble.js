import $ from 'jquery';
import * as d3 from 'd3';
import { convertEm } from '../../utils/convert';


class BubbleChart {
  constructor(selector, width = null, height = null) {
    this.selector = selector;
    this.paddingBottom = convertEm(5, document.querySelector(this.selector));
    if (width) this.width = width;
    else this.width = document.querySelector(this.selector).clientWidth;

    if (height) this.height = height;
    else this.height = document.querySelector(this.selector).clientHeight - this.paddingBottom;

  }

  prepareData(data) {
    const maxAmount = d3.max(data.themes, (d) => {return +d.value});

    const radiusScale = d3.scalePow()
          .exponent(0.5)
          .range([2, 85])
          .domain([0, maxAmount]);

    let prepared = [];
    $.each(data.themes, (idx, data) => {
      prepared.push({
        name: data.name,
        slug: data.slug,
        value: data.value,
        radius: radiusScale(+data.value),
        x: Math.random() * ( this.width - convertEm(5) ),
        y: Math.random() * ( this.height - convertEm(5) )
      })
    })
    prepared.sort(function (a, b) { return b.value - a.value; });
    return prepared;
  }

  setup() {
    const center = {x: this.width / 2, y: this.height / 2};
    const forceStrength = 0.03;
    let bubbles = null;
    function charge(d) {
      return -Math.pow(d.radius, 2.0) * forceStrength;
    }

    function collide(d) {
      return d.radius + 1;
    }

    const simulation = d3.forceSimulation()
      .velocityDecay(0.2)
      .force('x', d3.forceX().strength(forceStrength).x(center.x))
      .force('y', d3.forceY().strength(forceStrength).y(center.y))
      .force('charge', d3.forceManyBody().strength(charge))
      .force("collide", d3.forceCollide().radius(collide).iterations(2))
      .on('tick', ticked);
    simulation.stop();

    function ticked() {
      bubbles
        .attr('cx', function (d) { return d.x; })
        .attr('cy', function (d) { return d.y; });
    }

    const diameter = 500;

    const bubble = d3.pack()
      .size([diameter, diameter])
      .padding(1.5)

    const svg = d3.select(this.selector)
      .append('svg')
        .attr('width', this.width)
        .attr('height', this.height)
        .attr('class', 'chart')

    d3.queue()
      .defer(d3.json, '/static/state-data.json')
      .await((error, data) => {
        if (error) return console.error(error);
        const preparedData = this.prepareData(data);
        bubbles = svg.selectAll('.buble').data(preparedData);
        const bubblesE = bubbles.enter().append('circle')
          .attr('r', 0)
          .attr('class', (d) => { return `chart__bubble ${d.slug}`; })

        bubbles = bubbles.merge(bubblesE);
        bubbles.transition()
          .duration(1000)
          .attr('r', function (d) { return d.radius; });
        simulation.nodes(preparedData);
        simulation.force('x', d3.forceX().strength(forceStrength).x(center.x));
        simulation.alpha(1).restart();
      })
  }
}

export default BubbleChart;
