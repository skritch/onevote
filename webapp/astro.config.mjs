import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import react from '@astrojs/react';
import rehypeMathjax from 'rehype-mathjax'
import remarkMath from 'remark-math'

// https://astro.build/config
export default defineConfig({
  integrations: [
    react(), 
    mdx({
      remarkPlugins: [remarkMath],
      rehypePlugins: [rehypeMathjax],
    })
  ],
  markdown: {
    shikiConfig: {
      theme: 'github-light'
    }
  }
});