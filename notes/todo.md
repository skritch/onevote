

## Tech


Views:
1. [ ] value of a vote by election x state (/states/[stateId].astro)
  - [x] p1, p2, p5 as is
  - [ ] p3, p4 require district
  - [ ] Add a "fact chart", state viz, and top line "here's what your vote is worth"
2. [x] value by election x state by party (/states/[stateId].astro?)
  - [x] p1, p2, p5 as is
  - [x] wvv needs to split out parties
  - [ ] p3, p4 require district
3. [ ] compare state v state by election (/compare/compare-result.astro)
  - compare states/districts
4. [ ] compare state v state by election x party (/compare/compare-result.astro)
5. [ ] over time by state/district? (no route yet, stateId page is for something else)
6. [ ] compare scenarios
7. [ ] over states / states x parties by election (/elections/[electionId].astro)



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
    





I don't feel good about either pv or wvv
- PV looks way too low across the board?
  - is it really normalized to 1? I'm skeptical
  - why missing for p5?
- WVV obviously weird with the "national loser = zero".


TODO p3:
- what to do before 2012? 
  - don't support districts, I guess. 
  - copy p2?

TODO p4:
- display average value for states
- display electors for districts
- display electors for states 
- is a statewide average correct? Does it include the senate contribution?
- only support p4 after 2012


TODO: clean up 2028 page
- show empty VAP/VEP
- where are state logos?

TODO: add tooltip to disabled V / Ps saying what is disabling them
- in manifest probably
- need to do this for other disablements too. later.


TODO:
- port the shapefile pipeline to its own repo, upload to kaggle maybe

TODO: script cleanup
- cache kaggle results locally.
- no default paths in CLI args


TODO: maybe "at large" districts aren't = "the whole state"?




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