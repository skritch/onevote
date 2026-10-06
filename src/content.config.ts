import { defineCollection } from 'astro:content';
import { file } from 'astro/loaders';
import { z } from 'astro/zod';
import type { State } from './lib/states';

const states = defineCollection({
  loader: file("src/data/states.json", {
    parser: (text) => JSON.parse(text).map((s: State) =>
      ({ ...s, id: s.statePO.toLowerCase() }))
  }),
  schema: z.object({
    statePO: z.string(),
    stateName: z.string()
  })
});

const elections = defineCollection({
  loader: file("src/data/elections.json"),
  schema: z.object({
    id: z.string(),
    year: z.number(),
    office: z.enum(['president', 'senate', 'house']),
    name: z.string(),
    state: z.string().optional() // For senate/house elections
  })
});

export const collections = { states, elections };
