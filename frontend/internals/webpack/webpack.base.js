const path = require('path');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const APP_ROOT = path.join(process.cwd(), 'frontend', 'app');
const appConfig = require(path.join(APP_ROOT, 'config'));
const STYLES_ROOT = path.join(APP_ROOT, 'styles');

const htmlPlugin = new HtmlWebpackPlugin({
    template: "frontend/index.html",
    inject: true
});

const webpack =
    module.exports = {
        entry: {
            app: [
                path.join(process.cwd(), 'frontend', 'app', 'index.js')
            ]
        },
        plugins: [
            new CleanWebpackPlugin(['dist']),
            htmlPlugin,
        ],
        output: {
            filename: '[name].bundle.js',
            path: path.resolve(__dirname, 'dist')
        },
        optimization: {
            splitChunks: {
                chunks: 'all'
            }
        },
        module: {
            rules: [
                {
                    test: /\.js$/,
                    exclude: /node_modules/,
                    use: {
                        loader: "babel-loader"
                    }
                },
                {
                  type: 'javascript/auto',
                  test: /\.mjs$/,
                  use: []
                },
                {
                    test: /\.(csv|tsv)$/,
                    use: {
                        loader: 'csv-loader'
                    }
                },
                // {
                //     test: /\.json$/,
                //     use: [{loader: 'json-loader'}],
                // },
                {
                    test: /\.(sass|scss)$/,
                    use: [
                        {loader: 'style-loader'},
                        {loader: 'css-loader'},
                        {loader: 'resolve-url-loader'},
                        {
                            loader: 'sass-loader',
                            options: {
                                sourceMap: true,
                                includePaths: [STYLES_ROOT],
                                // automatically import variables into every scss file
                                data: `@import "~super-skeleton/scss/base/_variables.scss";
                     @import "${__dirname}/../../app/styles/_variables.scss";
                    `,
                            },
                        },
                    ],
                },
                {
                    test: /\.css$/,
                    use: ["style-loader", "css-loader"]
                },
                {
                    test: /\.(png|jpg|gif|svg|eot|ttf|woff|woff2)$/,
                    loader: 'url-loader',
                    options: {
                        limit: 10000
                    }
                }
            ]
        },
    };