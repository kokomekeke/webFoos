const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true
})
module.exports = {
  devServer: {
    proxy: {
      '/static': {
        target: 'http://localhost:8081',
        changeOrigin: true,
      },
    },
  },
};
