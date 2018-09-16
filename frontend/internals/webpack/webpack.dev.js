const path = require('path')
const merge = require('webpack-merge');
const base = require('./webpack.base.js');
const webpack = require('webpack')

module.exports = merge(base, {
    mode: 'development',
    devtool: 'inline-source-map',
    devServer: {
        contentBase: './dist'
    },
    plugins: [
        new webpack.HotModuleReplacementPlugin(),
    ],
    entry: {
        app: [
            'webpack-hot-middleware/client?reload=true',
            'react-hot-loader/patch',
        ],
    },
});