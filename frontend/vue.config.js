const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,

  chainWebpack(config) {
    // Evita copiar el HTML plantilla dos veces en rutas con paréntesis.
    config.plugin('copy').tap(([options]) => {
      for (const pattern of options.patterns) {
        pattern.globOptions = pattern.globOptions || {}
        pattern.globOptions.ignore = [...(pattern.globOptions.ignore || []), '**/index.html']
      }
      return [options]
    })
  },

  devServer: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: 'all',

    client: {
      webSocketURL: 'auto://0.0.0.0:0/ws',

      overlay: {
        errors: true,
        warnings: false,
      },
    },
  },
})
