import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import rehypeMathjax from 'rehype-mathjax'
import remarkMath from 'remark-math'
import { marimoIntegration } from 'astro-marimo';

import svelte from '@astrojs/svelte';

// https://astro.build/config
export default defineConfig({
  // vite: {
  //   plugins: [{
  //     name: 'suppress-marimo-health',
  //     configureServer(server) {
  //       server.middlewares.use((req, res, next) => {
  //         if (req.url?.endsWith('/health')) {
  //           res.writeHead(200, { 'Content-Type': 'application/json' });
  //           res.end('{"status":"ok"}');
  //         } else {
  //           next();
  //         }
  //       });
  //     }
  //   }]
  // },
  integrations: [
    mdx({
      remarkPlugins: [remarkMath],
      rehypePlugins: [rehypeMathjax],
    }),
    svelte(),
    marimoIntegration({ layout: "src/layouts/NotebookLayout.astro" })
  ],
  markdown: {
    shikiConfig: {
      theme: 'github-light'
    }
  }
});