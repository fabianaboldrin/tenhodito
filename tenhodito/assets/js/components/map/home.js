import $ from 'jquery';
import * as d3 from 'd3';
import * as topojson from 'topojson';
import { addClass, removeClass } from '../../utils/polyfills';
import { convertEm } from '../../utils/convert';
import SVGMap from "./svgMap";


class HomeMap extends SVGMap {
  constructor() {
    super('.js-map')
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

  handleStateMouseOver(state) {
    const targetEl = d3.event.target;
    const elementBox = targetEl.getBoundingClientRect();
    const theme = this.data[state.id];
    const viewportWidth = document.documentElement.clientWidth;
    const top = elementBox.top + (elementBox.height / 2) - (this.mapTooltip.clientHeight / 2);
    this.mapTooltipTheme.innerText = theme.theme;

    let left = elementBox.left + (elementBox.width + convertEm(1.5));
    if (viewportWidth - this.mapTooltip.offsetWidth - left < 100 ) {
      left = elementBox.left - (this.mapTooltip.offsetWidth + convertEm(4.5));
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

  handleStateClick(state) {
    window.location.href = Urls.state(state.id);
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
        .on('click', (data) => {this.handleStateClick(data)});
  }
}

export {
  HomeMap
}
