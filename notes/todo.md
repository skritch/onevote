

## Tech


SWE projects:
- implement a basic form of V1 in the UI


Figure out a straightforward way to duplicate graphics between:
- notebooks
- markdown on website
- html pages on website

More requirements:
- ideally we can dynamically create a graphic per-state, highlighting that state in particular
- a D3 pipeline like my personal blog would work for that, or similar, where we explicitly design graphics as react components
- I'm not sure any form of Marimo-conversion would work, short of full Python-in-the-browser reactivity.
- but ideally we'd have the same visuals on the state pages vs the method writeup, just with different emphasis...
- ideally these are also directly servable as "widgets" of some kind


requirements:
- supports mouseover
- can easily populate from either json in JS or straight from pandas



implement:
- state vs state comparison


deploy:
- github pages
- or, domain name + cloudflare or something
- or a subdomain of my current site?


## Analysis


Continue with Apportionment Weight, V1
- what happen if you just held each general election with every vote worth what we've just calculated, as opposed to the EC-winner-takes all approach?
  - to what extent does sum(V1 weights) correlate with election outcomes?

- obviously the low-population states have the highest-value votes. What fraction of the nation possesses each vote value? How to visualize? 
  - Maybe: a histogram over "values of the votes" with "number of voters" as bar height. Can also do this by party for the votes actually cast.
  - "average value of a vote by party"
  - by demographics


- compute the above for each of the P1-P5.
  - need district-level data
- compute for various changes to apportionment itself
  - removing immigrants
  - citizen age -> 21
  


Experiment with ways of turning V1 into a measure:
- devise a measure of overall fairness
  - rms
  - mad
  - entropy
- devise a way to compare the relative fairness of two separate electoral systems
  - versions of this can answer most of the L2 questions




Try other Values:
- V2, apportionment waste
- V3, wasted votes
- pursue the derivative idea?



## Data

- acquire districts dataset for some of the other P scenarios
- acquire house/senate datasets