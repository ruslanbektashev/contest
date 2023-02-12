const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
    entry: './src/js/main.js',
    plugins: [
        new MiniCssExtractPlugin({
            filename: 'bootstrap.min.css'
        })
    ],
    output: {
        globalObject: 'this',
        library: {
            name: 'bootstrap',
            type: 'umd',
        },
        filename: 'bootstrap.min.js',
        path: path.resolve(__dirname, '../../contest/static/bootstrap')
    },
    module: {
        rules: [
            {
                test: /\.(scss)$/,
                use: [
                    {
                        // Extracts CSS for each JS file that includes CSS
                        loader: MiniCssExtractPlugin.loader
                    },
                    {
                        loader: 'css-loader'
                    },
                    {
                        loader: 'postcss-loader',
                        options: {
                            postcssOptions: {
                                plugins: () => [
                                    require('autoprefixer')
                                ]
                            }
                        }
                    },
                    {
                        loader: 'sass-loader'
                    }
                ]
            }
        ]
    }
}