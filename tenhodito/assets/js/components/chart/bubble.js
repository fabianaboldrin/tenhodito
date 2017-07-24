import $ from 'jquery';
import * as d3 from 'd3';
import { convertEm } from '../../utils/convert';
import mixitup from 'mixitup';


class BubbleChart {
  constructor(selector, width = null, height = null) {
    this.selector = selector;
    this.paddingBottom = convertEm(5, document.querySelector(this.selector));
    if (width) this.width = width;
    else this.width = document.querySelector(this.selector).clientWidth;

    if (height) this.height = height;
    else this.height = document.querySelector(this.selector).clientHeight;

    self.mixer = mixitup('.js-mixer', {
      selectors: {
        target: '.js-mixer-item'
      },
      animation: {
        duration: 100,
        easing: 'cubic-bezier(0.645, 0.045, 0.355, 1)'
      }
    });
  }

  prepareData(data) {
    const maxAmount = d3.max(data.themes, (d) => {return +d.value});
    const aspectRatio = (window.innerHeight / window.innerWidth) * 5;

    const radiusScale = d3.scalePow()
          .exponent(0.6)
          .range([2, 85])
          .domain([0, maxAmount]);

    let prepared = [];
    $.each(data.themes, (idx, data) => {
      prepared.push({
        name: data.name,
        slug: data.slug,
        value: data.value,
        radius: radiusScale((+data.value + 0.5) * aspectRatio),
        x: Math.random() * ( this.width - convertEm(aspectRatio) ),
        y: Math.random() * ( this.height - convertEm(aspectRatio) )
      })
    })
    prepared.sort(function (a, b) { return b.value - a.value; });
    return prepared;
  }

  setup() {
    const center = {x: this.width / 2, y: this.height / 2};
    const forceStrength = 0.03;
    let bubbles = null;
    let texts = null;
    let bubbleInfos = null;
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
        .attr('cx', (d) => { return d.x; })
        .attr('cy', (d) => { return d.y; });
      texts
        .attr('x', (d) => { return d.x - d.radius; })
        .attr('y', (d) => { return d.y - d.radius; })
      bubbleInfos
        .attr('style', (d) => {
          const maxFontSize = 30;
          let fontSize = d.radius * 0.20;
          if (fontSize > maxFontSize) fontSize = maxFontSize;
          return `font-size: ${fontSize}px`; })
    }

    function checkFilter() {
      const container = $('.js-bubble-chart').find('.chart');
      console.log(container)
      const filters = self.mixer.getState().activeFilter.selector;

      if (filters === '.js-mixer-item') {
        container.removeClass('filter-active');
      } else {
        container.addClass('filter-active');
      }
    }

    function handleBubbleClick(data) {
      const currentFilter = self.mixer.getState().activeFilter.selector;
      const svgParent = $(`.bubble__circle.${data.slug}`).parent();

      if (currentFilter.indexOf(`.${data.slug}`) !== -1) {
        self.mixer.toggleOff(`.${data.slug}`).then(checkFilter);
        svgParent.removeClass('active');
      } else {
        self.mixer.toggleOn(`.${data.slug}`).then(checkFilter);
        svgParent.addClass('active');
      }

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

    const path = window.location.pathname;
    let dataUrl = ''
    if (path.endsWith('/')) dataUrl = `${path}data`;
    else dataUrl = `${path}/data`;

    d3.queue()
      .defer(d3.json, dataUrl)
      .await((error, data) => {
        if (error) return console.error(error);
        const preparedData = this.prepareData(data);
        bubbles = svg.selectAll('.buble').data(preparedData);
        const bubbleGroups = bubbles.enter().append('g').attr('class', 'chart__bubbles')
                                    .on('click', (data) => {handleBubbleClick(data)});
        const bubblesE = bubbleGroups.append('circle')
          .attr('class', (d) => { return `bubble__circle ${d.slug}`; })
          .attr('r', 0)

        bubbles = bubbles.merge(bubblesE);
        bubbles.transition()
          .duration(750)
          .attr('r', function (d) { return d.radius; })
          .ease();

        texts = bubbleGroups.append('foreignObject')
          .attr('x', (d) => { return d.x - d.radius })
          .attr('y', (d) => { return d.y - d.radius })
          .attr('width', (d) => { return d.radius * 2 })
          .attr('height', (d) => { return d.radius * 2 })
          .style('opacity', 0)

        bubbleInfos = texts.append('xhtml:div')
          .attr('class', 'bubble__info')
            .append('xhtml:p')
            .attr('class', 'info__name')
            .text((d) => {return d.name;})

        texts.transition()
          .delay(500)
          .duration(1000)
          .style('opacity', 1)

        simulation.nodes(preparedData);
        simulation.force('x', d3.forceX().strength(forceStrength).x(center.x));
        simulation.alpha(1).restart();
      })
  }
}

export default BubbleChart;
