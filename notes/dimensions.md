


# Dimensions



Our election analysis depends on all of the following:
- election:
  - office (president | house | senate, only president is implemented so far)
  - year (1976-2028, with some special casing for 2028, and district data missing pre-2012)
location:
  - state (50 + D.C.)
    - district (optional)
  - party (optional; only used by WVV so far)
- election scenario (P1 at a national granularity, P2 & P5 at state, P3 and P4 at district, but P3 is "really" a state resolution in all states except 2.)
- value (AV, PV, WVV so far. Only WVV depends on the party.)
  - population variable (AP, VAP, VEP, VP. Some V/P combinations not supported.)



At the same time, our `/states/[stateId]` page can be set to either state or district
granularity. So we need to determine appropriate behaviors when:
- (a) a national or state-level value is chosen, but a district is displayed.
- (b) district-level value is chosen, but a state is displayed

In (a) we can just show the state-level variable.

For (b) we need to do display some kind of state-wide summary of the district-level data. In some cases this is simple; e.g. AV and PV only depend on the district size and so are insensitive to equally-apportioed districts. Future values 