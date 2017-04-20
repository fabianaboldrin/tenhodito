import React, { Component } from 'react';
import Map from '../map';

class MainContent extends Component {
  render () {
    return (
      <main className="main-content">
        <Map />
        <div className="map__tooltip js-map-tooltip">
          <i className="tooltip__icon material-icons js-tooltip-icon">android</i>
          <span className="tooltip__theme js-tooltip-theme">Testando Tema</span>
        </div>
      </main>
    )
  }
}

export default MainContent;
