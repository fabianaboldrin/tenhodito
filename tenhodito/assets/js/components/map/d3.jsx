import * as d3 from 'd3';
import * as topojson from 'topojson';
import { addClass, removeClass } from '../../utils/polyfills'
import { convertEm } from '../../utils/convert'

function d3Init() {
  const paddingBottom = convertEm(2, document.querySelector('.js-map'));
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
    'PARÁ': {
      slug: 'consumidor',
      theme: 'Consumidor'
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
    'RORAIMA': {
      slug: 'educacao',
      theme: 'Educação'
    },
    'PARANÁ': {
      slug: 'relacoes-exteriores',
      theme: 'Relações Exteriores'
    },
    'ACRE': {
      slug: 'relacoes-exteriores',
      theme: 'Relações Exteriores'
    },
    'DISTRITO FEDERAL': {
      slug: 'relacoes-exteriores',
      theme: 'Relações Exteriores'
    },
    'SÃO PAULO': {
      slug: 'seguranca',
      theme: 'Segurança'
    },
    'AMAPÁ': {
      slug: 'seguranca',
      theme: 'Segurança'
    },
    'ESPIRITO SANTO': {
      slug: 'seguranca',
      theme: 'Segurança'
    },
    'MATO GROSSO': {
      slug: 'adm-publica',
      theme: 'Administração Pública'
    },
    'BAHIA': {
      slug: 'assistencia-social',
      theme: 'Assistência Social'
    },
    'PIAUÍ': {
      slug: 'cidades',
      theme: 'Cidades'
    },
    'MARANHÃO': {
      slug: 'ciencia',
      theme: 'Ciência'
    },
    'TOCANTINS': {
      slug: 'previdencia',
      theme: 'Previdência'
    },
    'CEARÁ': {
      slug: 'turismo',
      theme: 'Turismo'
    },
    'RIO GRANDE DO NORTE': {
      slug: 'trabalho',
      theme: 'Trabalho'
    },
    'PARAÍBA': {
      slug: 'seguranca',
      theme: 'Segurança'
    },
    'PERNAMBUCO': {
      slug: 'participacao-e-transparencia',
      theme: 'Participação e Transparência'
    },
    'ALAGOAS': {
      slug: 'seguranca',
      theme: 'Segurança'
    },
    'RONDÔNIA': {
      slug: 'participacao-e-transparencia',
      theme: 'Participação e Transparência'
    },
    'SERGIPE': {
      slug: 'seguranca',
      theme: 'Segurança'
    },
    'GOIÁS': {
      slug: 'familia',
      theme: 'Família'
    },
    'MATO GROSSO DO SUL': {
      slug: 'direitos-humanos',
      theme: 'Direitos Humanos'
    },
    'AMAZONAS': {
      slug: 'familia',
      theme: 'Família'
    }
  }

  const mapTooltip = document.querySelector('.js-map-tooltip');
  const mapTooltipIcon = mapTooltip.querySelector('.js-tooltip-icon');
  const mapTooltipTheme = mapTooltip.querySelector('.js-tooltip-theme');

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
    const mapDropshadowFilter = svg.append('filter')
      .attr('id', 'mapDropshadow')
      .attr('height', '200%')
      .attr('width', '200%')

    mapDropshadowFilter.append('feGaussianBlur') // stdDeviation is how much to blur
      .attr('in', 'SourceAlpha')
      .attr('stdDeviation', '1')
    mapDropshadowFilter.append('feOffset') // how much to offset
      .attr('dx', '1')
      .attr('dy', '7')
      .attr('result', 'offsetblur')

    const mapDropshadowFilterMerge = mapDropshadowFilter.append('feMerge')
    mapDropshadowFilterMerge.append('feMergeNode')
    mapDropshadowFilterMerge.append('feMergeNode')
      .attr('in', 'SourceGraphic')

    const stateDropshadowFilter = svg.append('filter')
      .attr('id', 'stateDropshadow')
      .attr('height', '200%')
      .attr('width', '200%')

    stateDropshadowFilter.append('feGaussianBlur') // stdDeviation is how much to blur
      .attr('in', 'SourceAlpha')
      .attr('stdDeviation', '1')
    stateDropshadowFilter.append('feOffset') // how much to offset
      .attr('dx', '1')
      .attr('dy', '3')
      .attr('result', 'offsetblur')

    const stateDropshadowFilterMerge = stateDropshadowFilter.append('feMerge')
    stateDropshadowFilterMerge.append('feMergeNode')
    stateDropshadowFilterMerge.append('feMergeNode')
      .attr('in', 'SourceGraphic')
    svg.append('g')
        .attr('class', 'map__states')
        .attr('style', 'filter:url(#mapDropshadow)')
      .selectAll('path')
        .data(states.features)
      .enter().insert('path')
        .attr('class', 'state__path')
        .attr('d', path)
        .attr('style', 'filter:url(#stateDropshadow)')
        .on('mouseover', (data) => {
          const targetEl = d3.event.target;
          const elementBox = targetEl.getBoundingClientRect();
          const theme = fakeData[data.properties.name];
          const top = elementBox.top + (elementBox.height / 2) - (mapTooltip.clientHeight / 2);
          const left = elementBox.left + (elementBox.width + convertEm(1.5));
          mapTooltip.style.left = `${left}px`;
          mapTooltip.style.top = `${top}px`;
          mapTooltipTheme.innerText = theme.theme;
          addClass(mapTooltip, 'is-visible');
          addClass(mapTooltipIcon, theme.slug);
          addClass(targetEl, theme.slug);
        })
        .on('mouseout', (data) => {
          const targetEl = d3.event.target;
          const theme = fakeData[data.properties.name];
          removeClass(mapTooltip, 'is-visible');
          removeClass(targetEl, theme.slug);
          removeClass(mapTooltipIcon, theme.slug);
        });
  }

  d3.queue()
    .defer(d3.json, '/static/br-states.json')
    .await(mapLoaded);
}

export default d3Init;
