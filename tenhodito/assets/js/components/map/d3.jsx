import * as d3 from 'd3';
import * as topojson from 'topojson';
import { addClass, removeClass } from '../../utils/polyfills'
import { convertEm } from '../../utils/convert'

function d3Init() {
  const paddingBottom = convertEm(2, document.querySelector('.js-map'));
  console.log(paddingBottom);
  const map = {
    width: 750,
    height: Math.max(document.documentElement.clientHeight, window.innerHeight || 0) - paddingBottom,
    selector: '.map',
  }

  const fakeData = {
    'RIO GRANDE DO SUL': {
      slug: 'seguranca',
      theme: 'Segurança'
    },
    'RIO DE JANEIRO': {
      slug: 'economia',
      theme: 'Economia'
    },
    'MINAS GERAIS': {
      slug: 'educacao',
      theme: 'Educação'
    },
    'SANTA CATARINA': {
      slug: 'educacao',
      theme: 'Educação'
    },
    'PARANÁ': {
      slug: 'economia',
      theme: 'Economia'
    },
    'SÃO PAULO': {
      slug: 'seguranca',
      theme: 'Segurança'
    }
  }

  const infoCardEl = document.querySelector('.js-map-info-card');
  const infoCard = {
    element: infoCardEl,
    regionInfo: infoCardEl.querySelector('.info-card__region-info'),
    infoState: infoCardEl.querySelector('.info-card__region-info > .region-info__state'),
    infoRegion: infoCardEl.querySelector('.info-card__region-info > .region-info__region'),
    themeInfo: infoCardEl.querySelector('.info-card__theme-info'),
    themeIcon: infoCardEl.querySelector('.info-card__theme-info > .theme-info__icon'),
    themeTitle: infoCardEl.querySelector('.info-card__theme-info > .theme-info__title'),
  }
  console.log(infoCard);

  function mapLoaded(error, br_states) {
    if (error) return console.error(error);

    const states = topojson.feature(br_states, br_states.objects.states);

    const projection = d3.geoMercator()
        .fitSize([map.width, map.height], states);

    const path = d3.geoPath()
      .projection(projection);

    const svg = d3.select(map.selector).append('svg')
        .attr('width', map.width)
        .attr('height', map.height);
    const dropshadowFilter = svg.append('filter')
      .attr('id', 'dropshadow')
      .attr('height', '100%')

    dropshadowFilter.append('feGaussianBlur')
      .attr('in', 'SourceAlpha')
      .attr('stdDeviation', '3')
    dropshadowFilter.append('feOffset')
      .attr('dx', '2')
      .attr('dy', '2')
      .attr('result', 'offsetblur')

    const dropshadowFilterMerge = dropshadowFilter.append('feMerge')
    dropshadowFilterMerge.append('feMergeNode')
    dropshadowFilterMerge.append('feMergeNode')
      .attr('in', 'SourceGraphic')

    svg.append('g')
        .attr('class', 'map__states')
        .attr('style', 'filter:url(#dropshadow)')
      .selectAll('path')
        .data(states.features)
      .enter().append('path')
        .attr('class', 'state__path')
        .attr('d', path)
        // .attr('style', 'filter:url(#dropshadow)')
        .on('mouseover', (data) => {
          const targetEl = d3.event.target;
          const theme = fakeData[data.properties.name];
          infoCard.infoState.innerText = data.properties.name;
          infoCard.infoRegion.innerText = data.properties.region;
          infoCard.themeTitle.innerText = theme.theme;
          addClass(targetEl, theme.slug);
        })
        .on('mouseout', (data) => {
          const targetEl = d3.event.target;
          const theme = fakeData[data.properties.name];
          removeClass(targetEl, theme.slug);
        });
  }

  d3.queue()
    .defer(d3.json, '/static/br-states.json')
    .await(mapLoaded);
}

export default d3Init;
