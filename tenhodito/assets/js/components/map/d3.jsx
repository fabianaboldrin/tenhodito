import * as d3 from 'd3';
import * as topojson from 'topojson';
import { addClass, removeClass } from '../../utils/polyfills'

function d3Init() {
  const map = {
    width: 750,
    height: 650,
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

    svg.append('g')
        .attr('class', 'map__states')
      .selectAll('path')
        .data(states.features)
      .enter().append('path')
        .attr('class', 'state__path')
        .attr('d', path)
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
