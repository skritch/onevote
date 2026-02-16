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

    I won't attempt to take on this level.

    It will be easier to work at L2 or L3, which take somewhat more of reality into account.

    **L2**. **Voting systems + state populations + apportionment**.
    1. Here the main issues are is the inequality of apportionment, such as:
      - Unequal apportionment of electors to states. In the U.S. each state has 3 minimum. Wyoming receives 3 electors for only 600K people (200K/elector) while California has 54 electors for 40M (740K / elector).
      - Discrepancies due to winner-take-all assignments instead of electors voting with their associated district or party-proportionally.
      - Rounding issues
    2. Any philosophical issues with the calculation of apportionment, e.g. illegal aliens being counted, exclusion of overseas territories, ages under consideration, etc.

    **L3**. **Voting system + population + party affiliations**.
    1. Wasted votes, in some sense. Here we should be able to characterize "swing states"--states where every vote is inherently much more likely to affect the overall outcome, just because the election is likely to be close and to have a marginal effect on the national election. How wasted a vote is will depend on the party affiliation (ex post or ex ante, see below).
    2. Gerrymandering (which is really a way of engineering wasted-votes)
    3. Spoilers, i.e. 3rd party candidates stealing votes from major parties and the like

    Here "party affiliation" might be defined in various ways:
    - *ex post* actual election outcomes (note this is not necessarily a better definition than *a priori* estimates, as it is causally downstream of the election system itself, see L4.)
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

    It will likely be useful to try to characterize wrong/lost/fraudlent votes as affecting the value of *everybody*'s political expression, regardless of their effect on the outcome themselves—an L2 effect rather than L3. A kind of "information loss" comes to mind.


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
    ## Population Variables

    We'll be making a lot of use of "populations", and it will helpful to be clear about what we mean.

    The following tables lists the different populations variables we might use:

    | Variable      | Full Name | Description | Nationally in 2020 | In dataset? |
    | ----------- | ----------- | ----------- | ---- | ---- |
    | P      | population       | the census residential population of a state  |  331.4M | |
    | AP   | apportionment population        | P + overseas federal employees and their dependents - indigenous populations "not taxed" | 331.8M[^ap] | `apportionment_population` |
    | VAP   | voting-age population | all residents 18 and older.  | 258M | `vap_estimate` |
    | CVAP   | civizen voting-age population   | VAP - non-citizens  | 233M |  |
    | VEP   | voting-eligible population  | CVAP - citizens from voting, e.g. felons. | 231M | `vep_estimate`
    | VP   | voting population  | Actual number of voters | 158M | `votes_total`

    We will typically refer to these variables by their acronyms AP, VAP.

    TODO: work out exactly how and where P/AP differ in the census data itself.

    TODO: work out relationship of citizenship to VEP

    [^ap]: The census definition of AP excludes the ~700k residents of D.C., who have no representation in the House (except for 1 non-voting delegate), and are then granted their 3 electors by the 23rd Amendment. Under that definition the total would be 331.1M. My `apportionment_population` variable differs from this in that it sdoes include D.C., as we do want to assign it an AP : elector ratio.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ----

    It will help to give identifiers to the scenarios we would like to compare.

    ## Presidential Electoral Scenarios

    We'll start with these:

    **P1**. A national general election.

    **P2**. Simplified electoral college: electors assigned by winner-take-all in all states. Two parties only.

    **P3**. Actual electoral college: electors assigned by winner-take-all in all states but Maine and Nebraska, which assign their House electors to winners of districts. Arbitrarily many third parties.

    **P4**. Districtized Electoral College: assign senate electors to state winners, district electors to district winners, i.e. what Maine and Nebraska do today, in all states.

    **P5**. Party-proportional Electoral College: assign state electors, including senate electors, in proportion to vote share in each state.

    This requires choosing method of handling remainders. The obvious method is to assign the remaining elector(s) to parties in descending order of their remaining votes.

    -----
    Some lower priority ideas

    **P6**. National ranked-choice/instant-runoff.

    This is very interesting, but will be hard to come up with realistic data for this, but I imagine someone has estimated it.

    **P7, P8, and P9**. As P2, P4, and P5, but without the 2 Senate electors per state.

    **P10**. Ranked-choice/instant-runoff-type schemes to determine electors at the state level.

    **P11**. As P10 but at the district level.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    -----

    ## Philosophical Considerations for Value and Measure Design

    Trying to read about these topics online, I am led to the conclusion that the field (or the part of it which rises to the surface on Wikipedia and the like) is quite muddled. The point of all the structure I am establishing here is to un-muddle things.

    As above, our measures may turn out to target any of the levels L1... L6 above. My ambition, for the presidential election, is to target:
    - L2. Apportionment
    - L3. Waste
    - L5. Lost Votes

    That is, "purely theoretical" (L1), "dynamical" (L4), and the "underlying preferences" (L6) are out of scope, though we may still take them into consideration. A reasonable voting system should be *simple*; it is as important that it "feel" fair as it is that it "be" fair.

    I want to additionally place the following stipulation on measures of fairness:

    *A fully general election for a single office is perfectly fair*.[^general]

    [^general]: It may be said that this is a biased place to start from. Well--too bad. I think this is so obvious as to not be worth talking about. I really cannot think of a way any other system could be "fairer" than this, for a single office—it treats all votrers equally; that is a low bar to clear. And yet.

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

    We will use $n_s, n_d$ similar to represent the "population of state $s$ or district $d$", with variables like $S, D$ for the number of states or districts. These will sum to $N = \sum_s n_s$ across all voters. Here $n_s$ and $N$ may represent any of the population variables described above—we'll sometimes calculate the same quantity with different population variables. When we want to be specific we'll use a subscript $N_{AP}, N_{VAP}, \ldots$ or perhaps a text-function like $\text{AP}(s)$.

    We'll use the symbol $e_s$ for the electors assigned to state $s$, with $E = \sum_s e_s$ the total number of electors.

    Subscripts like $n_s$ and $e_s$ just given will generally represent parameters of the voting system or of reality, as opposed to results of the election or our analysis, which will be represented as functions.

    We'll use variables like $x, y, z$ to name particular voters. We'll write $x \in s$ to indicate that voter $x$ belongs to state $s$, and will also use $s(x)$ to represent the state to which voter $x$ belongs.

    Our general approach will be to attempt to define various "value of a vote functions" or "valuations", which will be some function of a voter like:

    $$
    V(x) = ~~ ???
    $$

    We will always define a "value of a vote" such that the values across an entire population sum to $N$ (for some population variable), such that the "baseline" value of a vote is $1$, as opposed to $\frac{1}{N}$. The project is called "OneVote", after all. A valuation will usually assign the same value to a lot of voters, such as all the voters in a state, meaning that its sum is:

    $$
    N = \sum_x V(x) = \sum_s n_s V(s)
    $$

    where $V(s)$ is the value the valuation assigns to *each* voter in state $s$.

    Specific valuations will be written as Roman text and will always end in "V", like

    $$
    \text{AV}(x) = \frac{e_{s(x)}}{E} \cdot \frac{N}{n_{s(x)}}
    $$

    When we want to refer to the actual *vote* cast by a voter $x$ we'll use $v(x)$, which will take values in some $P$ of parties, often just $\{0, 1\}$. The vote of a state (in an electoral college, say) will be $v(s)$.

    The result of an election will generally be a lower-case $r \in P$ or $r(s) \in P$. An upper-case $R$ will be used for the actual count of votes (with a sense like a random variable). $R$ alone will stand for "votes for party 1" in a two-party election $\{0, 1\}$, while $R(p)$ will stand for the count of votes for a particular party. Likewise for $R(s), R_p(s)$. The number of electors won by party $p$ in state $s$ will be written $e_p(s)$.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## TODO to think about

    Third parties.

    Abstentions.
    """)
    return


@app.cell(hide_code=True)
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
