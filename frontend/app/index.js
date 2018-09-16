import { AppContainer as HotReloadContainer } from 'react-hot-loader'
import React from 'react'
import ReactDOM from 'react-dom'

import App from './components/App'
const APP_MOUNT_POINT = document.getElementById('app');

const renderRootComponent = (Component) => {
  ReactDOM.render(
      <Component />,
    APP_MOUNT_POINT
  )
};


renderRootComponent(App);

if (module.hot) {
  module.hot.accept('./components/App', () => {
    ReactDOM.unmountComponentAtNode(APP_MOUNT_POINT)
    const NextApp = require('./components/App').default;
    renderRootComponent(NextApp)
  })
}