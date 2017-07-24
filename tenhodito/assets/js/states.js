import StatesMap from './components/map/states';
import BubbleChart from './components/chart/bubble';


const map = new StatesMap();
map.setup();

const bubbleChart = new BubbleChart('.js-bubble-chart');
bubbleChart.setup();
