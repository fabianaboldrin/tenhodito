import { addClass, removeClass } from './utils/polyfills';


console.log('oi')

window.onbeforeunload = function(){
  addClass(document.querySelector('.loading-spinner__wrapper'), 'active');
};
