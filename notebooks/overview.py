import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Analysis Overview

    Our goal is to answer the questions:

    **Q1**. How much is your vote worth in a given election?

    Answer to this question will be called "values" and given identifiers like **V1**.

    **Q2**. How do we measure the fairness of the election overall?

    Answer to this question will be called "measures of fairness" and given identifiers like **M1**.

    A value might come with an obvious measure, or not.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Levels of Analysis

    There are many ways to go about assigning the "value" of a vote. We can generally organize these into categories depending on what kind of information goes into the measure:

    **L1**. **The voting system alone**. Here we have the theoretical issues with "first-past-the-post" / "plurality" voting, including:
    1. Wasted votes in general. If only one candidate is elected, all other votes count, in a certain sense, zero. (This is not a great argument, see L4.) Party-proportional representation and the like can help with this problem, where applicable.
    2. Potential for spoilers. Ranked-choice and similar systems help here.
    3. Theoretical incentives on candidates and platforms due to FPIP/plurality systems.

    I won't try to measure unfairness based on the voting system in the abstract. It will be easier to consider L2 or L3 below, which take more of reality into account.

    **L2**. **Voting systems + state populations**.
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

    [^ap]: The census definition of AP excludes the ~700k residents of D.C., who have no representation in the House (except for 1 non-voting delegate), and are then granted their 3 electors by the 23rd Amendment. Under that definition the total would be 331.1M. My `state_population` variable does include D.C., as we would like to assign it an AP : elector ratio.

    **L3**. **Voting system + population + party affiliations**.
    1. Wasted votes, in some sense. Here we should be able to characterize "swing states"--states where every vote is inherently much more likely to affect the overall outcome, just because the election is likely to be close and to have a marginal effect on the national election. How wasted a vote is will depend on the party affiliation (ex post or ex ante, see below).
    2. Gerrymandering (which is really a way of engineering wasted-votes)
    3. Spoilers

    Here "party affiliation" might be defined in various ways:
    - *ex post* actual election outcomes (note this is not necessarily a better definition than *a priori* estimates, as it include dynamical effects, see L4.)
    - *ex ante estimates of election outcomes
      - the simplest is "whatever happened last time"
      - polling
      - statistical models
    - "true" party affiliations (which are only an idealization)
    - estimated party affiliations
      - voter registrations
      - polling
      - statistical models

    We may also need to estimate turnout to determine how close an election is likely to be. Again we have options:
    - *ex post* actual turnout
    - *ex ante estimates*
      - what happened last time
      - polling
      - voter registrations
      - statistical models


    **L4**. **Voting system + population + party affiliations + dynamical effects**, i.e. feedback from the voting system affecting...

    1. ...candidates and platforms, Candidates are chosen to appeal to moderates, and are chosen *by* primaries or similar; the effect is that approxime party affiliations of a population have some sort of dynamical effect on the candidates themselves--to be more radical in the primaries and then moderate, to avoid alienating their base or moderates with certain issues, etc.

    2. ...canvassing, ad spend, etc.

    3. ...voter turnout--whether people vote depends on the perception that their votes will matter.

    These quickly get complex, so we won't take them on for now.

    But we should keep this category in mind when considering *counterfactuals*: the turnout which actually occurs, say, is some function of the voting system and party affiliations; we cannot simply say "what would have been the outcome of a national general election under such-and-such system?", because different voters would have showed up, candidates would have positioned themselves and advertised differently, etc.

    **L5**. **Wrong and Missing Votes**:
    1. Voters unable to take time off or travel to polling place.
    2. Lost ballots
    3. Restrictions on voting itself: unreasonable ID requirements, intimidation, poll taxes, etc.
    4. Fraud
    5. Philosophical issues with the franchise itself, such as the exclusion of overseas territories

    We could further try to quantify the effect of wrong votes on the voters who *did* vote--to what extent were they disenfranchised by the loss of their potential allies?


    **L6**. **Issues with the expression of electorate's preferences**.
    1. Effects of primarying/caucuses and party conventions.
    2. "Median voter theorem" and "Hotelling's law"-type incentivizes for candidates.

    These quickly get complex, so we won't take them on for now.

    -----


    Of all the above categories, my intuition is that the most tractable angles for quantifying the "fairness" of the U.S. presidential election will be:

    - L2.1, apportionment.
    - L3.1, wasted votes.
    - L5, missing votes.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ----

    It will help to give identifiers to the scenarios we would like to compare.

    ## Presidential Electoral Scenarios

    **P1**. A national general election.

    **P2**. Simplified present day (winner-take-all in all states)

    **P3**. The present day: winner-takes-all electors in all states but Maine and Nebraska.
    - Will require a dataset of results and populations by district in those two states.

    **P4**. Assigning electors by districts, and the two senate electors to the winners of the states as whole. (I.e. what Maine/Nebraska do but nationwide)
    - Will require a dataset of results and populations by district.

    **P5**. Assigning state electors, including senate electors, to candidates in proportion to vote share in each state.
    - Requires a method of handling remainders.

    -----
    Lower priority:

    **P6**. National ranked-choice/instant-runoff.
    - May not have the data, but perhaps someone has estimated this.

    **P7-P9**. As P3-P5, but without the 2 Senate electors per state.

    **P10**. Various ranked-choice/instant-runoff-type schemes to determine electors at the district level.
    - Maine does some version of this as of 2020.

    Realistically, we will probably only take on P1-P5 and maybe P6.

    ---

    It may be interesting to also consider these in a cartoon scenario with just 50 voters:
    1. Equal votes $(10,10,10,10,10)$. (This is P1, a general election.)
    2. "States" of size $(20,10,10,10)$ with electors apportioned exactly by population $(20,10,10,10)$, who assign electors proportionally. (This is equivalent to case 1, so also P1)
    3. States of size $(20,10,10,10)$ with electors apportioned in exact proportion to population  $(2,1,1,1)$ assigned by Winner-Takes-All (WTA) within the states. (P7, kind of)
    4. States of size $(20,10,10,10)$, with electors apportionated proportionately $(2,1,1,1)$, but assigned in proportion to the vote within the states. (P9, kind of)
    5. States of size $(20,10,10,10)$, with some non-proportional apportionment, such as $(4,3,3,3,3)$, with electors in proportion to the vote within the states. (P5)
    6. States of size $(20,10,10,10)$, with some non-proportional apportionment, such as $(4,3,3,3,3)$, with electors assigned by WTA within the states. (P2)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    -----

    ## Philosophical Considerations for Value and Measure Design

    Trying to read about these topics online, I am led to the conclusion that the field (or the part of it which rises to the surface on Wikipedia and the like) is quite muddled. The point of all the structure I am establishing here is to un-muddle things.

    As above, our measures may turn out to target any of the levels L1... L6 above. My ambition, for the presidential election, is to target:
    - L2
    - L3
    - L5

    That is, "purely theoretical" (L1), "dynamical" (L4), and the "underlying preferences" (L6) are out of scope, though we may still take them into consideration. A reasonable voting system should be *simple*; it is as important that it "feel" fair as it is that it "be" fair.

    I want to additionally place the following stipulation on measures of fairness:

    *A fully general election for a single office is perfectly fair*.[^general]

    [^general]: It may be said that I am sweepign the problem under the rug  by taking a "national general election" as fair from the outset. Well--too bad. I think this is so obvious as to not be worth talking about. I really cannot think of a way any other system could be fairer than this, for a single office.

    This immediately rules out a lot of "wasted vote" measures which treat _all the losing candidate's votes_ as wasted. This is a pointless view. This also steers us far away from measures which attempt to quantify "the probability of a vote being decisive", which to me seems rather nonsensical: such a probability is a function of a lot of things beyond the _fairness of the election system itself_.

    Instead, what we want to measure is something like the "incentivize for a candidate to appeal to a voter". In the view of a candidate trying to win votes, all votes in a general election trade one-for-one against each other--hence, all are equal.

    That is: our philosophical outlook is that we would like to measure the _influence of a voter's preferences on the policies/platform which result from the election_ (bringing in a bit of L6), rather than the _influence of their vote_. The majority of the influencing happens before the time of the vote!


    Now an immediate objection is that, *in practice* candidates are going to mostly be interested in changing the minds of voters near the *median* (assuming preferences are basically linear).

    I think this is fine, for two main reasons:
    - The "ideal" winner of an idealized general election *is* one who reflects the views of median voter. Who else would it be??[^mvt]
    - While candidates of course will position themselves and target their rhetoric in ways which efficiently win over the public in the neighborhood of the median, it is still the case that every voter in a general election exerts the same influence over the "position of the median"--you can move it by, at most, one spot in either direction.

    [^mvt]: This brings to mind the [median voter theorem](https://en.wikipedia.org/wiki/Median_voter_theorem), which says that, under reasonable conditions, an election will choose the candidate *preferred* by the median voter. Note this is not quite the same thing as "reflecting the views of the median", as it takes the candidates themselves as fixed.

    Let us also enumerate briefly some of the ways a real election differs from an "idealized" one:
    - the candidates (or their views) are selected (or change) on the basis of the electorate's own views (this is good--a representative should represent!)
    - candidates have noisy/biased signals of the electorate's preferences, and v.v.
    - candidates have inherent levels of "quality" and/or "likeability" as people, independent of their political views.
    - candidates have some power to *alter* the views of the electorate. (Potentially a lot of power, as the Trump era demonstrates.)

    All of these are certainly true, but should not really affect whether an election is "fair", at least to first order. This is, really, a simpler problem.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Basic Notation

    For Q1, our answer will be some multiple of $\frac{1}{N}$, with $N$ the total population (see below); this is obviously the most "fair" value for a vote to be worth.

    We will use $n_s, n_d$ similar to represent the "population of state $s$ or district $d$", with variables like $S, D$ for the number of states or districts.

    We'll use variables like $x, y, z$ to designate these "values" of different votes in units of $1/N$. That is, for a general popular election, every vote is worth $1$ unit:

    $$
    \begin{align}
    x_i = 1 && \text{(popular vote)}
    \end{align}
    $$


    where $i$ some index referring to a particular voter.

    In a "weighted" election where voter $i$ is assigned $e_i$ votes, their weight should obviously be $e_i$:


    $$
    \begin{align}
    x_i = e_i && \text{(weighted vote)}
    \end{align}
    $$


    If we want to assign variables for the votes of specific people or states we'll use variables $u, v, w$.

    If assigning "weights" to votes as in the electoral college, we will use symbols like $e, f$ for "elector". So we might say that state $s$ has electors $e_s$. We'll use the corresponding capital $E, F$ for the total number of electors: $\sum_s e_s = E$.

    When we consider party affiliations we'll use $p, p_s$ to represent one party's share nationally or in a state, or $p_j, p_{j, s}$ with j ranging over parties.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---


    TODO: probably treat $R$ as a sum of 0s or 1s...
    TODO: probably remove all of this...

    In a national popular election with a binary outcome, one way to determine the median is by the sign of (votes for) minus (votes against):

    $$
    \text{result} = \text{sign}\left( |\text{for}| -  |\text{against}|\right)
    $$

    If $v_i = \pm 1$ is the vote of voter $i$, and the overall result is $R = \pm 1$, then this expression is

    $$
    R_{\text{popular}} = \text{sign}\left(\sum v_i\right)
    $$

    If voters' votes have unequal weights $e_i$, then the outcome is:

    $$
    R_{\text{weighted}} = \text{sign}\left(\sum e_i v_i\right)
    $$

    In the first case the obvious "value of a vote" is $x_i = 1$ for all $i$. In the second, it is obviously $x_i = e_i$ or perhaps a normalized $x_i = \frac{e_i}{E}$.

    Evidently we can quantify a voter's "influence" by considering their contribution to the "decision criteria", the sum of votes, which we'll call $r$, with the outcome being determine by $R = \text{sign}(r)$. Then in the

    $$
    \begin{align}
    r_{\text{popular}} = \sum v_i && && && r_{\text{weighted}} = \sum e_i v_i \\
    x_{i, \text{popular}} = 1 && && && x_{i, \text{weighted}} = e_i
    \end{align}
    $$

    Evidently the coefficient of $v_i$ in $r$ is something like the "weight of a vote":

    $$
    x_i \stackrel{?}{=} \frac{\partial r}{\partial v_i}
    $$

    For single-tiered elections (no districts / states), this is a completely reasonable result! The trick will be generalizing it to multi-tiered elections.

    For a two-tiered election (problem P3, the simplified electoral college), an exact expression for the overall decision criteria $r$ in terms of the state "votes" $R_s$ or the individual votes $v_{s, i}$ is:

    $$
    r = \sum_s e_s R_s = \sum_s e_s \cdot \text{sign}\left( \sum_i^{n_s} v_{s, i} \right)
    $$

    We can't take a derivative of $\text{sign}\left( \sum_i^{n_s} v_{s, i} \right)$, though. What *do* we do?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Values

    Here is a first pass at designing some measures.

    The first two involve L2 (apportionment) only.

    **V1**: **Apportionment Weight**. We simply divide the electors for each state by the population, giving $x_s \propto \frac{e_s}{n_s}$ for state $s$, then scale so they sum to $N$:

    $$
    \begin{align}
    x_s &= \frac{e_s / E}{n_s / N} \\
    \sum_s n_s x_s &= N \sum_s \frac{e_s}{E} = N
    \end{align}
    $$

    This is "L2" measure--it depends on apportionment only, and knows nothing of "swing states" or the like. It might also be called "relative representation". It could be easily adapted into meaures on the House and Senate as well.

    - can this be written as an appropriate generalization of the derivative above?
    - this measure would treat perfectly proportional apportionments $e_i \propto \frac{n_i}{N}$ as perfectly fair, even if they are WTA.

    **V2**, wasted votes at L2.

    - Without using party affiliation at all, how "susceptible" is an apportionment scheme to wasting votes, just due to the fact that $e_s$ votes swing together?
    - The idea here is to use to only L2 apportionment data, but to penalize WTA at the state/district level.
    - It will simplest to try to distinguish just the effects of grouping $n_s$ voters into "states" with vote $n_s$. We can handle the uneven apportionment separately (e.g. by V1). Ideally this will make V1 and V2 "orthogonal" to each other.
    - V2 is basically a measure of "coarse graining", then. The value of a vote in state should go down as the size of the state grows.
      - But when the state size reaches $N$, we just have a general election again, but now at a lower level: the entire election is decided "within the state".
      - Does this mean the valuation has a minimum? Or should it go to zero, but the valuation "within the state" then dominates?
      - Could it just be a sum like $\propto \frac{1}{n_s} + \frac{n_s}{N}$?
      - Of course, within a WTA state, a vote is perfectly fair. Where it's unfair is the level above this.
    - Everyone in the same state should have the same value. Once a state reaches 50% of the population the value of all other states becomes exactly zero, and its members reach 1.
    - We probably cannot require that coarse-graining affects only the voters within the affected states.
    - We may not be able to meet all those demands with the same measure, especially if it's normalized.

    **V3**: wasted votes at L3.

    - Here we can use the outcomes/party affiliations, either ex ante or ex post.
    - This should capture the size of the "flat" region in which a change in $r_s$ does not affect $r$.
    - That is, it should capture "waste from districts".
    - Ideally it would also depend on the national margin.


    - One idea: $x_i = 0$ for losing party, $x_i = \frac{1/2}{p_s}$ for winning party. Harsh for losers but basically captures the winner-take-all nature of state electors.
    - Another idea: $1 - \frac{L_s + (W_s - \frac{1}{2})}{n_s} = \frac{1}{2} - |p_s - \frac{1}{2}|$
      - $p_s = 0, 1 \to 0$, $p_s = \frac12 \to \frac{1}{2}$.

    - Might be better to think about "influence on candidates"
      - Some function of the margin of victory with $f(0) = 1$, decreasing?
        - Could compare to national margin: $\frac{f(m_s)}{f(m)}$.
        - What function? tanh? or just $1 - 2m$.



    **V4**: probability of a decisive vote?
    - there's established theory here.


    **V5**: some kind of smoothed $\tanh$ derivative things?

    $$
    \text{sign}(r_s) \longrightarrow \sigma(r_s / \tau_s)
    $$

    - Can get V1 in the vicinity of $r_s = 0$ if we take $\sigma'(0) = \frac{1}{n_s}$, maybe?

    **V6**: some other interpretation of the derivative $\frac{\partial r}{\partial  v_{s,i}}$, like an expectation over permutations of voters or something.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Measures

    Based on values?
    - mean absolute deviation (MAD)
    - mean square deviation (MSD), or root
    - Shannon entropy of the set $\{x_i\}$, or perhaps relative entropy to the uniform

    **M1**. Apportionment only, L2

    **M2**. Wasted-vote efficiency gap?
    - wasted votes assigning zero value to losers feels weird, but maybe that's right for winner-take-all.
    - [see here](https://www.brennancenter.org/sites/default/files/legal-work/How_the_Efficiency_Gap_Standard_Works.pdf)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Third Parties?

    TBD
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    value functions V(x)....
    """)
    return


@app.cell(hide_code=True)
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
