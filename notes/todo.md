

## Tech


SWE projects:
- implement a basic form of V1 in the UI

Figure out a straightforward way to duplicate graphics between:
- notebooks
- markdown on website
- html pages on website
- directly-servable widgets

More requirements:
- ideally we can dynamically create a graphic per-state, highlighting that state in particular
- a D3 pipeline like my personal blog would work for that, or similar, where we explicitly design graphics as react components
- I'm not sure any form of Marimo-conversion would work, short of full Python-in-the-browser reactivity.
- but ideally we'd have the same visuals on the state pages vs the method writeup, just with different emphasis...


requirements:
- supports mouseover
- can easily populate from either json in JS or CSVs


implement:
- state vs state comparison


deploy:
- github pages
- or, domain name + cloudflare or something
- or a subdomain of my current site?


## Analysis


- [x] compute the above for each of the P1-P5.
  - [x] need district-level data
- compute for various changes to apportionment itself
  - removing immigrants
  - citizen age -> 21
  - etc.
  


Try other valuations:
- swinginess?
- pursue the derivative idea?
- read Gelman -> Ising model.
- "information loss".



Obviously state-proportional representation is nonviable, because rural areas are going to be
excluded entirely; both party's concentrated centers would wind up nominating all the candidates.


## Data

- acquire house/senate datasets
- add territories