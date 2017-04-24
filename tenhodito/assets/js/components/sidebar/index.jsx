import React, { Component } from 'react';

class Sidebar extends Component {
  render() {
    return (
      <section className="sidebar">
        <div className="sidebar__header">
          <img className="header__logo" src="/static/img/tenho-dito-vertical-logo.png" alt="tenhodito-logo" />
        </div>
        <div className="sidebar__body">
          <p className="body__text">
            Veja o que está sendo mais falado no cenário político brasileiro. Clique nos estados para saber os
            temas mais abordados pelos deputados que os representam. Ou selecione uma outra opção de visualização:
          </p>
          <ul className="body__menu-list">
            <li className="menu-list__item">Por região</li>
            <li className="menu-list__item">Por partido</li>
            <li className="menu-list__item">Por tema</li>
          </ul>
        </div>
      </section>
    )
  }
}

export default Sidebar;
