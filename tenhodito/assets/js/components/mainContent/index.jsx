import React, { Component } from 'react';
import Map from '../map';

class MainContent extends Component {
  render () {
    return (
      <main className="main-content">
        <Map />
        <div className="map__info-card js-map-info-card">
          <div className="info-card__region-info">
            <span className="region-info__state">Distrito Federal</span>
            <span className="region-info__region">Centro-Oeste</span>
          </div>
          <div className="info-card__theme-info">
            <i className="theme-info__icon"></i>
            <span className="theme-info__title">Segurança</span>
          </div>
        </div>
      </main>
    )
  }
}

export default MainContent;
