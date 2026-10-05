import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Philosophical Considerations for Value and Measure Design

    Trying to read about these topics online, I am led to the conclusion that the field (or the part of it which rises to the surface on Wikipedia and the like) is quite muddled. The point of all the structure I am establishing here is to un-muddle things.

    As above, our measures may turn out to target any of the levels L1... L6 above. My ambition, for the presidential election, is to quantify:
    - L2. Apportionment
    - L3. Waste
    - L6. Missing Votes

    #### Simplicity

    That is, "purely theoretical" (L1), "feedback" (L4), and the "underlying preferences" (L5) are out of scope, though we may still take them into consideration.

    A reasonable voting system should be *simple*; it is as important that it "feel" fair as it is that it "be" fair. Hence we must not be too theoretical.

    #### Wasting Votes

    I want to additionally place the following stipulation on measures of fairness:

    *A fully general election for a single office is perfectly fair*.


    This immediately rules out a lot of "wasted vote" measures which treat _all the losing candidate's votes_ as wasted. This is a pointless view: those votes may have been wasted, but they still counted as much as every other vote. (We will still calculate these, though, as they are seen in the literature.)


    #### Probabilities

    This also steers us far away from measures which attempt to quantify "the probability of a vote being decisive", which to me seems rather nonsensical: who, in a general election split by 1 vote, was the "decisive" voter? Was not each voter decisive? It is still sillier to introduce some sort of distribution over "orderings": the underlying problem does not have an ordered structure; your result will derive solely from the addition of this structure; it does not mean anything.

    #### Incentives?

    Instead, what we want to measure is something like the "incentivize for a candidate to cater to a voter". In the view of a candidate trying to win votes, all votes in a general election trade one-for-one against each other--hence, all are equal.

    That is: our philosophical outlook is that we would like to measure the _influence of a voter's preferences on the policies/platform which result from the election_ (bringing in a bit of L6), rather than the _influence of their vote_. The majority of the influencing happens before the time of the vote!


    #### Quadratic / weighted voting

    This is ridiculous, we won't consider it. Stop trying to assign numbers to preferences.

    #### Medians?

    The "[median voter theorem](https://en.wikipedia.org/wiki/Median_voter_theorem)" is a central elementary result of the field. This says that, under reasonable conditions, an election will choose the candidate *preferred* by the median voter. (Note this is not quite the same thing as "reflecting the views of the median", as it takes the candidates themselves as fixed.)

    Does this not imply that candidates are going to primarily interested in changing the views of voters near the median? They will have almost no incentive to appeal to outliers.

    I don't think this matters, for a few reasons.
    - If a population's preferences were truly one-dimensional, and if we ignored every detail except for these preferences, then tbe "correct" winner would indeed be the one who reflects the views of median voter. Who else would it be??
    - Real populations' preferences are not very one-dimensional at all; less so in the present day than ever in my lifetime.
    - The fact that outlier voters can reject a candidate by *not voting* gives them considerable power over the position of the median *actual vote cast*.

    We might think of the an voter as having two votes; abstained casts one to each candidate while a vote for a candidate casts both to them. Generally a candidate can improve their chances by targeting not only undecided voters near the median (who could be persuaded to switch one or both of their two votes, but also outlying voters who might otherwise abstain.)


    ----

    Let us also enumerate briefly some of the ways a real election differs from an "idealized" one:
    - the candidates (or their views) are selected (or change) on the basis of the electorate's own views (this is good--a representative should represent!)
    - candidates have noisy/biased signals of the electorate's preferences, and v.v.
    - candidates have inherent levels of "quality" and/or "likeability" as people, independent of their political views.
    - candidates have some power to *alter* the views of the electorate. (Potentially a lot of power, as the Trump era demonstrates.)

    All of these are certainly true, but should not really affect whether an election is "fair", at least to first order. This is, really, a simpler problem than that.
    """)
    return


@app.cell(hide_code=True)
def _():
    import marimo as mo

    return (mo,)


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
    \text{V}(x) = ~~ ???
    $$

    We will always define a "value of a vote" such that the values across an entire population sum to $N$ (for some population variable), such that the "baseline" value of a vote is $1$, as opposed to $\frac{1}{N}$. IThe project is called "OneVote", after all.)

    A valuation will usually assign the same value to a lot of voters, such as all the voters in a state, in which case we could write expressions like

    $$
    N = \sum_x \text{V}(x) = \sum_s n_s \text{V}(s)
    $$

    where $\text{V}(s)$ is the value the valuation assigns to *each* voter in state $s$.

    (This might be a bad idea; we might prefer $\text{V}(x \mid s)$.)

    Specific valuations will be written as Roman text and will always end in "V", like

    $$
    \text{AV}(x) = \frac{e_{s(x)}}{E} \cdot \frac{N}{n_{s(x)}}
    $$

    When we want to refer to the actual *vote* cast by a voter $x$ we'll use $v(x)$, which will take values in some $P$ of parties, often just $\{0, 1\}$.

    The result of an election will generally be a lower-case $r \in P$ or $r(s) \in P$. An upper-case $R$ will be used for the actual count of votes (with a sense like a random variable). $R$ alone will stand for "votes for party 1" in a two-party election $\{0, 1\}$, while $R_p$ will stand for the count of votes for a particular party. Likewise for $R(s), R_p(s)$. The number of electors won by party $p$ in state $s$ will be written $e_p(s)$.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
