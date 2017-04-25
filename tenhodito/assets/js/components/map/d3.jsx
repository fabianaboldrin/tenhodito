import * as d3 from 'd3';
import * as topojson from 'topojson';
import { addClass, removeClass } from '../../utils/polyfills'
import { convertEm } from '../../utils/convert'

function d3Init() {
  const paddingBottom = convertEm(5, document.querySelector('.js-map'));
  const map = {
    width: document.querySelector('.js-map').clientWidth,
    // width: 750,
    height: Math.max(document.documentElement.clientHeight, window.innerHeight || 0) - paddingBottom,
    selector: '.map',
  }

  const fakeData = {
    'AC': {
      slug: 'seguranca',
      theme: 'Segurança'
    },
    'AL': {
      slug: 'consumidor',
      theme: 'Consumidor'
    },
    'AP': {
      slug: 'economia',
      theme: 'Economia'
    },
    'AM': {
      slug: 'educacao',
      theme: 'Educação'
    },
    'BA': {
      slug: 'educacao',
      theme: 'Educação'
    },
    'CE': {
      slug: 'educacao',
      theme: 'Educação'
    },
    'DF': {
      slug: 'relacoes-exteriores',
      theme: 'Relações Exteriores'
    },
    'ES': {
      slug: 'relacoes-exteriores',
      theme: 'Relações Exteriores'
    },
    'GO': {
      slug: 'relacoes-exteriores',
      theme: 'Relações Exteriores'
    },
    'MA': {
      slug: 'seguranca',
      theme: 'Segurança'
    },
    'MT': {
      slug: 'seguranca',
      theme: 'Segurança'
    },
    'MS': {
      slug: 'seguranca',
      theme: 'Segurança'
    },
    'MG': {
      slug: 'adm-publica',
      theme: 'Administração Pública'
    },
    'PA': {
      slug: 'assistencia-social',
      theme: 'Assistência Social'
    },
    'PB': {
      slug: 'cidades',
      theme: 'Cidades'
    },
    'PR': {
      slug: 'ciencia',
      theme: 'Ciência'
    },
    'PE': {
      slug: 'previdencia',
      theme: 'Previdência'
    },
    'PI': {
      slug: 'turismo',
      theme: 'Turismo'
    },
    'RJ': {
      slug: 'trabalho',
      theme: 'Trabalho'
    },
    'RN': {
      slug: 'seguranca',
      theme: 'Segurança'
    },
    'RS': {
      slug: 'participacao-e-transparencia',
      theme: 'Participação e Transparência'
    },
    'RO': {
      slug: 'seguranca',
      theme: 'Segurança'
    },
    'RR': {
      slug: 'participacao-e-transparencia',
      theme: 'Participação e Transparência'
    },
    'SC': {
      slug: 'seguranca',
      theme: 'Segurança'
    },
    'SP': {
      slug: 'familia',
      theme: 'Família'
    },
    'SE': {
      slug: 'direitos-humanos',
      theme: 'Direitos Humanos'
    },
    'TO': {
      slug: 'familia',
      theme: 'Família'
    }
  }

  const mapTooltip = document.querySelector('.js-map-tooltip');
  const mapTooltipIcon = mapTooltip.querySelector('.js-tooltip-icon');
  const mapTooltipTheme = mapTooltip.querySelector('.js-tooltip-theme');

  function mapLoaded(error, br_states) {
    if (error) return console.error(error);

    const states = topojson.feature(br_states, br_states.objects.estados);


    const projection = d3.geoMercator()
        .fitSize([map.width - convertEm(2.5), map.height - convertEm(2.5)], states);

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

    const stateDropshadowFilter = svg.append('filter')
      .attr('id', 'stateDropshadow')
      .attr('height', '200%')
      .attr('width', '200%')

    stateDropshadowFilter.append('feGaussianBlur') // stdDeviation is how much to blur
      .attr('in', 'SourceAlpha')
      .attr('stdDeviation', '0')
    stateDropshadowFilter.append('feOffset') // how much to offset
      .attr('dx', '1')
      .attr('dy', '2')
      .attr('result', 'offsetblur')

    const stateDropshadowFilterMerge = stateDropshadowFilter.append('feMerge')
    stateDropshadowFilterMerge.append('feMergeNode')
    stateDropshadowFilterMerge.append('feMergeNode')
      .attr('in', 'SourceGraphic')

    svg.append('g')
        .attr('class', 'map__background')
      .selectAll('path')
        .data(states.features)
      .enter().insert('path')
        .attr('class', 'state__path')
        .attr('stroke-alignment', 'outer')
        .attr('d', path)

    svg.append('g')
        .attr('class', 'map__states')
        .attr('style', `filter:url(#mapDropshadow)`)
      .selectAll('path')
        .data(states.features)
      .enter().insert('path')
        .attr('class', 'state__path')
        .attr('d', path)
        .attr('stroke-linecap', 'round')
        // .attr('style', 'filter:url(#stateDropshadow)')
        .on('mouseover', (data) => {
          console.log(data)
          const targetEl = d3.event.target;
          const elementBox = targetEl.getBoundingClientRect();
          const theme = fakeData[data.id];
          const viewportWidth = document.documentElement.clientWidth;
          const top = elementBox.top + (elementBox.height / 2) - (mapTooltip.clientHeight / 2);
          mapTooltipTheme.innerText = theme.theme;

          let left = elementBox.left + (elementBox.width + convertEm(1.5));
          console.log(mapTooltip.offsetWidth)
          console.log(viewportWidth - mapTooltip.offsetWidth - left)
          if (viewportWidth - mapTooltip.offsetWidth - left < 100 ) {
            left = elementBox.left - (mapTooltip.offsetWidth + convertEm(1.5));
            addClass(mapTooltip, 'left');
          }

          mapTooltip.style.left = `${left}px`;
          mapTooltip.style.top = `${top}px`;
          addClass(mapTooltip, 'is-visible');
          addClass(mapTooltipIcon, `icon-${theme.slug}`);
          addClass(mapTooltipIcon, theme.slug);
          addClass(targetEl, theme.slug);
        })
        .on('mouseout', (data) => {
          const targetEl = d3.event.target;
          const theme = fakeData[data.id];
          removeClass(mapTooltip, 'is-visible');
          removeClass(mapTooltip, 'left');
          removeClass(targetEl, theme.slug);
          removeClass(mapTooltipIcon, theme.slug);
          removeClass(mapTooltipIcon, `icon-${theme.slug}`);
        });
  }

  d3.queue()
    .defer(d3.json, '/static/br-states.json')
    .await(mapLoaded);
}

export default d3Init;
