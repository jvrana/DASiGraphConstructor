const express = require('express');
const bodyParser = require('body-parser');
const proxy = require('express-http-proxy');
const {graphqlExpress, graphiqlExpress} = require('apollo-server-express');
const schema = require('./schema.js');

const webpackConfig = require('../internals/webpack/webpack.dev');
const addDevMiddlewares = require('./addDevMiddlewares');

const frontendHost = process.env.HOST || 'localhost';
const frontendPort = process.env.PORT || 3000;

const backendPort = process.env.API_PORT || 5000;
const backendHost = process.env.API_HOST || frontendHost;

// bodyParser is needed just for POST.
const app = express();
app.use('/json', bodyParser.urlencoded({extended: true}), graphqlExpress({schema: schema}));
app.use('/graphql', bodyParser.json(), graphqlExpress({schema: schema}));
app.get('/graphiql', graphiqlExpress({endpointURL: '/graphql'})); // if you want GraphiQL enabled

// backend route
app.use('/api', proxy(`http://${backendHost}:${backendPort}`,
    {
        proxyReqPathResolver: (req) => {
            return require('url').parse(req.url).path;
        }
    }));


addDevMiddlewares(app, webpackConfig);

app.listen(frontendPort, frontendHost, (err) => {
    if (err) {
        return logger.error(err.message)
    }
    console.log("Frontend server started on " + frontendHost + ":" + frontendPort);
});
