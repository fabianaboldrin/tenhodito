import * as d3 from 'd3';
import * as topojson from 'topojson';
import { addClass, removeClass } from '../../utils/polyfills';
import { convertEm } from '../../utils/convert';


class HomeMap {
  constructor() {
    this.paddingBottom = convertEm(5, document.querySelector(this.selector));
    this.width = document.querySelector('.js-map').clientWidth;
    this.height = Math.max(document.documentElement.clientHeight, window.innerHeight || 0) - this.paddingBottom;
    this.selector = '.js-map';
    this.data = this.getData();
  }

  get mapTooltip() {
    return document.querySelector('.js-map-tooltip');
  }

  get mapTooltipIcon() {
    return this.mapTooltip.querySelector('.js-tooltip-icon');
  }

  get mapTooltipTheme() {
    return this.mapTooltip.querySelector('.js-tooltip-theme');
  }

  getData() {
    $.ajaxSetup({async: false});
    const response = $.getJSON('/static/home-data.json', (data) => {
      $.ajaxSetup({async: true});
      return data;
    })
    return response.responseJSON;
  }

  setup() {
    d3.queue()
      .defer(d3.json, '/static/br-states.json')
      .await((error, brStates) => {
        if (error) return console.error(error);
        this._createSVG(brStates);
        this._drawMap();
      });
  }

  handleStateMouseOver(state) {
    const targetEl = d3.event.target;
    const elementBox = targetEl.getBoundingClientRect();
    const theme = this.data[state.id];
    const viewportWidth = document.documentElement.clientWidth;
    const top = elementBox.top + (elementBox.height / 2) - (this.mapTooltip.clientHeight / 2);
    this.mapTooltipTheme.innerText = theme.theme;

    let left = elementBox.left + (elementBox.width + convertEm(1.5));
    if (viewportWidth - this.mapTooltip.offsetWidth - left < 100 ) {
      left = elementBox.left - (this.mapTooltip.offsetWidth + convertEm(1.5));
      addClass(this.mapTooltip, 'left');
    }

    this.mapTooltip.style.left = `${left}px`;
    this.mapTooltip.style.top = `${top}px`;
    addClass(this.mapTooltip, 'is-visible');
    addClass(this.mapTooltipIcon, `icon-${theme.slug}`);
    addClass(this.mapTooltipIcon, theme.slug);
    addClass(targetEl, theme.slug);
  }

  handleStateMouseOut(state) {
    const targetEl = d3.event.target;
    const theme = this.data[state.id];
    removeClass(this.mapTooltip, 'is-visible');
    removeClass(this.mapTooltip, 'left');
    removeClass(targetEl, theme.slug);
    removeClass(this.mapTooltipIcon, theme.slug);
    removeClass(this.mapTooltipIcon, `icon-${theme.slug}`);
  }

  _createSVG(brStates) {
    this.states = topojson.feature(brStates, brStates.objects.estados);
    const projection = d3.geoMercator()
        .fitSize([this.width - convertEm(2.5), this.height - convertEm(2.5)], this.states);

    this.path = d3.geoPath()
      .projection(projection);

    this.svg = d3.select(this.selector).append('svg')
        .attr('width', this.width)
        .attr('height', this.height);
  }

  _drawMap() {
    this._svgDropShadow();
    this._svgMapBackground();
    this._svgMap();
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

  _svgMap() {
    this.svg.append('g')
        .attr('class', 'map__states')
        .attr('style', `filter:url(#mapDropshadow)`)
      .selectAll('path')
        .data(this.states.features)
      .enter().insert('path')
        .attr('class', 'state__path')
        .attr('d', this.path)
        .on('mouseover', (data) => {this.handleStateMouseOver(data)})
        .on('mouseout', (data) => {this.handleStateMouseOut(data)})
        .on('click', console.log('ois'));
  }
}

export {
  HomeMap
}
