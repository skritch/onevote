# /// astro
# title: Introduction
# description: How do we define the "value" of a vote?
# ///

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Our goal is to be able to answer the following two questions:

    **Q1**. What is the relative value of a certain person's vote in an election?

    **Q2**. How "fair" is an election?

    It will be useful to be fairly systematic about these problems. We will adopt a convention of labeling many of the ideas we talk about with boldfaced identifiers. So the two questions above are **Q1** and **Q2**.

    An answer to **Q1** question will be called a "value", and will be labeled like **V1**, **V2a**, and similar.

    An answer to question **Q2** will be called a "measure" (of fairness) and will be labeled like **M1** or **M2.3**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Vocabulary

    ## Voting Systems


    A "voting system" is a procedure by which a population of voters elects a candidate for office.

    We will characterize voting systems by a number of distinctions:

    **Single-winner** vs. **multi-winner**: whether a single representative is elected or many are. Essentially all state and national U.S. elections are single-winner at present.


    **Winner-take-all** vs. **proportional**: whether the winning candidate or party receives *all* of the representation, or some amount proportional to the number of votes they receive. Essentially all state and national U.S. elections are winner-take-all, being single-winner elections.

    A notable instance which *could* be multi-winner and proportional, but usually isn't, is the assignment of Electoral College electors to states: at present all but two states assign all of their electors to the winning presidential candidate in the state.


    It would be feasible for U.S. states to assign House representatives in a state-wide multi-winner election, rather than by holding a winner-takes-all election in each district. In this case, representatives could be assigned proportionally.

    **Plurality** vs. **majority**: whether the candidate can win simply by having the *most* votes, or if they must have more than 50% of the total votes cast. Essentially all U.S. elections are decided by a plurality.

    The confusing term **first-past-the-post** is sometimes used to describe a plurality & winner-take-all election, which necessarily must be single-winner.

    **Ranked-choice** vs. **single-choice**: does a voter rank multiple candidates in order of preference, or do they cast their vote for a single candidate?

    Ranked-choice can be used for either single-winner or multi-winner elections. Various algorithms can be used to determine the winner(s). In the case of single-winner elections a common one is **instant runoff**, where the least-preferred candidate is eliminated, and the voters who placed them first have their votes assigned to their next-highest candidate instead.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Populations

    A "population" consists of all of the people living in a place, who may or may not be voters. There are a lot of ways of defining "populations", and it will helpful to distinguish them clearly as follows:

    | Label      | Full Name | Description | Approx Nationally in 2020 | Variable in dataset |
    | ----------- | ----------- | ----------- | ---- | ---- |
    | **P**      | population       | the census residential population of a state  |  331.4M | |
    | **AP**   | apportionment population        | P + overseas federal employees and their dependents| 331.8M[^ap] | `apportionment_population` |
    | **VAP**   | voting-age population | residents 18 and older  | 258M | `vap_estimate` |
    | **CVAP**   | civizen voting-age population   | VAP - non-citizens  | 238M |  |
    | **VEP**   | voting-eligible population  | CVAP + eligible voters overseas <br/> - people prohibited from voting, e.g. felons | 234M | `vep_estimate`
    | **VRP**   | voting-registered population  | Number of registered voters | 210M |
    | **VP**   | voting population  | Actual number of voters | 159.7M | `votes_total`

    We will typically refer to these variables by their labels like **AP**, **VAP**, etc.

    For the purposes of calculating whether an election is fair, or the value of a vote, we will mostly be concerned with **VEP**.


    [^ap]: The census definition of AP excludes the ~700k residents of D.C., who have no representation in the House (except for 1 non-voting delegate), and are then granted their 3 electors by the 23rd Amendment. Under that definition the total would be 331.1M. Our `apportionment_population` variable differs from this in that it does include D.C., as we will want to assign D.C. an AP : elector ratio.

    ---

    Clearly there is a major difference between **VEP** and **VP** in the United States. The difference is "voter turnout".

    We may also need to estimate turnout to determine how close an election is likely to be. We have options:
    - *ex post* actual turnout
    - *ex ante estimates* of turnout: polling, voter registrations, statistical models, or simply "what happened last time"
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Parties

    A **party** is a voluntary coalition of voters. A party will usually vote for the same candidate, and also might choose their candidates for a general election by primaryign or caucusing.

    The term **third-party** is used for all parties other than the two most popular parties.

    When we want to describe the population of voters affiliated with a party we will use the same labels as for populations, but prefixed with *P*, such as **PVEP** and **PVP**.

    An individual voter does not always have a "true" party affiliation, so it is not necessarily possible to define the number of voters per party. At times we will distinguish between:

    - "Actual" or *ex post* election outcomes—how many votes are actually case for each party's candidate (or in some system, for the parties themselves).
    - *ex ante* estimates of election outcomes—any kind of forecast of actual election outcomes. Examples include polls, statistical models, or simply "whatever happened in the previous election"
    - "Actual" party affiliations—if we asked them to vote right now, which party would a given voter prefer?
    - Estimates of party affiliations, such as registered members of parties, polls, and statistical models.
    - Platform preference—the similarity of between an individual's political views and party's platform.


    Note that "actual" party turnouts are not necessarily a better measure of party affiliation than are *ex ante* estimates, as voter turnout is causally downstream of the election system itself; for example a party with no chance of winning may see extremely low turnout.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Well-known Defects of Voting Systems

    - Wasted Votes
    - Spoilers
    - Strategic Voting
    - Gerrymandering
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Levels of Analysis

    There are many ways to go about assigning the "value" of a vote. We will organize the problem by distinguishing between the following "levels of analysis", based on the degree to of real-world information employed, as opposed to purely theoretical problems.

    **L1**: **Theoretical Problems**

    Here we have "purely-theoretical" issues with voting systems, without taking into account *any* real-world data such as actual populations or party affiliations.

    For example, the U.S. presidential election, with its winner-take-all assignment of electors to states, can be characterized in various ways to be less "fair" than a fully-general election would be, in that fewer voters' votes "matter". And we can assign some intermediate degree of fairness to a system which assigns electors within single-elector districts, or or a system assigning electors *proportionally* within their states.

    Likewise the possibility for "third-party spoilers" and "strategic voting" are inherent to a voting system, regardless of the apportionment, turnouts, or actual party affiliations.


    **L2**. **Apportionment**

    Here the main issues is the inequality of apportionment, such as the disproportionality in the assignment of senators, representatives, and electors to states. Wyoming is the most extreme case, with 600k people, one representative, two senators (300k/ea), and three electors (200k/ea), compared to California with 52 representatives (760k/ea), two senators (20M/ea), and so 54 electors (740k/ea).

    We can also place here any arguments about how apportionment is calculated, e.g.:
    - Inclusion of non-citizens, illegal aliens, or felons
    - Whether overseas territories are apportioned representation

    **L3**. **Party Affiliation**

    Once we take into account the actual party affiliations of voters (defined in any of the ways described above), we encounter the issues of:
    - Wasted votes
    - Gerrymandering (intentionally-engineered wasted-votes)
    - Swing states
    - Third-party Spoilers
    - Strategic Voting


    **L4**. **Feedback Effects**

    The basic idea here is that the choice of voting system dictates how the political process plays out. For example, the votes of swing-state voters matter far more for national victories than do non-swing states. Political parties will specifically target swing-state voters with their choices of candidates and platforms, and their canvassing and advertising spend, giving vastly more power over the electoral outcome to swing-state voters relative to others.

    - ...choice of candidates
    - ...choice of platforms
    - ...canvassing, ad spend, etc.
    - ...voter turnout: whether people vote depends on the perception that their votes will matter.

    These feedback affects quickly complex, and we will generally not attempt to take them on.

    But we should ought to this category in mind when considering *counterfactuals*. For example, the voter turnout we actually see is the one arising as a result of this sort of feedback from the voting system. we cannot simply say "what would have been the outcome of a national general election under such-and-such system?", because different voters would have turned up to vote, candidates would have positioned themselves and advertised differently, etc.


    **L5**. **Expression of voter preferences**

    Here we place:
    - Effects of primarying or caucusing systems and party conventions.
    - Incentives on candidates to take certain positions, such as the "median voter theorem" and "Hotelling's law".


    **L6**. **Incorrect or Missing Votes**

    Issues such as:
    - Voters unable to take time off or travel to polling place.
    - Lost ballots
    - Fraud
    - Restrictions on the franchise itself: unreasonable ID requirements, intimidation, poll taxes, etc.
    - Philosophical issues with the franchise itself, such as the exclusion of overseas territories
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Presidential Electoral Scenarios

    We'll start with these:

    **P1**. Actual electoral college: electors assigned by winner-take-all in all states but Maine and Nebraska, which assign their House electors to winners of districts. Arbitrarily many third parties.

    **P2**. Simplified electoral college: electors assigned by winner-take-all in all states. Two parties only.

    **P3**. Districtized Electoral College: assign senate electors to state winners, assign district electors to district winners in all states.

    **P4**. Party-proportional Electoral College: assign state electors, including senate electors, in proportion to vote share in each state. This requires choosing method of handling remainders. The simplest method is to assign the remaining elector(s) to parties in descending order of their leftover votes.

    **P5**. A national general election.

    ---

    We can also label some lower-priority ideas:

    **P6**. National ranked-choice, probably with instant-runoff.

    This is very interesting. It would be hard to come up with realistic data for this, but I imagine someone has estimated it.

    **P7, P8, and P9**. As P2, P3, and P4, but without the 2 Senate electors per state.

    **P10**. Ranked-choice/instant-runoff-type schemes to determine electors at the state level.

    **P11**. As P10 but at the district level.
    """)
    return


@app.cell(hide_code=True)
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
