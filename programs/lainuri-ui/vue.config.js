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
    }
  }
}
