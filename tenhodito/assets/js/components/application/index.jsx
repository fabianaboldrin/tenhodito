import React, { Component } from 'react';

import Sidebar from '../sidebar';
import MainContent from '../mainContent';

class Application extends Component {
  render() {
    return (
      <div className="tenhodito-application">
        <Sidebar />
        <MainContent />
      </div>
    );
  }
}

export default Application;
