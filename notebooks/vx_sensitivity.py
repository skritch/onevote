import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import altair as alt
    import pandas as pd

    import viz


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Better than Wasted Votes...
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    But WVV is not enough to fix the problems with "wasted votes" per the standard definition.

    A few problems are:
    1. As before, the question of *which* votes were wasted on the winner side, which is easily handled by averaging.
    2. Second, that "wasted votes" considers half of the votes in even a *general election* as wasted, which is unreasonable.

    This is not a useful view, to my eye, because those voters *did* have an influence on the results of the election—they produced incentivizes on the candidates, parties, and platforms! In a general election, [median voter theorem](https://en.wikipedia.org/wiki/Median_voter_theorem) applies, at least in spirit: the winning candidate will be something like the one preferred by the median voter—every voter in a general election at least possesses the power to "move" the median, though, whether this affects the eventual candidate depends on the relationships of the candidates themselves to that median.

    The primary purpose of a definition of "wasted votes" should be to characterize the loss of _influence_ brought about by the winner-take-all elections in the states and districts. It is not *really* the case that the votes typically considered "wasted"—winners in excess of 50% and the losers—have zero influence: they *are* able to move the median within the state, and this in turn can the median nationally. But the effect is diminished relative to a general election.

    ---
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Let us try to make this idea concrete.

    Let $R$ be the sum of the votes of in an $N$ member election, with no abstentions and $N$ odd (so there are ties):

    $$
    R = \sum_x v(x)
    $$

    Each vote takes a value in $v(x) \in \{0, 1\}$, so $R \in [0, N]$. We might think of a $R$ as a random variable on the state space $\{0, 1\}^N$, but we won't imagine the outcomes are "random" in any way—$R$ here is really the "decision criteria" which decides the election. The margin of victory for party "1" we'll call $M = R - \lfloor\frac{N}{2}\rfloor$.

    In a general election, every voter has the power to move $R$ by 1:

    $$
    \frac{dR}{dv(x)}\bigg\vert_{v(x) = 0} = 1
    $$

    In a weighted election (such as that conducted by the states in the electoral college) $R$ is  instead:

    $$
    \begin{align}
    R = \sum_s e_s v(s) \quad\quad\quad\quad\frac{dR}{dv(s)}\bigg\vert_{v(s) = 0} = e_s
    \end{align}
    $$

    In this view, no vote is "wasted", because all votes have an equal effect on $R$. We won't think now about what effect $R$ has on the candidates or their platforms, but we assume it has some effect, representing the power of voters to influence candidates.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Now we consider a two-tiered election according to scenario P3. The state votes are now:

    $$
    v(s) = \begin{cases}
    1 & R_s \ge \frac{n_s}{2} \\
    0 & R_s < \frac{n_s}{2}
    \end{cases}
    $$

    with $R_s = \sum_{x \in s} v(x)$

    For any particular set of votes in the state $\{ v(x) \mid x \in s\}$, $R_s$ is decided by winner-take-all, and the individual voters have no further effect on the national election. We've already taken a few approaches here:
    - for Apportionment Value, we simply assigned each voter the average influence of all voters' influences on the national election, giving a value $\propto \frac{e_{s(x)}}{n_{s(x)}}$
    - for Pivotality Value, we assigned values to voters in proportion to the number of all possible election outcomes they personally "decided", which was approximately $\propto \frac{e_{s(x)}}{\sqrt{n_{s(x)}}}$.
    - for Wasted Vote Value, we assigned values to the winning party's voters in proportion to their fraction of the winning party's votes: $\propto \frac{e_{s(x)}}{R_{v(x),s(x)}}$ for $v(x) = v(s(x))$ only.

    How to do better than these?
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    We said that, in a general election, each voter moves the decision criteria $R$ by 1 unit. Two votes moves it by two units, etc. The growth rate of the margin with respect to "the number of votes we flip $0\to 1$" is $1$. Or, if we consider $R$ as a function of the vector of votes $\mathbf{v} = (v(x_1), v(x_2), \ldots)$, $R(\mathbf{v}) = \sum_{x} v(x)$,

    $$
    R(\mathbf{v} + \delta \mathbf{v}) = R(\mathbf{v}) + R(\delta \mathbf{v})
    $$

    In a two-tiered election, the national decision boundary $R$ will not move until a state moves by half of its margin $\frac{M_s}{2} \approx R_s - \frac{n_s}{2}$, at which point it moves by $e_s$ units in our scaled system). These are votes which would have to defect from the winning party to the losing party—but each vote *for* the losing party votes narrow this gap, just as each for vote for the winning party increases it.

    To be concrete, let's imagine a given state has a population $n_s = 100$ and casts $R_s = 60$ votes for party "1", with $40$ for party "0", for a margin of victory of $M_s = 20$. At this margin, one voter altering their vote doesn't change the national result, but 10 voters defecting from "1" to "0" would. The main effect of each vote actually cast is to move this margin.

    In this view, the national $R$ is "insensitive" to small $\delta \mathbf{v}_s$....


    just confused, overall.

    need to be thinking about votes as mediating a causality: "preferences -> candidates -> votes -> winning preference".
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
