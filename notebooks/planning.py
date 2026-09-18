import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Basic Notation

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
    # Philosophical Considerations for Value and Measure Design

    Trying to read about these topics online, I am led to the conclusion that the field (or the part of it which rises to the surface on Wikipedia and the like) is quite muddled. The point of all the structure I am establishing here is to un-muddle things.

    As above, our measures may turn out to target any of the levels L1... L6 above. My ambition, for the presidential election, is to target:
    - L2. Apportionment
    - L3. Waste
    - L6. Missing Votes

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
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
