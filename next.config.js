const path    = require('path')
const withCSS = require('@zeit/next-css')

module.exports = phase => {
    const nextConfig = {
        target: 'serverless',

        env: {
            PRE_RELEASES: process.env.PRE_RELEASES || "false",
        },

        webpack(config, options) {
            config.resolve.alias = {
                ...config.resolve.alias,

                components: path.resolve(__dirname, 'components/'),
                utils:      path.resolve(__dirname, 'utils/'),
            }

            return config
        },
    }

    return withCSS(nextConfig)
}
