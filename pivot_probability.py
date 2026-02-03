import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import altair
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
 
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # **V2**: Pivot Probability
    """)
    return


@app.cell(hide_code=True)
def _():
    # This dataset is prepared in https://github.com/skritch/election-datasets and uploaded to Kaggle for general use.

    import kagglehub
    from kagglehub import KaggleDatasetAdapter

    # Load the latest version
    data = kagglehub.dataset_load(
      KaggleDatasetAdapter.PANDAS,
      "samkritch/u-s-presidential-elections-by-state-1976-2024",
      'presidential_elections_1976_2024.csv',
    )

    # data.head()
    return (data,)


@app.cell(hide_code=True)
def _(data):
    # Add apportionment_value column to entire dataframe
    # For each year, AV = (state_electors / state_population) * (national_population / national_electors)

    data_with_av = data.copy()

    # Calculate national totals by year
    national_totals = data_with_av.groupby('year').agg({
        'state_electors': 'sum',
        'state_population': 'sum'
    }).rename(columns={
        'state_electors': 'national_electors',
        'state_population': 'national_population'
    })

    # Merge national totals back to dataframe
    data_with_av = data_with_av.merge(national_totals, left_on='year', right_index=True)

    # Calculate apportionment value
    data_with_av['apportionment_value'] = (
        (data_with_av['state_electors'] / data_with_av['state_population']) *
        (data_with_av['national_population'] / data_with_av['national_electors'])
    )

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Here is the situation so far:
    1. We have calculated a "value function" for voters called Apportionment Value (AV) for the U.S. presidential election, which is a function of the state populations and elector counts alone (making it a level 2 (L2) measure, by my system). AV is indifferent to the "winner take all" nature of state elections, so it's not very useful.
    2. We tried briefly to calculate a "Winner-Take-All Value" WTAV to account for this, but quickly realized that every WTA election "wasted" 50% of votes; this value function was insensitive to the *size* of districts, which contradicted our intuition that larger districts are more unfair.

    The extension of these two value functions to various presidential elections scenarios (P1... P5) is obvious and not very interesting.

    Now we can go two directions:
    3. (a) Attempt to devise a measure, still at L2, which capture winner-take-all elections *and* accounts for the size of the states.
    3. (b) Continue with (2), but look at L3--calculate the *actual* wasted votes in various elections and under various scenarios; the WTAV measure may still be interesting these cases.

    Here we'll take on 3a.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # District Size

    The problem with WTAV was that, intuitively, it feels like, even if you are going to have some kind of intermediaate winner-take-all state or district, smaller districts should be more fair, all else being equal. Imagine electors going as WTA in a full state vs. dividing the state up into House districts and assigning electors by district--clearly the second is better. How?

    Furthermore, small districts should be quantitatively more fair than larger districts even without knowing the party affiliations within the state. Later when we discuss gerrymandering we will quantify the ways that even *small* districts can be gamed, but that will be an additional effect in addition to the general sense of unfairness we seek here.

    If we don't know the actual party affiliations (or votes), it feels like, to make any progress, we need to try to characterize what results an electoral system would produce for *any* election result, or at least for any "typical" election result.

    The absolutely simplest way to approach this is, I think, to postulate that party affiliations (party A or B, say) are effectively random, with probability $P[v(x) = A] = p$, i.e. each voter obeys a $\text{Bernoulli(p)}$ distribution. Then the resulting number of votes going to A in an election of $n$ voters is distributed as $\text{Binomial}(n, p)$.

    We'll additionally take $p = 0.5$, meaning that the result--the actual votes--of an election of $n$ voters are distributed as a $\text{uniform}(\{0, 1 \}^N)$.

    That votes are "random" is of course completely unrealistic. We can justify this approach somewhat by noting that we need not be thinking of $\text{uniform}(\{0, 1 \}^N)$ as describing a *probability* at all, nor any kind of random event. It merely reflects our own indifference to the actual election results: all possible results are, at this point, under consideration.

    This we represent by a uniform measure on the set of all possible outcomes. This of course directly implies a $\text{Binomial}(n, 0.5)$ measure on the set of vote *counts*, and assigns each candidate the win in $p=50%$ of cases.

    Later we can imagine adding information (e.g. within-state correlations), or excluding some outcomes (extremes, or those inconsisent with polls, etc), but it is likely to expect that the "shape" of the resulting distribution, in the vicinity of its average, given whatever information we have, still resembles the shape of a binomial. (Approximately I have "maximum entropy inference" in mind here, but we'll deal withn that when we come to it.)


    The choice of $p=0.5$ in particular, is suspect, as real elections, it seems as though this should hold in any particular state. But to treat $p=0.5$ as the *national* probability will imply some distribution of means in the individual states: some will be dominated by one party, some the other; some will be swing states, some bastions.

    At the national level, $p=50%$ can be justifeid by observing that, in a two-party system, the parties will tend to converge to platforms which appeal to approximately 50% of the electorate: if they are not competitive, they will tend on average to cede points until they are. (I believe there is a theorem describing this phenomenon for some toy model of political parties.)

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's choose some notation. As before $x$ will represent a voter, and $s(x)$ their state. The random variable $X_i$ will represent the vote of voter $x_i$, and the random vector $\mathbf{X} = (X_1, \ldots, X_N)$ represents the votes of the entirely population. $R$ will be the random variable of the sum of the votes, with $R_1$ as the number of "1" votes and $R_0$ the number of $0$ votes. We have:

    $$
    R_1 - R_0 = \sum_{i=1}^N X_i
    $$

    $P$ will be a random variable for the outcome of entire election, with $P=0$ indicating the event that the first or "0" party wins, while $P=1$ is the event that the second or "1" party wins.

    For now let us assume $N$ is odd and very large, and that voters must cast a vote one way or the other; we are far from considering abstentions.

    Per the above

    $$
    \begin{align}
    X_i &\sim \text{uniform}(\{0, 1 \})\\
    \mathbf{X} &\sim \text{uniform}(\{0, 1 \}^N)\\
    R_1 &\sim \text{Binomial}(N, 0.5)\\
    P = 1_{R >= 0} &\sim \text{uniform}(\{0, 1 \})
    \end{align}
    $$

    Note there are $2^N$ possible results in the set $\{0, 1 \}^N$, and $N+1$ possible vote totals.

    ----

    Now, how do we want to define our actual "measure"?

    - pivotality 1/N?
    - pivotality as "the remaining votes come out to exactly a margin of 1".
      - ... influence on candidates?
      -  "Banzhaf"
      -  Penrose limit
      -  Shapley-Shubik?
    - or.. pivotality as, if margin = 1, every voter on the winning side is pivotal?
    - state pivotality. CLT for small e_s.



    - look at distribution of shape outcomes (each binomial)
    - P(state being close) ~= ? within k? within n_s . f??
    - can we say what fraction of voters are likely within ...?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Pivotality

    One line of investigation is to ask: what is the probability that a given voter "decides" the entire election--that, if not for their vote, the result would have been different?

    We will use the term "pivotal" for a voter whose vote decides an election, however we choose to define it.

    I should note immediately that the idea here is not to treat elections as though every voter should have a shot at being the decisive vote. I expect that this probability, even in our toy "uniform distribution", is going to be extremely small; even in a real election which is quite close the probabilities will be quite small; we are not trying to argue people should vote because they might have a shot at changing something.

    What I will be interested in is the *relative probabilities*--the ratio between this probability for different voters--which are a way of characterizing the election system itself.

    And, I mention again, the point of a fair electoral system is not actually to give every voter explicit "power" to change the outcome, but rather to give voters *influence* of the candidates and parties: the election system itself, I believe, should not negate the influence of certain voters arbitrarily.

    Now, how shall we describe "pivotality" mathematically?

    Let us first consider a single general election among $N$ voters with no states.

    The very first definition of "pivotal" you might reach for is this: one side or the other must cast the $(\frac{N}{2}+1)$th vote. This voter is "the pivotal one". Amidst $N$ voters, each is equally likely to be in the pivotal spot (I suppose we randomize over *order*) so the probability is

    $$
    P[\text{vote } i \text{ is pivotal}] \stackrel{?}{=} \frac{1}{N}
    $$

    But this is not very useful. For one, it doesn't make sense to think of the votes as occurring in any particular *order*--wouldn't every one of the winning voters be equally "pivotal"? Anyway, the generalization of of this notion to an electoral college is just going to be something $\propto \frac{1}{n_s} \cdot \frac{e_s}{E}$, which gives us AV again.


    Let us try a narrower definition. Fix a single voter $x_i$ and ask: what is the probability that the remaining $(N-1)$ votes sum to exactly 0, such that $x_i$ decides the whole election? We need exactly $\frac{N-1}{2}$ of the remaining $(N-1)$ votes to be "1". We'll depict the sum of these votes by the random variable $R^{(N-1)}. The number of ways to realize this result is given by a binomial coefficient (with $2^{-(N-1)}$ as the normalization):

    $$
    \begin{align}
    P[R^{(N-1)} = 0] &= {N - 1 \choose \frac{N-1}{2}}2^{-(N-1)}  \\
      &= \frac{(N-1)!}{(\frac{N-1}{2})! (\frac{N-1}{2})!}2^{-(N-1)}
    \end{align}
    $$

    Since the numbers involved are large we can use a Stirling approximation to the factorial, $n! \approx \exp(n \log n)$. We get:

    $$
    \begin{align}
    \frac{(N-1)!}{(\frac{N-1}{2})! (\frac{N-1}{2})!} &\approx \exp{\left( (N-1)\log (N-1) - 2 \cdot (\frac{N-1}{2}) \log (\frac{N-1}{2})\right)} \\
      &= \exp{\left( (N-1)(\log (N-1) -  \log (\frac{N-1}{2}))\right)}\\
      &= \exp{\left( (N-1)\log \frac{N-1}{(N-1)/2}\right)}\\
      &= \exp{\left( (N-1)\log 2\right)} \\
      &= 2^{N-1}
    \end{align}
    $$

    ... oops: that Stirling approximation was *so* approximate that it assigned the entire measure of the space to the single mean value. That will just cancel with the normalization, giving $P[R^{(N-1)}] = 0] = 1$.

    The two-term approximation $n! \approx \exp(n \log n -n)$ because the errors in the numerator and denominator will cancel. We need a third term: $n! \approx \exp(n \log n - n + \log \sqrt{2\pi n})$. With that the above is:

    $$
    \begin{align}
    \frac{(N-1)!}{(\frac{N-1}{2})! (\frac{N-1}{2})!} &\approx 2^{N-1} \exp{\left( \log \sqrt{2 \pi N} - 2 \log \sqrt{2 \pi \frac{N-1}{2}}\right)} \\
    &= 2^{N-1} \exp{\left( \log \sqrt{2 \pi N} - \log (\pi (N-1))\right)} \\
    &= 2^{N-1} \exp{\left( \log \sqrt\frac{2}{\pi} \frac{\sqrt{ N}}{ N-1}\right)} \\
    & \approx 2^{N-1}  \sqrt\frac{2}{\pi}  \frac{\sqrt{ N}}{ N-1}\\
    \end{align}
    $$

    The final factor $\frac{\sqrt{ N}}{ N-1}$ is what we're interested in. For large $N$ is this is approximately $\frac{1}{\sqrt{N}}$, which gives us "scaling" of our pivotal probability with the population size:

    $$
    \begin{align}
    P[\text{vote } i \text{ is pivotal}]  &\stackrel{?}{=} P[R^{(N-1)} = 0] \\
      &\propto \frac{1}{\sqrt{N}} \\
    \end{align}
    $$

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This result $P \propto \frac{1}{\sqrt{N}}$ is new to us, and is our result.

    - it's sort of a weird thing to measure: most election results aren't decided by one vote!
      - how many are? $P(R = 1 \cap R = -1) = 2 \cdot 2^{-N} \cdot {N \choose (N+1)/2}$
    - if you know your vote isn't this close, does this matter?


    other interpretations:
    - width of the neighborhood of 0
    - probability of the vote being close at all


    normalization?


    weighted election?
    - small-N case: integer partitions, Banzhaf power index
    - large-N case: CLT.



    - multi-tier election

    - probability of swing states and the like
    """)
    return


@app.cell
def _():
    
    return


if __name__ == "__main__":
    app.run()
