export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },

  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@nuxtjs/color-mode',
    '@vueuse/nuxt',
  ],

  components: [
    { path: '~/components', pathPrefix: false },
  ],

  runtimeConfig: {
    public: {
      apiUrl: '/api',
      wsUrl: '/ws',
    },
  },

  tailwindcss: {
    cssPath: '~/assets/css/main.css',
  },

  colorMode: {
    classSuffix: '',
    preference: 'system',
    fallback: 'dark',
  },

  nitro: {
    devProxy: {
      '/api': { target: 'http://localhost:8000/api', ws: false },
      '/ws': { target: 'http://localhost:8000/ws', ws: true },
    },
  },

  app: {
    head: {
      title: 'Remotifex',
      meta: [
        { name: 'description', content: 'AI-powered remote software development platform' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1, maximum-scale=1' },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
        },
      ],
    },
  },
})
