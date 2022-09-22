const { merge } = require('webpack-merge');
const webpack = require('webpack');
const common = require('./webpack.common.js');

module.exports = merge(common, {
  mode: 'production',
  plugins: [
    new webpack.DefinePlugin({
      API_URL: JSON.stringify('https://fuelpricesgr-api.mavroprovato.net')
    }),
  ]
});
