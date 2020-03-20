const CopyPlugin = require('copy-webpack-plugin');

module.exports = {
  "transpileDependencies": [
    "vuetify"
  ],
  "devServer": {
    "watchOptions": {
      "poll": true
    }
  },
  configureWebpack: {
    module: {
      rules: [
        { test: /globalize/, parser: { amd: false } }
      ]
    },
    plugins: [
      new CopyPlugin([
        { from: '../lainuri-serve/lainuri/config_schema.json', to: './config_schema.json' },
      ])
    ],
  }
}
