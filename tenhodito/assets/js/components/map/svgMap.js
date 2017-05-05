import * as d3 from 'd3';
import * as topojson from 'topojson';
import $ from 'jquery';
import { convertEm } from '../../utils/convert';

class SVGMap {
  constructor(selector, width = null, height = null) {
    this.selector = selector;
    this.paddingBottom = convertEm(5, document.querySelector(this.selector));
    if (width) this.width = width;
    else this.width = document.querySelector(this.selector).clientWidth;

    if (height) this.height = height;
    else this.height = document.querySelector(this.selector).clientHeight - this.paddingBottom;
  }

  setup() {
    d3.queue()
      .defer(d3.json, '/static/br-states.json')
      .await((error, brStates) => {
        if (error) return console.error(error);
        this._setStates(brStates)
        this._createSVG();
        this._drawMap();
      });
  }

  _setStates(brStates) {
    this.states = topojson.feature(brStates, brStates.objects.estados);
  }

  _drawMap() {
    this._svgDropShadow();
    this._svgMapBackground();
    this._svgMap();
  }

  _createSVG() {
    const projection = d3.geoMercator()
        .fitSize([this.width - convertEm(2.5), this.height - convertEm(2.5)], this.states);

    this.path = d3.geoPath()
      .projection(projection);

    this.svg = d3.select(this.selector).append('svg')
        .attr('width', this.width)
        .attr('height', this.height);
  }

  _svgDropShadow() {
    const mapDropshadowFilter = this.svg.append('filter')
      .attr('id', 'mapDropshadow')
      .attr('height', '200%')
      .attr('width', '200%')

    mapDropshadowFilter.append('feGaussianBlur') // stdDeviation is how much to blur
      .attr('in', 'SourceAlpha')
      .attr('stdDeviation', '0')
    mapDropshadowFilter.append('feOffset') // how much to offset
      .attr('dx', '1')
      .attr('dy', '8')
      .attr('result', 'offsetBlur')
    mapDropshadowFilter.append('feFlood')
      .attr('flood-color', '#002926')
      .attr('flood-opacity', '1')
      .attr('operator', 'in')
      .attr('result', 'offsetColor')
    mapDropshadowFilter.append('feComposite')
      .attr('in', 'offsetColor')
      .attr('in2', 'offsetBlur')
      .attr('operator', 'in')
      .attr('result', 'offsetBlur')

    const mapDropshadowFilterMerge = mapDropshadowFilter.append('feMerge')
    mapDropshadowFilterMerge.append('feMergeNode')
    mapDropshadowFilterMerge.append('feMergeNode')
      .attr('in', 'SourceGraphic')
  }

  _svgMapBackground() {
    this.svg.append('g')
        .attr('class', 'map__background')
      .selectAll('path')
        .data(this.states.features)
      .enter().insert('path')
        .attr('class', 'state__path')
        .attr('stroke-alignment', 'outer')
        .attr('d', this.path)
  }
}

export default SVGMap;
