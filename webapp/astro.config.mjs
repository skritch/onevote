import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import rehypeMathjax from 'rehype-mathjax'
import remarkMath from 'remark-math'

import svelte from '@astrojs/svelte';

// https://astro.build/config
export default defineConfig({
  integrations: [mdx({
    remarkPlugins: [remarkMath],
    rehypePlugins: [rehypeMathjax],
  }), svelte()],
  markdown: {
    shikiConfig: {
      theme: 'github-light'
    }
  }
});