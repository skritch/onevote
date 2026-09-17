import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import rehypeMathjax from 'rehype-mathjax'
import remarkMath from 'remark-math'
import { marimoIntegration } from 'astro-marimo';

import svelte from '@astrojs/svelte';

// https://astro.build/config
export default defineConfig({
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