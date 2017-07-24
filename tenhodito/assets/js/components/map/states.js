import $ from 'jquery';
import * as topojson from 'topojson';
import SVGMap from "./svgMap";


class StatesMap extends SVGMap {
  constructor() {
    super('.js-map')
  }

  _setStates(brStates) {
    const currentState = [];
    $.each(brStates.objects.estados.geometries, (idx, state) => {
      if (state.id === STATE) {
        currentState.push(state);
      }
    })
    brStates.objects.estados.geometries = currentState;
    this.states = topojson.feature(brStates, brStates.objects.estados);
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
  }
}

export default StatesMap;
