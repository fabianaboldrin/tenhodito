import React, { Component } from 'react';

class Sidebar extends Component {
  render() {
    return (
      <section className="sidebar">
        <div className="sidebar__header">
          <img className="header__logo" src="/static/img/tenho-dito-vertical-logo.png" alt="tenhodito-logo" />
        </div>
      </section>
    )
  }
}

export default Sidebar;
