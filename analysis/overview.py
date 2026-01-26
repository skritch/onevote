import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Analysis Overview

    Our goal is to answer the questions:

    **Q1**. How much is your vote worth in a given election?

    **Q2**. How fair is an election overall?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Levels of Analysis

    There are many ways to go about assigning the "value" of a vote. We can generally organize these into categories depending on what kind of information goes into the measure:

    **C1**. **The voting system alone**. Here we have the theoretical issues with "first-past-the-post" / "plurality" voting, including:
    1. Wasted votes in general. If only one candidate is elected, all other votes count, in a certain sense, zero. (This is not a great argument, see C4.) Party-proportional representation and the like can help with this problem, where applicable.
    2. Potential for spoilers. Ranked-choice and similar systems help here.
    3. Theoretical incentives on candidates and platforms due to FPIP/plurality systems.

    I won't try to measure unfairness based on the voting system in the abstract. It will be easier to consider C2 or C3 below, which take more of reality into account.

    **C2**. **Voting systems + state populations**.
    1. Here the main issues are is the inequality of apportionment, such as Wyoming receiving 3 electors for only 600K people (200K/elector) while California has 54 electors for 40M (740K / elector). We can subdivide this further:
      - Apportionment of electors to states (in the U.S. each state has 3 minimum)
      - Discrepancies due to winner-take-all assignments instead of electors voting with their associated district
      - Rounding discrepancies
    2. Any philosophical issues with the calculation of apportionment, e.g. illegal aliens being counted, exclusion of overseas territories.

    The following tables lists the different populations variables we might use:



    | Variable      | Full Name | Description | Nationally in 2020 | In dataset? |
    | ----------- | ----------- | ----------- | ---- | ---- |
    | P      | population       | the census residential population of a state  |  331.4M | |
    | AP   | apportionment population        | P + overseas federal employees and their dependents - indigenous populations "not taxed" | 331.8M[^ap] | `state_population` |
    | VAP   | voting-age population | all residents 18 and older.  | 258M | `state_vap_estimate` |
    | CVAP   | civizen voting-age population   | VAP - non-citizens  | 233M |  |
    | VEP   | voting-eligible population  | VAP - felons, etc. barred from voting. | 231M | `state_vep_estimate`
    | VP   | voting population  | Actual number of voters | 158M | `votes_total`

    [^ap]: The census definition of AP excludes the ~700k residents of D.C., who have no representation in the House (except for 1 non-voting delegate), and are then granted their 3 electors by the 23rd Amendment. Under that definition the total would be 331.1M. My `state_population` variable does include D.C. so as to assign it an AP : elector ratio.

    **C3**. **Voting system + population + party affiliations**.
    1. Wasted votes by state margin. Here we should be able to characterize "swing states"--states where every vote is inherently much more likely to affect the overall outcome, just because the election is likely to be close and to have a marginal effect on the national election.
      - the measures here might be "probability of an individual vote deciding the election" or "marginal effect of a vote".
      - winner-takes-all systems should produce far more wasted votes than proportional ones.
    2. Gerrymandering (which is really a way of engineering wasted-votes)
    3. Spoilers

    Here "party affiliation" might be defined in various ways:
    - *post hoc* election outcomes (which is not necessarily better than *a priori* estimates, as it include dynamical effects, see C4.)
    - *a priori* estimates of election outcomes
      - the simplest is "whatever happened last time"
      - polling
      - statistical models
    - "true" party affiliations (which are only an idealization)
    - estimated party affiliations
      - voter registrations
      - polling
      - statistical models

    We may also need to estimate turnout to determine how close an election is likely to be. Again we have options:
    - *post hoc* turnout
    - *a priori estimates*
      - what happened last time
      - polling
      - voter registrations
      - statistical models


    **C4**. **Voting system + population + party affiliations + dynamical effects** of these on...

    1. ...on candidates and platforms, Candidates are chosen to appeal to moderates, and are chosen *by* primaries or similar; the effect is that approxime party affiliations of a population have some sort of dynamical effect on the candidates themselves--to be more radical in the primaries and then moderate, to avoid alienating their base or moderates with certain issues, etc.

    2. ...on canvassing, ad spend, etc. (Inasmuch as these do anything.)

    3. ...on voter turnout--whether people vote depends on the perception that their votes will matter.

    These quickly get complex, so we won't take them on for now.

    But we should keep this category in mind when considering *counterfactuals*: the turnout which actually occurs, say, is some function of the voting system and party affiliations; we cannot simply say "what would have been the outcome of a national general election under such-and-such system?", because different voters would have showed up, candidates would have positioned themselves and advertised differently, etc.

    **C5**. **Issues with voting itself**:
    1. Voters unable to take time off or travel to polling place
    2. Lost ballots
    3. ID requirements limiting franchise
    4. Fraud
    5. Philosophical issues with the franchise itself, such as the exclusion of overseas territories


    **C6**. **Issues with the expression of electorate's preferences**.
    1. Effects of primarying/caucuses and party conventions.
    2. "Median voter theorem" and "Hotelling's law"-type incentivizes for candidates.

    These quickly get complex, so we won't take them on for now.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ----

    ## Presidential Electoral Scenarios

    **P1**. The present day: winner-takes-all electors in all states but Maine and Nebraska.
    - Will require a dataset of results and populations by district in those two states.

    **P2**. A national general election.

    **P3**. Simplified present day (winner-take-all in all states)

    **P4**. Assigning electors by districts, and the two senate electors to the winners of the states as whole. (I.e. what Maine/Nebraska do but nationwide)
    - Will require a dataset of results and populations by district.

    **P5**. Assigning state electors, including senate electors, to candidates in proportion to vote share in each state.
    - Requires a method of handling remainders.

    **P6**. National ranked-choice/instant-runoff.
    - May not have the data, but perhaps someone has estimated this.

    **P7-P9**. As P3-P5, but without the 2 Senate electors per state.

    **P10**. Various ranked-choice/instant-runoff-type schemes to determine electors at the district level.
    - Maine does some version of this as of 2020.

    Realistically, we will probably only take on P1-P6.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Basic Notation

    For Q1, our answer will be some multiple of $\frac{1}{N}$, with $N$ the total population (see below); this is obviously the most "fair" value for a vote to be worth.

    We'll use variables $x, y, z$ to designate these "values" of different votes in units of $1/N$, and $p, q$ to design the un-"normalized" values. We have


    $$
    x_i = \frac{p_i}{1/N} = Np_i
    $$

    with $i$ some index referring to a particular voter.

    For a general popular election between two candidates with 100% turnout, we will assert that any reasonable measure of  the "value of a vote" should produce

    $$
    \begin{align}
    x_i = 1 && && && p_i = \frac{1}{N}
    \end{align}
    $$


    For Q2, we can consider separately:
    - answers which are some function of the answer to Q1, such as "variance of $x_i$" or "entropy"
    - answers distinct from Q1, e.g. those involve the ability of voters to get to polls


    Also, note that an answer to Q2 may only be defined pairwise between *different* voting systems.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    -----

    ## Considerations for Measure Design

    Of all the above categories, the most tractable angles for quantifying the "fairness" of the U.S. presidential election will be:

    C2.1, apportionment. Here we can use a measure which depends on state populations alone (i.e. no party affiliations.)
    - the easiest idea is to measure the inequality of apportionment: relative number of electors per citizen.
    - another idea: something like a discrete derivative $\frac{d(\text{outcome})}{dx}$ (this might turn out to be the same thing)

    C3.1, wasted votes, using "post-hoc" party affiliation and turnout, i.e. how many votes were *actually* wasted? The main aim would be to measure the unfairness of "swing states".
    - Here we can probably come up with a measure which makes use of the gap between the two leading parties only.
    - Possibly "fraction of votes wasted" will suffice here.


    I *don't* like algorithms that try to deal in "probabilities of a vote being pivotal" (like a [Banzhaf power index](https://en.wikipedia.org/wiki/Banzhaf_power_index)), or which cannot give an answer for third parties; they should give very low values for third parties instead.


    ---


    - what about probabilities?
    - how much should we be considering "factors which could change an election" vs factors which are neutral to the outcome, e.g. "how many people were denied the franchise?"
    - Q2 answer could involve Q1 answer, but it also might not.
    - ... much more here.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Directions from here:

    Continue with Apportionment Inequality
    - compare by parties x election: which party benefits the most from unevenly-valued votes? What is the net effect of the votes actually cast being worth what they are?
    - what happen if you just held each general election with every vote worth what we've just calculated, as opposed to the EC-winner-takes all approach?
    - obviously the low-population states have the most-value votes. What fraction of the nation possesses each vote value? How to visualize? Maybe: a histogram over "values of the votes" with "number of voters" as bar height. Can also do this by party for the votes actually cast.

    Steps now are:
    - compute the above for each of the P1-P5.
      - need district-level data
    - determine which population (AP VAP VEP) makes the most sense.


    Address Q2:
    - devise a measure of overall fairness
    - devise a way to compare the relative fairness of two separate electoral systems
      - versions of this can answer most of the C2 questions


    Try other measures:
    - try a wasted-vote measure for C3?
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
