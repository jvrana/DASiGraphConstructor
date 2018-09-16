import {AppContainer as HotReloadContainer} from 'react-hot-loader'
import React from 'react'
import ReactDOM from 'react-dom'

import App from './components/App'
const APP_MOUNT_POINT = document.getElementById('app');

import ApolloClient from "apollo-boost";
const client = new ApolloClient({
    uri: "/api/graphql"
});

const renderRootComponent = (Component) => {
    ReactDOM.render(
            <HotReloadContainer>
                <Component/>
            </HotReloadContainer>,
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