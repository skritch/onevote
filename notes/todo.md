

## Tech


Views:
1. [ ] value of a vote by election x state (/states/[stateId].astro)
  - p1, p2, p5 as is
  - p3, p4 require district
2. [ ] value by election x state by party (/states/[stateId].astro?)
  - p1, p5 as is
  - p3, p4 require district
3. [ ] compare state v state by election (/compare/compare-result.astro)
  - compare states/districts
4. [ ] compare state v state by election x party (/compare/compare-result.astro)
5. [ ] over time by state/district? (no route yet, stateId page is for something else)
6. [ ] over states / states x parties by election (/elections/[electionId].astro)
7. [ ] compare scenarios
7. [ ] compare scenarios values



all across scenarios:
- p1: general election
  - dim: national
  - values: av (4 ps), pv (3 ps), wvv by party
  - years: values available for all yrs + 2028
- p2: simplified present day
  - dim: state
  - values: av (4 ps), pv (3 ps), wvv by party
  - years: no vap/vep in 1976
- p3: present-day
  - dim: state/district. But really only in 2 states.
    - maybe use p2 in other states?
  - values: av (ap/vap/vp), pv (vap/vp), wvv
  - years: 2012+ only

- p4: electoral with senators -> state
  - dim: state/district
  - values: av (ap/vap/vp), pv (ap/vap/vp), wvv
    - why different?
  
- p5: proportional
  - dim: state
  - values: av (4 ps), wvv
    - why no pv?
  years: no vap/vep in 1976
    



Initial plan:
- impl p1, p2, p5 by state
  - for an election, should display vs all other states
  - compare side-by-side with another presidential election scenario
  - or, compare all scenarios side by side
  - display av and pv x all available population variables
- and by state x party
  - also display wvv

(Note I don't feel good about either pv or wvv)



Implementation options:
- D3 or similar JS library
  - Observable
- Astro-marimo
  - How to embed in another page as a component?
    - How to pass data from enclosing component to Notebook?
  - Maybe better to just use Astro for the graphs?
  - Replicate the marimo-mdx flow, but with our pre-rendering options?
- Marimo-mdx
  - Need to test: how fast is this? What can it do?




TODO: wvv should always use "vp". Should we suffix it?
TODO: add tooltip to disabled V / Ps saying what is disabling them
- in manifest probably
- need to do this for other disablements too. later.




deploy:
- github pages
- or, domain name + cloudflare or something
- or a subdomain of my current site?




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





## Analysis


- [x] compute the above for each of the P1-P5.
  - [x] need district-level data
- compute for various changes to apportionment itself?
  - removing immigrants
  - citizen age -> 21
  - etc.
  


Try other valuations:
- swinginess?
- alternate wasted vote that doesn't treat a general election as wasted?3333
- pursue the derivative idea?
- read Gelman -> Ising model.
- "information loss".



Obviously state-proportional representation is nonviable, because rural areas are going to be
excluded entirely; both party's concentrated centers would wind up nominating all the candidates.


## Data

- acquire house/senate datasets
- add territories