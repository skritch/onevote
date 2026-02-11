import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import altair

    import viz


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # **V3**: Pivot Probability
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
      'pres_by_state_1976_2024.csv',
    )

    # data.head()
    return (data,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Introduction
    """)
    return


@app.cell(hide_code=True)
def _():
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
def _():
    mo.md(r"""
    ## Uniform Random Votes
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    The problem with WTAV was that intuitively, it feels like, "winner-take-all" in smaller districts should ought to "fairer" than in large districts. Imagine assigning a state's electors via WTA: assigning one elector to the winner of each House district is certainly more fair than assigning all the electors to the winner of the whole state.

    If we don't know the actual party affiliations (or votes), what do we do?

    One way to make progress is to try to characterize an electoral system would for *any* election result, or at least for any "typical" election result.

    The absolutely simplest way to approach this is to postulate that every election result is equally likely. We imagine each vote going to party "1" with probability $P[v(x) = 1] = 0.5$, i.e. each vote is distributed as a $\text{uniform}(\{0, 1 \})$ distribution. Then the resulting number of votes going to "1" in an election of $n$ voters will be distributed as $\text{Binomial}(n, 0.5)$ and the full result of $N$ votes is distributed as a $\text{uniform}(\{0, 1 \}^N)$.

    That votes are "random" is of course completely unrealistic. We can justify this approach somewhat by noting that we need not be thinking of $\text{uniform}(\{0, 1 \}^N)$ as describing a *probability* at all, nor any kind of random event. It merely reflects our own indifference to the actual election results: all possible results are, at this point, under consideration.

    This we represent by a uniform measure on the set of all possible outcomes. This of course directly implies a $\text{Binomial}(n, 0.5)$ measure on the set of vote *counts*, and assigns each candidate the win in $p=50%$ of cases.

    Later we can imagine adding information (e.g. within-state correlations), or excluding some outcomes (extremes, or those inconsisent with polls, etc), but it is likely to expect that the "shape" of the resulting distribution, in the vicinity of its average, given whatever information we have, still resembles the shape of a binomial. (Approximately I have "maximum entropy inference" in mind here, but we'll deal withn that when we come to it.)

    The choice of $p=0.5$ in particular, is suspect, as real elections, it seems as though this should hold in any particular state. But to treat $p=0.5$ as the *national* probability will imply some distribution of means in the individual states: some will be dominated by one party, some the other; some will be swing states, some bastions.

    At the national level, $p=50%$ can be justified by observing that, in a two-party system, the parties will tend to converge to platforms which appeal to approximately 50% of the electorate: if they are not competitive, they will tend on average to cede points until they are. (I believe there is a theorem describing this phenomenon for some toy model of political parties.)

    ---
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Let's choose some notation. As before $x$ will represent a voter, and $s(x)$ their state. The random variable $X_i$ will represent the vote of voter $x_i$, and the random vector $\mathbf{X} = (X_1, \ldots, X_N)$ represents the votes of the entirely population. $R$ will be the random variable of the sum of the votes. We have:

    $$
    R = \sum_{i=1}^N X_i
    $$

    $P$ will be a random variable for the outcome of entire election, with $P=0$ indicating the event that the first or "0" party wins, while $P=1$ is the event that the second or "1" party wins. Evidently $P = 1_{R > \frac{N-1}{2}}$.

    For now let us assume $N$ is odd, so there are no ties. Let us also assume $N$ is very large, and that voters must cast a vote one way or the other; we are far from considering abstentions.

    Per the above

    $$
    \begin{align}
    X_i &\sim \text{uniform}(\{0, 1 \})\\
    \mathbf{X} &\sim \text{uniform}(\{0, 1 \}^N)\\
    R &\sim \text{Binomial}(N, 0.5)\\
    P  = 1_{R > \frac{N-1}{2}} &\sim \text{uniform}(\{0, 1 \})
    \end{align}
    $$

    Note there are $2^N$ possible results in the set $\{0, 1 \}^N$, and $N+1$ possible vote totals.

    ----
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Pivotality
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    One line of investigation is to ask: what is the probability that a given voter "decides" the entire election--that, if not for their vote, the result would have been different?

    We will use the term "pivotal" for a voter whose vote decides an election, however we choose to define it.

    I should note immediately that the idea here is not to treat elections as though every voter should have a shot at being the decisive vote. I expect that this probability, even in our toy "uniform distribution", is going to be extremely small; even in a real election which is quite close the probabilities will be quite small; we are not trying to argue people should vote because they might have a shot at changing something.

    What I will be interested in is the *relative probabilities*--the ratio between this probability for different voters--which are a way of characterizing the election system itself.

    And, I mention again, the point of a fair electoral system is not actually to give every voter explicit "power" to change the outcome, but rather to give voters *influence* of the candidates and parties: the election system itself, I believe, should not negate the influence of certain voters arbitrarily.

    Now, how shall we describe "pivotality" mathematically?

    Let us first consider a single general election among $N$ voters with no states.

    The very first definition of "pivotal" you might reach for is this: one side or the other must cast the $(\frac{N}{2}+1)$th vote. This voter is "the pivotal one". Amidst $N$ voters, each is equally likely to be in the pivotal spot (I suppose we randomize over *order*) so the probability is

    $$
    P[\text{vote } x \text{ is pivotal}] \stackrel{?}{=} \frac{1}{N}
    $$

    But this is not very useful. For one, it doesn't make sense to think of the votes as occurring in any particular *order*--wouldn't every one of the winning voters be equally "pivotal"? Anyway, the generalization of of this notion to an electoral college is just going to be something $\propto \frac{1}{n_s} \cdot \frac{e_s}{E}$, which gives us AV again.


    Let us try a narrower definition. Fix a single voter $x_i$ and ask: what is the probability that exactly half of the other votes are "1", such that $x_i$ decides the whole election? We'll depict the sum of these votes by the random variable $R^{(N-1)}$. The number of ways to realize this result is given by a binomial coefficient (with $2^{-(N-1)}$ as the normalization):

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

    The two-term approximation $n! \approx \exp(n \log n -n)$ won't help, because the second terms of the numerator and denominator will cancel. We need a third term: $n! \approx \exp(n \log n - n + \log \sqrt{2\pi n})$. With that we get:


    $$
    \begin{align}
    \frac{(N-1)!}{(\frac{N-1}{2})! (\frac{N-1}{2})!} &\approx 2^{N-1} \exp{\left( \log \sqrt{2 \pi (N-1)} - 2 \log \sqrt{2 \pi \frac{N-1}{2}}\right)} \\
    &= 2^{N-1} \exp{\left( \log \sqrt{2 \pi (N-1)} - \log (\pi (N-1))\right)} \\
    &= 2^{N-1} \exp{\left( \log \sqrt\frac{2}{\pi} \frac{\sqrt{ N-1}}{ N-1}\right)} \\
    & \approx 2^{N-1}  \sqrt\frac{2}{\pi}  \frac{1}{\sqrt{ N-1}}\\
    \end{align}
    $$

    The final factor $\frac{1}{\sqrt{ N-1}}$ is what we're interested in. For large $N$ this is very nearly the same as $\frac{1}{\sqrt{N}}$, which gives us "scaling" of our pivotal probability with the population size:

    $$
    \begin{align}
    P[\text{vote } x \text{ is pivotal}]  &\stackrel{?}{=} P[R^{(N-1)} = 0] \\
      &\propto \frac{1}{\sqrt{N}} \\
    \end{align}
    $$

    ---
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    This result $P \propto \frac{1}{\sqrt{N}}$ is new to us. Let us briefly get a sense for it.


    The $\propto$ is a bit confusing: just how large *is* this probability?

    Take $N = 11$. The approximation above gives us ${10 \choose 5} \approx 258.4$, very close to the true value of $252$. There are $2^{10} = 1024$ possible outcomes of the first 10 voters, of which $\frac{252}{1024} \approx 0.246$ are ties, making the 11th voter pivotal. Of the $2^{11} = 2048$ total results, $252$ have voter 11 voting  "1" and the other $252$ have voter 11 voting "0", deciding the election in either case—still approximately one-fourth of the time.

    Likewise every other voter has the same probability of being pivotal. There are only $2^{11} = 2048$ outcomes of the full 11-way vote, so the pivotal cases for each voter cannot all be distinct. Consider: of the 252 cases where voter 11 is pivotal, in half of those voter 11 votes "1" and the "1"s win. Each of those cases is also a pivotal case for all of the other voters who voted "1"; if not for their vote the election would have been tied.

    Of the $2^{11} = 2048$ total outcomes, how many wound up being decided by a margin of 1 in either direction? The answer should be

    $$
    {N \choose \frac{N-1}{2}} + {N \choose \frac{N+1}{2}}
    $$

    which in this case is $462 + 462  = 924$, or a bit less than half of the $2048$ outcomes. These expressions will scale as $\frac{1}{\sqrt{N}}$ as well, and this probabiltiy will be approximately twice that of a single voter being pivotal.

    For $N=21$, the numbers are: approximately a $0.176$ probability of being pivotal, and a $0.336$ probability of the election having a margin of 1. Doubling $N$ reduces the probabilities by $\sqrt{2}$, as expected.


    Note that every one of the $N$ voters has the same probability of being pivotal. We could create a "value of a vote" measure with pivotal probabilities as weights, but the $\frac{1}{\sqrt{N}}$ would disappear when we normalize, leaving us with just $V(x) = \frac{1}{N}$.

    ---
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Now, I have some qualms with the idea of pivotality.

    For any reasonably large $N$, only a small fraction of elections will be decided by one vote. Why should we care about this at all?

    The immediate answer is just what I said at the beginning of this section: we don't actually expect this scenario to obtain, but we consider it as characterization of the election system and of the influence of the voters on the candidates.

    As a second answer, note that we just showed that the $P \propto \frac{1}{\sqrt{N}}$ rule describes both the probability of a single voter being pivotal *and* the probability that the election has a margin of $1$. We can actually say more: it turns out that the probability of any small margin $m$ will have this same scaling. We could get an exact expression as a sum of binomials, or an approximation. For the latter we need the variance and standard deviation of our $R = \sum_i^N X_i$ variable:

    $$
    \begin{align}
    \text{Var}[R] &= \sum_i^N \text{Var}[X_i] \\ &= \frac{N}{4}\\
    \text{SD}[R] &= \sqrt{\text{Var}[R] } \\ &= \frac{\sqrt{N}}{2}
    \end{align}
    $$

    Then if we define a new random variable for the margin $M = R - \frac{N}{2}$, it will be approximately normal in the vicinity of $0$ with the same variance:

    $$
    M \sim \mathcal{N}(0, \frac{N}{4})
    $$

    and the probability of the margin being less than some particular $m$ can be found by linearizing the normal CDF $\Phi(z)$ around $0$, where $\Phi(z) \approx \Phi(0) + \Phi'(0) z = \frac{1}{2} + \frac{1}{\sqrt{2\pi}} z$. We standardize $m \to z = m/\sqrt{N/4}$ and calculate:

    $$
    \begin{align}
    P[|M| \le m] &= P\big[|Z| \le m / \sqrt{N/4}\big] \\
      &= \Phi\left(\frac{2m}{\sqrt{N}}\right) - \Phi\left(-\frac{2m}{\sqrt{N}}\right) \\
      &\approx \left(\frac{1}{2} + \frac{1}{\sqrt{2\pi}} \frac{2m}{\sqrt{N}} \right) - \left(\frac{1}{2} - \frac{1}{\sqrt{2\pi}} \frac{2m}{\sqrt{N}} \right) \\
      &= \sqrt{\frac{8}{\pi}} \frac{m}{\sqrt{N}}
    \end{align}
    $$

    So the probability of the election being close at all scales as $\frac{1}{\sqrt{N}}$ as well. (Only under our completely-random model—real elections do not fit this model at all!)

    It feels likely at this point that many "reasonable" definitions of the weight of votes will reproduce the $\frac{1}{\sqrt{N}}$ scaling. Here I wonder if there might be others which are more palatable than either "probability of being pivotal" or "probability of the election being close".


    I still have a reservation along the lines of: what if you have additional information that the election *isn't* close? Logically, does this measure of pivotality just cease to mean anything? How do we handle this? One answer might be that all information you could have is probabilistic, and the probability of a close election never goes to *zero* (considering unforeseeable rare events that might come up before the moment your vote is cast, unreliability of information, etc); there should still be some pivot probability which can be compared, even if it's low. We'll punt on taking this further for now. Here I think of calculating the pivot probability over a different distribution based on historical party shares or something. This would be viable as a metric!
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Pivotality in Two-Tiered Elections
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Let's move on to a two-tier electoral-college system.

    Obviously in a single-tiered system every voter had an *equal* probability of being pivotal.

    If we imagine a two-tiered system where every state gets just one vote, the probability of a voter being pivotal *nationally* looks like:

    $$
    \begin{align}
    P[\text{vote } x \text{ is pivotal nationally}] &= P[\text{vote } x \text{ is pivotal in state } s(x)] \\
    & \quad\quad\times P[\text{state } s(x) \text{ is pivotal nationally}] \\
      &\propto \frac{1}{\sqrt{n_{s(x)}}} \times \frac{1}{\sqrt{N}}
    \end{align}
    $$

    This immediately suggests itself as a "value of a vote": we can measure the relative weights of votes $x, y$ as

    $$
    \frac{V(x)}{V(y)} = \frac{1 / \sqrt{n_{s(x)}}}{1 / \sqrt{n_{s(y)}}}
    $$

    though we still need to figure out how to handle the electoral college. Note, though, that if we normalized these values, the resulting $V(x)$ would *not* admit an interpretation as "probability vote $x$ is pivotal" rather than any other vote: the pivotal scenarios for different voters are *not distinct from each other*; they are probabilities over a different set of events (the election sans that single voter). The value $V(x)$ might be useful, but it cannot simply be interpreted as a probability.

    How to add the elector counts $e_s$ to the picture? The second factor in $\frac{1}{\sqrt{n_{s(x)}}} \times \frac{1}{\sqrt{N}}$ should incorporate this somehow.

    We now need to think about how pivotality should work in a "weighted" elections. The obvious generalization is this: given a uniform distribution on the results of all *states*, what is the probability that the states except for some $i$ result in a total number of "1" votes which falls within $e_i$ of a tie? That is

    $$
    \sum_{s \ne i} e_s X_s \in \frac{E - 1}{2} - \left[0, e_i\right]
    $$

    The problem is that the states all have uneven numbers of electors. The problem of finding the number of outcomes falling in the above interval is an integer partition problem, and the resulting probability is called the [Banzhaf Power Index](https://en.wikipedia.org/wiki/Banzhaf_power_index).

    But let us suppose that the individual states elector counts $e_s$ are small enough, relative to their total $E$, that the result may be approximated with the Central Limit Theorem. Let $Y = \sum_{s \ne i} e_s X_s$, with each $X_s \sim \text{uniform}[\{0, 1\}]$. Each $X_s$ has mean $\mu = 0.5$ and variance $\sigma^2_{X_s} = \frac{1}{4}$. Then:

    $$
    \begin{align}
    \mu_{Y} &= \frac{E - e_i}{2} \\
    \sigma^2_{Y} &= \sum_{s \ne i} {(e_s)}^2 \sigma^2_{X_s} \\
      &= \frac{1}{4} \sum_{s \ne i} {(e_s)}^2 \\
    \end{align}
    $$

    By the Central Limit Theorem, $Y$ is approximately distributed as

    $$
    Y \sim \frac{1}{\sqrt{2\pi \sigma^2_{Y}}} \exp{\left( -\frac{(y - \mu_Y)^2}{2\sigma^2_{Y}}\right)}
    $$

    The probability of the result landing in the range $[\frac{E}{2} - e_i, \frac{E}{2}]$, rounding because we're taking $E$ large anyway, is:

    $$
    P[\text{state } i \text{ is pivotal}] \approx \int_{\frac{E}{2} - e_i}^{\frac{E}{2}} \frac{1}{\sqrt{2\pi \sigma^2_{Y}}} \exp{\left( -\frac{(y - \mu_Y)^2}{2\sigma^2_{Y}}\right)} dy
    $$

    and then we can take a further approximation that the Normal is approximately flat in the vicinity of its mean, meaning that the above is:


    $$
    \begin{align}
    P[\text{state } i \text{ is pivotal}] &\approx \frac{e_i}{\sqrt{2\pi \sigma^2_{Y}}}  \\
      &\approx \frac{e_i}{\sqrt{2\pi \cdot \frac{1}{4} \sum_{s \ne i} {(e_s)}^2}} \\
      &\approx \sqrt{\frac{2}{\pi}} \frac{e_i}{\sqrt{\sum_{s \ne i} {(e_s)}^2}} \\
    \end{align}
    $$

    The overall result for our "probability of a voter being pivotal" is

    $$
    P[x \text{ pivotal}] \propto \frac{1}{\sqrt{n_{s(x)}}} \times \frac{e_{s(x)}}{\sqrt{\sum_{s \ne i} {(e_s)}^2}}
    $$


    This is definitely something we can work with!

    If we write $\Vert \mathbf{e} \Vert = \sqrt{\sum_{s} {(e_s)}^2}$, where $\mathbf{e} = (e_1, \ldots, e_S)$ is the vector of elector counts, we can then express the above as

    $$
    P[x \text{ pivotal}] \propto \frac{1}{\sqrt{n_{s(x)}}} \times \frac{e_{s(x)}}{\sqrt{\Vert \mathbf{e} \Vert^2 - (e_{s(x)})^2}}
    $$

    We could simplify this a little more removing the restriction $s \ne  i$ from the sum; this shouldn't change the relative sizes of the probabilities very much. We then get:

    $$
    P[x \text{ pivotal}] \propto \frac{1}{\sqrt{n_{s(x)}}} \times \frac{e_{s(x)}}{\Vert \mathbf{e} \Vert}
    $$

    To create a value-of-a-vote function, we need to normalize this quantity to sum to $N$ across all voters. Its current sum is:

    $$
    \sum_x \frac{e_s}{ \Vert \mathbf{e} \Vert\sqrt{n_s}}
    = \frac{1}{\Vert \mathbf{e} \Vert} \cdot \sum_s n_s \cdot \frac{e_s}{\sqrt{n_s}}
    = \frac{1}{\Vert \mathbf{e} \Vert} \cdot \sum_s e_s \sqrt{n_s}
    $$

    Renormalizing to $N$, we get a function we'll call the "**Pivotality Value**", or "PV":

    $$
    \begin{align}
    \text{PV}(x) &= N \cdot \frac{ \frac{e_{s(x)}}{ \Vert \mathbf{e} \Vert\sqrt{n_{s(x)}}}}{\frac{1}{\Vert \mathbf{e} \Vert} \cdot \sum_s e_s \sqrt{n_s}} \\
      &= \frac{ N \cdot e_{s(x)} / \sqrt{n_{s(x)}}}{ \sum_s e_s \sqrt{n_s}} \\
      &= \frac{ e_{s(x)} \sqrt{n_{s(x)}} / \sum_s e_s \sqrt{n_s}}{n_s / N} \\
    \end{align}
    $$

    In the last line I've written the expression in a style reminiscent of Apportionment Value $\frac{e_s / E}{n_s / N}$. The only difference is that the $e_s$ terms are replaced by $e_{s} \sqrt{n_{s}}$

    Let us briefly enumerate the approximations that went into this calculation.
    1. We replaced the sum $\sum_{s \ne i} e_s X_s$ by a normal approximation, via the CLT.
    2. Then we approximated the normal as flat to compute the probability in a range $e_s$ below its mean.
    3. Then we dropped the condition $s \ne i$ from the normal's variance.

    When we actually calculate these measures we may prefer not to approximate so much. The 2nd and 3rd  approximations should be easy to undo; the first becomes a complicated integer partition problem and is probably better left as is.

    TODO: consider redoing the derivation with votes $\pm 1$ and mean $0$, for clarity.

    TODO: fit a regression to $e_s$ vs $n_s$ and work out the effective benefit for large districts...

    ----
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Visualizationing PV
    """)
    return


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

    data_with_av['state_population_pct'] = 100 * data_with_av['state_population'] / data_with_av['national_population']
    data_with_av['state_elector_pct'] = 100 * data_with_av['state_electors'] / data_with_av['national_electors']
    data_with_av['apportionment_value'] = data_with_av['state_elector_pct'] / data_with_av['state_population_pct']


    # Calculate Pivotality Value (PV) as defined in line 372-374
    # PV(x) = (N * e_s / sqrt(n_s)) / (sum of e_s * sqrt(n_s) for all s)

    # Group by year to calculate PV for each year separately
    def calculate_pv(group):
        # Calculate the denominator: sum of e_s * sqrt(n_s) for all states
        denominator = (group['state_electors'] * np.sqrt(group['state_population'])).sum()

        # Calculate PV for each state
        group['pivotality_value'] = (
            (group['national_population'] * group['state_electors'] / np.sqrt(group['state_population'])) /
            denominator
        )
        return group

    data_with_pv = data_with_av.groupby('year').apply(calculate_pv).reset_index()
    data_with_pv
    return data_with_av, data_with_pv


@app.cell(hide_code=True)
def _(data):
    year_dropdown = mo.ui.dropdown.from_series(data.year, value=2024, label="Choose a year: ")
    year_dropdown
    return (year_dropdown,)


@app.cell(hide_code=True)
def _(data_with_pv, year_dropdown):
    viz.viz_value_by_state(data_with_pv, "pivotality_value", "Pivotality Value", year_dropdown.value)
    return


@app.cell(hide_code=True)
def _(data_with_pv, year_dropdown):

    viz.viz_value_hist(data_with_pv, "pivotality_value", "Pivotality Value", year_dropdown.value)
    return


@app.cell(hide_code=True)
def _(data_with_av):
    party_dropdown = mo.ui.dropdown.from_series(data_with_av.winning_party, value='democrat', label="Choose a party: ")
    party_dropdown
    return (party_dropdown,)


@app.cell(hide_code=True)
def _(data_with_pv, party_dropdown):
    viz.viz_value_vs_ec_popular_by_year(data_with_pv, "pivotality_value", "Pivotality Value", party_dropdown.value)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    The above looks almost exactly the same as the equivalent plot for AV, but it's not quite the same. (Could add a plot comparing the two)
    """)
    return


@app.cell(hide_code=True)
def _():
    comparison_dropdown = mo.ui.dropdown(options=["Apportionment Value (AV)", "% of National Population", "% of National Electors"], value="Apportionment Value (AV)", label="Choose a column to compare with:")
    comparison_dropdown
    return (comparison_dropdown,)


@app.cell(hide_code=True)
def _(comparison_dropdown, data_with_pv, year_dropdown):
    # Map comparison dropdown value to actual column names and chart titles
    comparison_mapping = {
        "Apportionment Value (AV)": "apportionment_value",
        "% of National Population": "state_population_pct",
        "% of National Electors": "state_elector_pct",
    }

    viz.viz_scatter_compare(
        data_with_pv,
        "pivotality_value", "Pivotality Value",
        comparison_mapping[comparison_dropdown.value], comparison_dropdown.value,
        year_dropdown.value
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Huh, what is that functional form?


    $$
    \begin{align}
    \text{AV}(x) \propto \frac{e_{s(x)}}{n_{s(x)}} && && && \text{PV}(x) \propto \frac{e_{s(x)}}{\sqrt{n_{s(x)}}}
    \end{align}
    $$

    For large $n_s$ we should have $e_{s(x)} \propto n_{s(x)}$ and so $\text{AV}(x) \propto 1$ and $\text{PV}(x) \propto \sqrt{n_{s(x)}}$. The large states form the constant horizontal asymptote.

    For small $n_s$ we have $e_{s(x)} = 3$, so $\text{AV}(x) \propto \frac{1}{n_{s(x)}}$ while $\text{PV}(x) \propto \frac{1}{\sqrt{n_{s(x)}}}$. Hence $\text{AV}(x) \propto (\text{PV}(x))^2$ for small states, which I suppose makes the vertical portion of our graph act like one tail of a parabola.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # **M3**: Pivotality Value Inequality
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Let's write out exact expressions for the MAD, Variance, and Entropy of our Pivotality measures, mainly just to see if the expressions happen to simplify nicely. In each case these expressions apply to election scenario P2 only.


    To simplify the expressions we'll write the denominator as $Z = \sum_{s} e_{s} \sqrt{n_{s}}$. Our PV function is then written $\text{PV}(x) = \frac{ e_{s(x)} \sqrt{n_{s(x)}} / Z}{n_s / N}$

    **M3.1** Mean absolute deviation (MAD):


    $$
    \begin{align}
    \text{PVI}_{\text{MAD}}[\text{P2}] &= \frac{1}{N}\sum_s n_s \vert\text{AV(s)} - 1 \vert \\
      &= \frac{1}{N}\sum_s n_s \left\vert \frac{ e_{s} \sqrt{n_{s}} / Z}{n_s / N} - 1 \right\vert \\
      &= \sum_s \left\vert \frac{e_{s} \sqrt{n_{s}}}{Z} - \frac{n_s}{N} \right\vert \\
    \end{align}
    $$

    We get the average difference between the state's share of the national $e_{s}\sqrt{n_{s}}$ and its share of $n_s$ alone.

    **M3.2** Variance:

    $$
    \begin{align}
    \text{PVI}_{\text{Var}}[\text{P2}]  &= \sum_s \frac{n_s}{N} \left(\text{PV(s)}\right)^2  - 1 \\
      &= \sum_s \frac{n_s}{N} \left(\frac{ e_{s} \sqrt{n_{s}} / Z}{n_s / N} \right)^2  - 1 \\
      &= \frac{N}{Z^2} \sum_s \left( e_{s} \right)^2  - 1
    \end{align}
    $$


    **M3.3** Relative Entropy with respect to a popular election:


    $$
    \begin{align}
    \text{PVI}_{\text{Ent}}[\text{P2}]  = H\left[\frac{\text{PV}(x)}{N} ~\Vert~ \frac{1}{N}\right]
      &= \frac{1}{N}\sum_s n_s \cdot \text{PV}(s) \cdot \log \text{PV}(s) \\
      &= \frac{1}{N}\sum_s n_s \cdot \frac{ e_{s} \sqrt{n_{s}} / Z}{n_s / N} \cdot \log \frac{ e_{s} \sqrt{n_{s}} / Z}{n_s / N} \\
      &= \sum_s \frac{e_{s} \sqrt{n_{s}}}{Z} \cdot \log \frac{ e_{s} \sqrt{n_{s}} / Z}{n_s / N} \\
      &= H\left[\frac{e_{s} \sqrt{n_{s}}}{Z} ~\Vert~ \frac{n_s}{N}\right]
    \end{align}
    $$

    Once again we get that the relative entropy over all $x$ corresponds to a different relative entropy over the states alone.

    Interestingly, these measures would all cancel perfectly if $e_s \propto \sqrt{n_s}$ exactly.
    """)
    return


@app.cell
def _(data_with_pv):
    viz.viz_measure_over_time(data_with_pv, "pivotality_value")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    TODO: which population should we be using? Is it AP or could it plausibly be VEP or VP?

    TODO: think about abstentions and third parties.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
