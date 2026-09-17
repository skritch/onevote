import { defineCollection } from 'astro:content';
import { file } from 'astro/loaders';
import { z } from 'astro/zod';

const states = defineCollection({
  loader: file("src/data/states.json"),
  schema: z.object({
    id: z.string(),
    name: z.string()
  })
});

const elections = defineCollection({
  loader: file("src/data/elections.json"),
  schema: z.object({
    id: z.string(),
    year: z.number(),
    type: z.enum(['president', 'senate', 'house']),
    name: z.string(),
    state: z.string().optional() // For senate/house elections
  })
});

export const collections = { states, elections };
