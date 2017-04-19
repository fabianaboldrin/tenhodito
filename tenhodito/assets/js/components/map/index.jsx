import React, { Component } from 'react';
import d3Init from './d3';

class Map extends Component {
  componentDidMount() {
    d3Init();
  }

  render() {
    return (
      <div className="map js-map" />
    );
  }
}

export default Map;
