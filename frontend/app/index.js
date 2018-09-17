import {AppContainer as HotReloadContainer} from 'react-hot-loader'
import React from 'react'
import ReactDOM from 'react-dom'

import App from './components/App'
import ApolloClient from "apollo-boost";
import {ApolloProvider} from "react-apollo";
import gql from 'graphql-tag';

const APP_MOUNT_POINT = document.getElementById('app');

const client = new ApolloClient({
    uri: "/api/graphql"
});

client
    .query({
        query: gql`
      {
  sequences {
    id
    circular
    bases
    size
    name
  }
}
    `
    })
    .then(result => console.log(result));

const renderRootComponent = (Component) => {
    ReactDOM.render(
        <HotReloadContainer>
            <ApolloProvider client={client}>
                <Component/>
            </ApolloProvider>
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